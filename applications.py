import pygst
pygst.require("0.10")
import gobject
import gst
import pygtk
import gtk
import threading
import os
import requests
import time
import sys

import scootplayer.scootplayer as sp

CACHE_DATA = False

cache = []

class BandwidthLogger(object):

    def __init__(self, log_file, interfaces):
        self.log_file = log_file
        self.interfaces = interfaces
        self.running = True

    def convert_bytes(self, bytes):
        bytes = float(bytes)
        if bytes >= 1099511627776:
            terabytes = bytes / 1099511627776
            size = '%.2f' % terabytes
        elif bytes >= 1073741824:
            gigabytes = bytes / 1073741824
            size = '%.2f' % gigabytes
        elif bytes >= 1048576:
            megabytes = bytes / 1048576
            size = '%.2f' % megabytes
        elif bytes >= 1024:
            kilobytes = bytes / 1024
            size = '%.2f' % kilobytes
        else:
            size = '%.2f' % bytes
        return size

    def convert_bytes_by_name(bytes, size):
        if size == "Terabytes":
            terabytes = bytes / 1099511627776
            return '%.2f' % terabytes
        elif size == "Gigabytes":
            gigabytes = bytes / 1073741824
            return '%.2f' % gigabytes
        elif size == "Megabytes":
            megabytes = bytes / 1048576
            return '%.2f' % megabytes
        elif size == "Kilobytes":
            kilobytes = bytes / 1024
            return '%.2f' % kilobytes
        else:
            return '%.2f' % bytes

    def start(self):
        self.f = open(self.log_file, 'w+')
        threading.Thread(target=self.log_bandwidth).start()

    def log_bandwidth(self):
        i = 0
        while self.running:
            for iface in self.interfaces:
                self.write_stats(self.f, iface, i)
            time.sleep(1)
            i = i + 1
        self.f.close()

    def write_stats(self, f, iface, t):
        rx = 0
        tx = 0

        try:
            rx = "".join(open("".join(['/sys/class/net/',str(iface),'/statistics/rx_bytes'])).readline().split())
            tx = "".join(open("".join(['/sys/class/net/',str(iface),'/statistics/tx_bytes'])).readline().split())
        except Exception as e:
            print "".join(["Stats Err: ", str(e)])
        print ",".join([iface, str(time.time()), str(t), str(rx), str(tx), str(int(tx)+int(rx)), ]) + '\n'
        f.write(",".join([iface, str(time.time()), str(t), str(rx), str(tx), str(int(tx)+int(rx))])  + '\n')

    def stop(self):
        self.running = False


class AudioRTPClass:

    def __init__(self, log_file, interfaces, time):

        self.interfaces = interfaces

        self.rtp_log_file = open("rtp_log", 'w+', 1)
        self.bw_log_file = open(log_file, 'w+', 1)

        stream = """gstrtpbin name=rtpbin  \
                  filesrc location="sintel-1024-surround.mp4" ! decodebin ! faac bitrate=320000 ! rtpmp4apay ! rtpbin.send_rtp_sink_1 \
                  rtpbin.send_rtp_src_1 ! udpsink port=5002 \
                  rtpbin.send_rtcp_src_1 ! udpsink port=5003 sync=false async=false  \
                  udpsrc port=5007 ! rtpbin.recv_rtcp_sink_1 \n"""

        self.streamer = gst.parse_launch (stream)

        self.audiobin = self.streamer.get_by_name("rtpbin")

        if self.audiobin:
            self.audiobin.connect("on-ssrc-active", self.on_ssrc_active)

        self.streamer.set_state(gst.STATE_PLAYING)

        gobject.timeout_add(1000, self.write_stats)

        gobject.timeout_add(time*1000, self.finish)

    def finish(self):
        print "Stop called\n"
        self.streamer.send_event(gst.event_new_eos())

        print "Close log files\n"
        self.bw_log_file.close()
        self.rtp_log_file.close()

        sys.exit()

    def write_stats(self):
        for iface in self.interfaces:
            rx = 0
            tx = 0

            try:
                rx = "".join(open("".join(['/sys/class/net/',str(iface),'/statistics/rx_bytes'])).readline().split())
                tx = "".join(open("".join(['/sys/class/net/',str(iface),'/statistics/tx_bytes'])).readline().split())
            except Exception as e:
                print "".join(["Stats Err: ", str(e)])
            print ",".join([iface, str(time.time()), str(rx), str(tx), str(int(tx)+int(rx))])
            self.bw_log_file.write(",".join([iface, str(time.time()), str(rx), str(tx), str(int(tx)+int(rx))]) + '\n')

        return True

    def on_ssrc_active(self, rtpbin, sessid, ssrc):
        """SSRC Info Received"""
        #self.get_sprop()
        if rtpbin == self.audiobin:
            print "on_ssrc_active: session %d" %  #(sessid, )
            try:
                print ssrc
                session = rtpbin.emit("get-internal-session", sessid)
                if not session:
                    return
                source = session.emit("get-source-by-ssrc", ssrc)
                if not source:
                    return
                stats = source.get_property('stats')
                print stats
                if not stats:
                    return

                print "-------------------------"
                print "ssrc: " + str(stats['ssrc'])
                print "have-rb: " + str(stats['have-rb'])

                if stats['have-rb'] == True:
                    print 'rb-fractionlost: ' + str(stats['rb-fractionlost'])
                    print 'rb-packetslost: ' + str(stats['rb-packetslost'])
                    print 'rb-jitter: ' + str(stats['rb-jitter'])
                    print 'rb-exthighestseq: ' + str(stats['rb-exthighestseq'])
                    print 'rb-lsr: ' + str(stats['rb-lsr'])
                    print 'rb-dlsr: ' + str(stats['rb-dlsr'])
                    print 'rb-round-trip: ' + str(stats['rb-round-trip'])

                    print "plost: " + str(float(stats["rb-fractionlost"])/256.00)

                    self.rtp_log_file.write(','.join([str(stats['rb-fractionlost']),
                        str(stats['rb-packetslost']),
                        str(stats['rb-jitter']),
                        str(stats['rb-round-trip'])]) + '\n')
                    self.rtp_log_file.flush()

            except Exception as exc:
                print exc

def file_transfer(url, file_list, download_path='./', log_file_name="file_transfer.log", cache_data=False):
    try:
        os.stat(download_path)
    except:
        print "Download Path doesn't exist"
        return

    with open(log_file_name, 'w+', 1) as log_file:
        for f in file_list:
            r = requests.get(url + '/%s' % f, stream=True)
            path = download_path + '/%s' % f
            if r.status_code == 200:
                start = time.time()
                with open(path, 'wb') as too:
                    for chunk in r.iter_content(1024):
                        too.write(chunk)
                end = time.time()
                log_file.write(str(end-start) + "," + f)
                print "Downloaded %s" % path
            if cache_data:
                os.system('cp %s /var/www/cache/%s' % (path, f))
                os.system('rm ' + path)
        os.system("rm -rf audio")

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

def create_default_options(mpd):
    options = Bunch(
        manifest = mpd,
        output = 'out/',
        keep_alive = True,
        max_playback_queue = 60,
        max_download_queue = 30,
        debug = True,
        reporting_period = 1,
        csv = True,
        gauged = False,
        playlist = None
    )
    return options

def video_player():
    url = "http://194.80.39.75:8080/ftp/datasets/mmsys12/BigBuckBunny/MPDs/BigBuckBunny_6s_isoffmain_DIS_23009_1_v_2_1c2_2011_08_30.mpd"
    options = create_default_options(url)
    sp.Player(options)

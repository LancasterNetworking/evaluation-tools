import scapy
import scapy.layers.l2
import scapy.layers.inet
from scapy.utils import PcapReader
from scapy.all import *


def print_psuedo_header(p):
    if UDP in p:
        print ''.join(["UDP: (SRC:", p[IP].src,':', str(p[UDP].sport),
                        ' DST:', p[IP].dst ,':', str(p[UDP].dport),')',
                        ' LEN: ', str(p[UDP].len)])
    elif TCP in p:
        print ''.join(["TCP: (", p[IP].src,':', str(p[TCP].sport),
                        ' DST:', p[IP].dst, ':', str(p[TCP].dport),')',
                        ' LEN: ', str(p[TCP].len)])
    else:
        print ''.join(["Proto: (", p.src, ', ', p.dst, ')'])


def psuedo_header(p):
    if any((UDP, TCP)) in p:
        return (p[IP].src, p[IP].dst, p[IP].sport, p[IP].dport)


def parse_tcp_flows(packets):
    flows = {}
    for p in packets:
        if psuedo_header(p) not in flows:
            flows[psuedo_header(p)] = []
        flows[psuedo_header(p)].append(p)
    return flows


def load_udp_packets(location):
    return load_packets(location, filter=lambda x: True if UDP in x else False)


def load_tcp_packets(location):
    return load_packets(location, filter=lambda x: True if TCP in x else False)



def get_time_values(pkts):
    return [x.time for x in pkts]


def load_packets(location, filter=lambda x: x is not None):
    pkts = []
    packets = rdpcap(location)
    for p in packets:
        if filter(p):
            pkts.append(p)
    return pkts


def get_duration(packets):
    start = min(packets, key=attrgetter('time'))
    end = max(packets, key=attrgetter('time'))
    return end


def get_total_size(packets, proto='tcp'):
    return sum(p[IP].len for p in packets)

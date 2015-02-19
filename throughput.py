#TODO
# use pexpect

def get_throughput_files(iface):
    rx = ''.join(['/sys/class/net/',str(iface),'/statistics/rx_bytes'])
    tx = ''.join(['/sys/class/net/',str(iface),'/statistics/tx_bytes'])
    return rx, tx

def get_throughput_stats((rx_file, tx_file)):
    try:
        with open(rx_file, 'r') as rf, open(tx_file, 'r') as tf:
            rx = ''.join(rf.readline().split())
            tx = ''.join(tf.readline().split())
            return (rx, tx)
    except Exception as e:
        print ''.join(['Stats Err: ', str(e)])

    return (0, 0)

def launch_process(cmd, success, failure):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    if p == None:
        return None
    poutput = ''
    try:
        while True:
            o = p.stdout.read(1)
            if o == '' and p.poll() != None:
                return None
            poutput = ''.join([poutput, o])
            if any(connect in poutput for connect in success):
                return p.pid
            elif any(fail in poutput for fail in failure):
                return None
    except:
        return None

def launch_iperf(server_ip, time, bind, threads, wnd=64, wlen=8):
    p = None
    if threads <= 0:
        threads = 1
    cmd = ['iperf', '-c', server_ip, '-t', str(time), '-P', str(threads)]
    if bind is not None:
        cmd += ['-P', str(threads)]
    return launch_process(cmd, ('connected', ), ('refused', 'failed'))

def launch_wget(url, bind):
    p = None
    cmd = ['wget', url]
    if bind is not None:
        cmd += ['--bind-address=', str(bind)]
    return launch_process(cmd, ('connected', ), ('refused', 'failed'))

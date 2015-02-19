
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

def launch_iperf(time, bind, threads, wnd=64, wlen=8):
    p = None
    if threads <= 0:
        threads = 1
    cmd = ['iperf', '-c', SERVER_IP, '-t', str(time), '-P', str(threads)]
    if bind is not None:
        cmd += ['-P', str(threads)]
    return launch_process(cmd, ('connected', ), ('refused', 'failed'))

def launch_wget(bind):
    p = None
    cmd = ['wget', ''.join(['http://', SERVER_IP, '/random.img'])]
    if bind is not None:
        cmd += ['--bind-address=', str(bind)]
    return launch_process(cmd, ('connected', ), ('refused', 'failed'))

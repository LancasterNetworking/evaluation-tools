import glob

def delete_empty_files(pathname):
    [os.remove(f) for f in glob.glob(pathname) if os.stat(f).st_size == 0]

class ssh(object):
    def __init__(self, host, identity_file=None):
        self.host = host
        self.identity_file = identity_file

    def cmd(self, cmd):
        run = ''
        if identity_file is not None:
            run = 'ssh -t -I%s %s "\'%s\'"' % (self.identity_file, self.host, cmd)
        else:
            run = 'ssh -t %s "\'%s\'"' % (self.host, cmd)
        os.system(run)

def clear_net_em(interface, call=lambda x: os.system(x)):
    cmd = "tc qdisc del dev %s root" % (interface, )
    call(cmd)

def add_qdisc(interface, root_handle, call=lambda x: os.system(x)):
    cmd = "tc qdisc add dev %s root handle %d: root htb" % (interface, root_handle)
    call(cmd)
    cmd = "tc class add dev %s parent 1:1 classid 1:11 htb rate 1000Mbps"
    call(cmd)

def add_qdisc_delay(inteface, ip_subnet, idx, net_handle, mean, bounds, call=lambda x: os.system(x)):
    cmd = "tc class add dev %s parent 1:1 classid 1:%d htb rate 1000Mbps" % (interface, idx)
    call(cmd)
    cmd = "tc qdisc add dev %s parent 1:%d handle %d: netem delay %s %s distribution normal" % (interface, idx, net_handle, mean, bounds)
    call(cmd)
    cmd = "tc filter add dev %s protocol ip prio 1 u32 match ip src %s/24 flowid %d:1" % (interface, ip_subnet, net_handle)
    call(cmd)
    cmd = "tc filter add dev %s protocol ip prio 1 u32 match ip dst %s/24 flowid %d:1" % (interface, ip_subnet, net_handle)
    call(cmd)

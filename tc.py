"""
tc example commands
-------------------
#create root
tc qdisc add dev eth0 handle 1: root htb
#create base class
tc class add dev eth0 parent 1: classid 1:1 htb rate 1000Mbps
#create child classes

sudo tc qdisc del dev eth1 root
sudo tc class add dev eth1 parent 1: classid 1:1 htb rate 1000Mbps
sudo tc class add dev eth1 parent 1:1 classid 1:11 htb rate 5Mbps
sudo tc qdisc add dev eth1 parent 1:11 handle 10: netem delay 20ms 5ms distribution normal
sudo tc filter add dev eth1 protocol ip prio 1 u32 match ip dst 10.32.96.0/20 flowid 1:11
sudo tc filter add dev eth1 protocol ip prio 1 u32 match ip src 10.32.96.0/20 flowid 1:11

sudo tc qdisc del dev eth1 root
sudo tc qdisc add dev eth1 root handle 1: cbq avpkt 1000 bandwidth 1gbit
sudo tc class add dev eth1 parent 1: classid 1:1 cbq rate 6114kbit allot 1500 prio 5 bounded isolated
#sudo tc qdisc add dev eth1 parent 1:1 handle 10: netem loss 0.5% delay 20ms 8ms distribution normal
sudo tc filter add dev eth1 parent 1: protocol ip prio 16 u32 match ip dst 10.32.96.0/20 flowid 1:1


sudo tc qdisc del dev eth1 root
sudo tc qdisc add dev eth1 root handle 1: cbq avpkt 1000 bandwidth 1gbit
sudo tc class add dev eth1 parent 1: classid 1:1 cbq rate 8120kbit allot 1500 prio 5 bounded isolated
#sudo tc qdisc add dev eth1 parent 1:1 handle 10: netem delay 30ms 10ms distribution normal
sudo tc filter add dev eth1 parent 1: protocol ip prio 16 u32 match ip dst 10.32.96.0/20 flowid 1:1

tc class add dev eth0 parent 1:1 classid 1:11 htb rate 100Mbps
tc class add dev eth0 parent 1:1 classid 1:12 htb rate 100Mbps
tc class add dev eth0 parent 1:1 classid 1:13 htb rate 100Mbps
#create rules for each class
tc qdisc add dev eth0 parent 1:11 handle 10: netem delay 100ms
tc qdisc add dev eth0 parent 1:12 handle 20: netem loss 20% delay 100ms
tc qdisc add dev eth0 parent 1:13 handle 30: tbf rate 20kbit buffer 1600 limit 3000
#create filters to specify traffic for class
tc filter add dev eth0 protocol ip prio 1 u32 match ip protocol 17 0xff match ip dport 5000 0xffff match ip dst 192.168.1.1 flowid 1:11   ----  IP AND port filter
tc filter add dev eth0 protocol ip prio 1 u32 match ip dst 192.168.1.2 flowid 1:12   --- IP filter
tc filter add dev eth0 protocol ip prio 1 u32 match ip dport 5001 0xffff flowid 1:13   --- Port filter
"""

def clear_net_em(interface, call=lambda x: os.system(x)):
    cmd = "tc qdisc del dev %s root" % (interface, )
    call(cmd)


def add_qdisc(interface, root_handle, call=lambda x: os.system(x)):
    cmd = "tc qdisc add dev %s handle %d: root htb" % (interface, root_handle)
    print cmd
    call(cmd)
    cmd = "tc class add dev %s parent 1: classid 1:1 htb rate 1000Mbps" % (interface, )
    print cmd
    call(cmd)

def add_qdisc_delay(interface, port, idx, net_handle, mbps, mean, bounds, call=lambda x: os.system(x)):
    cmd = "tc class add dev %s parent 1:1 classid 1:%d htb rate %dMbps" % (interface, idx, mbps)
    print cmd
    call(cmd)
    cmd = "tc qdisc add dev %s parent 1:%d handle %d: netem delay %s %s distribution normal" % (interface, idx, net_handle, mean, bounds)
    print cmd
    call(cmd)
    cmd = "tc filter add dev %s protocol ip prio 1 u32 match sport src %d flowid 1:%d" % (interface, port, idx)
    print cmd
    call(cmd)
    cmd = "tc filter add dev %s protocol ip prio 1 u32 match ip src %d flowid 1:%d" % (interface, port, idx)
    print cmd
    call(cmd)

if __name__ == '__main__':
    dev = 'eth0'
    clear_net_em(dev)
    add_qdisc(dev, 1)
    add_qdisc_delay(dev, 11, 101, 6, 0, 0)
    add_qdisc_delay(dev, 11, 101, 2, 0, 0)

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
                        ' LEN: ', str(p[UDP].len)])

def load_pcaps(folder):
    pkts = []
    for pcap in glob.glob('*.pcap'):
        pkts += [p for p in PcapReader(pcap)]

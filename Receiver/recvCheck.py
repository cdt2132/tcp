from struct import *
import datetime
import time

def check(packet, received_check):
    sum = 0
    i = 0
    if len(packet) % 2 != 0:
        packet += 'a'

    while i < len(packet):
        words = ord(packet[i]) + (ord(packet[i + 1]) << 8)
        sum = sum + words
        i += 2

    sum = sum + (sum >> 16)
    sum = ~sum & 0xffff

    if sum == received_check:
        return True
    else:
        return False


def un_pack(packet):
    h = packet[:20]
    data = packet[20:]
    header = unpack('!HHLLBBHHH', h)
    ack_port_num = header[0]
    remote_port = header[1]
    seq_number = header[2]
    tcp_ack_seq = header[3]
    tcp_offset_res = header[4]
    tcp_flags = header[5]
    tcp_window = header[6]
    received_check = header[7]
    tcp_urg_ptr = header[8]

    print "flags", tcp_flags
    header = pack('!HHLLBBHHH', ack_port_num, remote_port, seq_number, tcp_ack_seq, tcp_offset_res, tcp_flags, tcp_window, 0, tcp_urg_ptr)

    new_pack = header + data
    ts = time.time()
    timestamp = str(datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S'))
    if str(tcp_flags) == "1":
        flags = "FIN = 1"
    elif str(tcp_flags) == "16":
        flags = "ACK = 1"
    else :
        flags = "FLAGS = NONE"
    log_f = "%s %s %s %s %s %s\n" %(timestamp, ack_port_num, remote_port, seq_number, tcp_ack_seq, flags)

    return new_pack, received_check, seq_number, tcp_window, len(data), data, log_f, tcp_flags

def checksum(packet):
    sum = 0
    i = 0
    if len(packet) % 2 != 0:
        packet += 'a'

    while i < len(packet):
        words = ord(packet[i]) + (ord(packet[i + 1]) << 8)
        sum = sum + words
        i += 2

    sum = sum + (sum >> 16)
    sum = ~sum & 0xffff

    return sum

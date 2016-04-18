from struct import *
import time
import datetime

def un_pack(packet):
    header = unpack('!HHLLBBHHH', packet)
    remote_port = header[0]
    ack_port_num = header[1]
    seq_number = header[2]
    ack_number = header[3]
    tcp_offset_res = header[4]
    tcp_flags = header[5]
    tcp_window = header[6]
    received_check = header[7]
    tcp_urg_ptr = header[8]

    tcp_ack = pack('!HHLLBBHHH', remote_port, ack_port_num, seq_number, ack_number, tcp_offset_res, tcp_flags,
                  tcp_window, 0, tcp_urg_ptr)

    ts = time.time()
    timestamp = str(datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S'))
    if tcp_flags == 16:
        flags = "ACK = 1"
    elif tcp_flags == 1:
        flags = "FIN = 17"
    elif tcp_flags == 0:
        flags = "FLAGS = NONE"
    else:
        flags = "NONE"
    log_f = "%s %s %s %s %s %s" % (timestamp, remote_port, ack_port_num, seq_number, ack_number, flags)



    return tcp_ack, ack_number, received_check, log_f

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

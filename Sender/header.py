from struct import *
import sys
import socket
import checksum as c

def createPacket(data, remote_IP, remote_port, host, ack_port_num, window_size, seq_number, fin, ack):
    # tcp header fields
    tcp_ack_seq = 0
    tcp_doff = 5  # 4 bit field, size of tcp header, 5 * 4 = 20 bytes
    # tcp flags
    tcp_fin = fin
    tcp_syn = 0
    tcp_rst = 0
    tcp_psh = 0
    tcp_ack = ack
    tcp_urg = 0
    tcp_window = window_size  # maximum allowed window size
    tcp_check = 0
    tcp_urg_ptr = 0

    tcp_offset_res = (tcp_doff << 4) + 0
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)


    # the ! in the pack format string means network order
    header = pack('!HHLLBBHHH', ack_port_num, remote_port, seq_number, tcp_ack_seq, tcp_offset_res, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr)

    if data != 0:
        if len(data)% 2 == 0:
            padding = 0
        else:
            padding =1
    if data != 0:
        packet = header + data;
    else:
        packet = header

    tcp_check = c.checksum(packet)
    # print tcp_checksum

    # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
    tcp_header = pack('!HHLLBBHHH', ack_port_num, remote_port, seq_number, tcp_ack_seq, tcp_offset_res, tcp_flags,
                      tcp_window, tcp_check, tcp_urg_ptr)

    if data != 0:
        packet = tcp_header + data
    else:
        packet = tcp_header
    return packet


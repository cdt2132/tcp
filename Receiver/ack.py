from struct import *
import recvCheck

def createAck(seq_number, rec_bytes, sender_IP, sender_port, host, port, tcp_window):
    # tcp header fields
    tcp_ack_seq = seq_number + rec_bytes + 1
    print tcp_ack_seq
    tcp_doff = 5  # 4 bit field, size of tcp header, 5 * 4 = 20 bytes
    # tcp flags
    tcp_fin = 0
    tcp_syn = 0
    tcp_rst = 0
    tcp_psh = 0
    tcp_ack = 1
    tcp_urg = 0
    tcp_window = tcp_window  # maximum allowed window size
    tcp_check = 0
    tcp_urg_ptr = 0

    tcp_offset_res = (tcp_doff << 4) + 0
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)

    # the ! in the pack format string means network order
    header = pack('!HHLLBBHHH', port, sender_port, 1, tcp_ack_seq, tcp_offset_res, tcp_flags, tcp_window,
              tcp_check, tcp_urg_ptr)

    tcp_check = recvCheck.checksum(header)

    tcp_ack = pack('!HHLLBBHHH', port, sender_port, 1, tcp_ack_seq, tcp_offset_res, tcp_flags,
                      tcp_window, tcp_check, tcp_urg_ptr)

    return tcp_ack


def createFinAck(seq_number, sender_port, port, tcp_window):
    tcp_ack_seq = seq_number + 20 + 1
    tcp_doff = 5  # 4 bit field, size of tcp header, 5 * 4 = 20 bytes
    # tcp flags
    tcp_fin = 0
    tcp_syn = 0
    tcp_rst = 0
    tcp_psh = 0
    tcp_ack = 1
    tcp_urg = 0
    tcp_window = tcp_window  # maximum allowed window size
    tcp_check = 0
    tcp_urg_ptr = 0

    tcp_offset_res = (tcp_doff << 4) + 0
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)

    header = pack('!HHLLBBHHH', port, sender_port, 1, tcp_ack_seq, tcp_offset_res, tcp_flags, tcp_window,
                  tcp_check, tcp_urg_ptr)

    tcp_check = recvCheck.checksum(header)

    tcp_ack = pack('!HHLLBBHHH', port, sender_port, 1, tcp_ack_seq, tcp_offset_res, tcp_flags,
                   tcp_window, tcp_check, tcp_urg_ptr)

    return tcp_ack

def createFin(seq_number, sender_port, port, tcp_window):
    tcp_ack_seq = seq_number + 20 + 1
    tcp_doff = 5  # 4 bit field, size of tcp header, 5 * 4 = 20 bytes
    # tcp flags
    tcp_fin = 1
    tcp_syn = 0
    tcp_rst = 0
    tcp_psh = 0
    tcp_ack = 0
    tcp_urg = 0
    tcp_window = tcp_window  # maximum allowed window size
    tcp_check = 0
    tcp_urg_ptr = 0

    tcp_offset_res = (tcp_doff << 4) + 0
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)

    header = pack('!HHLLBBHHH', port, sender_port, 1, 0, tcp_offset_res, tcp_flags, tcp_window,
                  tcp_check, tcp_urg_ptr)

    tcp_check = recvCheck.checksum(header)

    tcp_ack = pack('!HHLLBBHHH', port, sender_port, 21, tcp_ack_seq, tcp_offset_res, tcp_flags,
                   tcp_window, tcp_check, tcp_urg_ptr)

    return tcp_ack



#Caroline Trimble
#Sender Program
#Sender portion of TCP-like transport layer protocol

import sys
import socket
import os
import recvCheck
import ack
import select
import time

def receive():
    host = ''
    filename = sys.argv[1]
    port = int(sys.argv[2])
    sender_IP = sys.argv[3]
    sender_port = int(sys.argv[4])
    log = sys.argv[5]
    if any(c.isalpha() for c in sender_IP):
        try:
            sender_IP = socket.gethostbyname(sender_IP)
        except:
            "Print invalid domain"
    if "." in str(sender_IP):
        version = 4
    else:
        version = 6
    if log != "stdout":
        log_f = open(log, "w")
    ex_seq = 0

    f = open(filename, 'w')

    try:
        if version == 4:
            try:
                ack_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                print "Ack Socket Created"
            except socket.error:
                print "Unable to create send socket"
            serverAddress = (sender_IP, sender_port)
            try:
                ack_sock.connect(serverAddress)
            except socket.error:
                print "Unable to connect to serverAddress"
        elif version == 6:
            try:
                ack_sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, 0)
                print "Ack socket created (6)"
            except socket.error:
                print "Unable to create socket"
            try:
                addr = (sender_IP, sender_port, 0, 0)
                ack_sock.connect(addr)
            except socket.error:
                print "Unable to connect to serverAddress"
        if version == 4:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except socket.error:
                print "Unable to create socket"
            try:
                sock.bind(('', port))
            except socket.error:
                print "Unable to bind to socket"
        elif version == 6:
            try:
                sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, 0)
            except socket.error:
                print "Unable to create socket"
            try:
                sock.bind(('', port))
            except socket.error:
                print "Unable to bind to socket"


        print "Serving on port %s" %port
        done = False
        while done == False:
            data = sock.recv(1024)
            new_pack, received_check, seq_number, tcp_window, rec_bytes, data, lf, fin = recvCheck.un_pack(data)
            check = recvCheck.check(new_pack, received_check)
            if fin == 1 and check == True:
                done = True
                if log != "stdout":
                    log_f.write(lf)
                else:
                    sys.stdout.write(lf)
            if check == True and seq_number == ex_seq:
                tcp_ack = ack.createAck(seq_number, rec_bytes, sender_IP, sender_port, host, port, tcp_window)
                ack_sock.send(tcp_ack)
                ex_seq = seq_number + rec_bytes
                data = str(data)
                if log != "stdout":
                    log_f.write(lf)
                else:
                    sys.stdout.write(lf)
                f.write(data)
        fin_ack = ack.createFinAck(seq_number, sender_port, port, tcp_window)
        ack_sock.send(fin_ack)
        fin_fin = ack.createFin(seq_number, sender_port, port, tcp_window)
        ack_sock.send(fin_fin)
        ack_sock.setblocking(0)
        ready = select.select([sock], [], [], 30)
        if ready[0]:
            data = sock.recv(64)
            new_pack, received_check, seq_number, tcp_window, ld, data, lf, tcp_flags = recvCheck.un_pack(data)
            if log != "stdout":
                log_f.write(lf)
            else:
                sys.stdout.write(lf)
        f.close()
        if log != "stdout":
            log_f.close()
        os._exit(0)





    except KeyboardInterrupt:
        print  'Shutting Down\n'
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


receive()

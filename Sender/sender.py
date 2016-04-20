#Caroline Trimble
#Sender Program
#Sender portion of TCP-like transport layer protocol

import sys
import socket
import os
import header
import checkAck
import threading
#import statements
global seq_number
global expected_acks
global timeout_window
import time
global last_ack
global est_rtt
global spl_rtt
global dev_rtt
import select
global seg
#global variables
expected_acks = {}


def getSize(fileobject):
    fileobject.seek(0,2)
    size = fileobject.tell()
    return size

def init(remote_IP, remote_port, host, ack_port_num, filename, version):
    try:
        if version == 4:
            try:
                send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                print "Send Socket Created"
            except socket.error:
                print "Unable to create send socket"
            serverAddress = (remote_IP, remote_port)
            try:
                send_sock.connect(serverAddress)
            except socket.error:
                print "Unable to connect to serverAddress"
        elif version == 6:
            host = '::1'
            try:
                send_sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM,0)
                print "Send Socket Created"
            except socket.error:
                print "Unable to create send socket"
            try:
                addr = (remote_IP, remote_port, 0, 0)
                send_sock.connect(addr)
            except socket.error:
                print "Unable to connect to serverAddress"
        if version == 4:
            try:
                ack_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except socket.error:
                print "Unable to create ack socket"
            try:
                ack_sock.bind(('', ack_port_num))
            except socket.error:
                print "Unable to bind to ack socket"
        elif version == 6:
            try:
                ack_sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM,0)
            except socket.error:
                print "Unable to create ack socket"
            try:
                ack_sock.bind(('', ack_port_num))
            except socket.error:
                print "Unable to bind to ack socket"

        try:
            f = open(filename, 'r')
        except:
            err = "File %s Not Found" % filename
            print err

        size = getSize(f)

        return send_sock, ack_sock, f, size
    except KeyboardInterrupt:
        print  'Shutting Down\n'
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


def recv_acks(ack_sock, lf, log_file):
    try:
        global expected_acks
        global seq_number
        global est_rtt
        global dev_rtt
        global last_ack
        global timeout_window
        global seg
        done = False
        while done == False:
            try:
                data = ack_sock.recv(64)
            except socket.error:
                print "Failed to receive ack"
            if data:
                tcp_ack, ack_number, received_check, log_f = checkAck.un_pack(data)
                last_ack = ack_number
                equal = checkAck.check(tcp_ack, received_check)
                done = True
                if equal == True and ack_number in expected_acks:
                    seg = seg + 1
                    cur_time = float(time.time() * 1000)
                    sent_time = expected_acks[ack_number][1]
                    sample_rtt = cur_time - sent_time
                    s_rtt = str(sample_rtt) + "ms\n"
                    log_f = log_f + " " + s_rtt
                    if log_file != "stdout":
                        lf.write(log_f)
                    else:
                        sys.stdout.write(log_f)
                    del expected_acks[ack_number]
                    for k in expected_acks.keys():
                        if k < ack_number:
                            del expected_acks[k]
                    if est_rtt == 0 and dev_rtt == 0:
                        est_rtt = sample_rtt
                        dev_rtt = sample_rtt
                    est_rtt = 0.875 * est_rtt+ 0.125 * sample_rtt
                    diff = sample_rtt - est_rtt
                    dev_rtt = .75 * dev_rtt + .25 * abs(diff)
                    timeout_window = est_rtt + 4 * dev_rtt
        return 0
    except KeyboardInterrupt:
        print 'Shutting Down\n'
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
def sendFin(send_sock, remote_IP, remote_port, host, ack_port_num, window_size):
    global seq_number
    seq_number = seq_number + 20
    p = header.createPacket(0, remote_IP, remote_port, host, ack_port_num, window_size, seq_number, 1, 0)
    send_sock.send(p)

def sendAck(send_sock, remote_IP, remote_port, host, ack_port_num, window_size):
    global seq_number
    seq_number = seq_number + 20
    p = header.createPacket(0, remote_IP, remote_port, host, ack_port_num, window_size, seq_number, 0, 1)
    send_sock.send(p)

def sendPack(send_sock, f, MSS, remote_IP, remote_port, host, ack_port_num, window_size):
    global expected_acks
    global seq_number
    global round_trip
    global last_ack
    global seg
    done = False
    f.seek(seq_number)
    data = f.read(MSS)
    if len(data) == 0:
        done = True
    if done == False:
        packet = header.createPacket(data, remote_IP, remote_port, host, ack_port_num, window_size, seq_number, 0, 0)
        if len(data) < MSS:
            ex_ack = seq_number + len(data) + 1
            seq_number = seq_number + len(data)
        else:
            seq_number = seq_number + MSS
            ex_ack = seq_number + 1
        send_time = float(round(time.time() * 1000))
        expected_acks[ex_ack] = [packet, send_time]
        send_sock.send(packet)
    return 0

def send():
    global expected_acks
    global seq_number
    global est_rtt
    global dev_rtt
    global last_ack
    global seg
    seg = 0
    seq_number = 0
    expected_acks = {}
    MSS = 580
    global timeout_window
    timeout_window = 1000
    est_rtt = 0
    dev_rtt = 0
    last_ack = 0
    re_sent = 0

    try:
        host = ''
        filename = sys.argv[1]
        remote_IP = sys.argv[2]
        remote_port = int(sys.argv[3])
        ack_port_num = int(sys.argv[4])
        log_file = sys.argv[5]
        print remote_IP
        if "." in remote_IP:
            version = 4
        elif ":" in remote_IP:
            version = 6
            host = '::1'
        lf = 0
        if log_file != "stdout":
            lf = open(log_file, "w")
        if len(sys.argv) > 6:
            window_size = float(sys.argv[6])
        else:
            window_size = 1
        send_sock, ack_sock, f, size = init(remote_IP, remote_port, host, ack_port_num, filename, version)
        waitAck = False
        while waitAck == False:
            copy_acks = dict(expected_acks)
            if expected_acks:
                m = min(copy_acks.items(), key=lambda x: x[0])[0]
                send_time = copy_acks[m][1]
                cur_time = float(round(time.time() * 1000))
                if float(cur_time - send_time) > timeout_window:
                    #print m, last_ack
                    try:
                        packet = expected_acks[m][0]
                        send_sock.send(packet)
                        re_sent = re_sent + 1
                        seq_number = int(m) - 1
                        #expected_acks.clear()
                        expected_acks[m] = [packet, cur_time]
                        timeout_window = 2 * timeout_window
                    except KeyError:
                        continue

            if threading.active_count() == 1:
                ack_thread = threading.Thread( target = recv_acks, args = (ack_sock, lf, log_file))
                ack_thread.start()
            if len(expected_acks) < window_size:
                sendPack(send_sock, f, MSS, remote_IP, remote_port, host, ack_port_num, window_size)
            l = size + 1
            if last_ack == l:
                waitAck = True
            if last_ack in expected_acks.keys():
                time.sleep(.001)
                if last_ack in expected_acks.keys():
                    del expected_acks[last_ack]
        sendFin(send_sock, remote_IP, remote_port, host, ack_port_num, window_size)
        f_time = float(time.time() * 1000.0)
        print "Entering FIN_WAIT"
        ack_sock.setblocking(0)
        ready = select.select([ack_sock],[],[], 30)
        if ready[0]:
            data = ack_sock.recv(64)
            tcp_ack, ack_number, received_check, log_f = checkAck.un_pack(data)
            c_time = float(time.time() * 1000.0)
            sample_rtt = c_time - f_time
            s_rtt = str(sample_rtt) + "ms\n"
            log_f = log_f + " " + s_rtt
            if log_file != "stdout":
                lf.write(log_f)
            else:
                sys.stdout.write(log_f)
        print "Entering FIN_WAIT_2"
        f_time = float(time.time() * 1000.0)
        ready = select.select([ack_sock],[],[],30)
        if ready[0]:
            data = ack_sock.recv(64)
            tcp_ack, ack_number, received_check, log_f = checkAck.un_pack(data)
            c_time = float(time.time() * 1000.0)
            sample_rtt = c_time - f_time
            s_rtt = str(sample_rtt) + "ms\n"
            log_f = log_f + " " + s_rtt
            if log_file != "stdout":
                lf.write(log_f)
            else:
                sys.stdout.write(log_f)
            sendAck(send_sock, remote_IP, remote_port, host, ack_port_num, window_size)
        print "Entering TIME_WAIT"
        time.sleep(5)
        print "Delivery completed successfully"
        print "Total bytes sent = %i"%size
        print "Segments sent = %i"%seg
        print re_sent
        rt = float(float(re_sent) / float(seg))
        rt = rt * 100.0
        print "Segments retransmitted = %f %%" %rt
        if lf != 0:
            lf.close()
        send_sock.close()
        ack_sock.close()
        os._exit(0)


    except KeyboardInterrupt:
        print  'Shutting Down\n'
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

send()

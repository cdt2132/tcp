#Caroline Trimble
#Checksum function

def checksum(packet):
    sum = 0
    i = 0
    if len(packet) %2 != 0:
        packet += 'a'

    while i < len(packet):
        words = ord(packet[i]) + (ord(packet[i+1]) << 8)
        sum = sum + words
        i += 2

    sum = sum + (sum >> 16)
    sum = ~sum & 0xffff

    return sum

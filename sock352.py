import socket as syssock
import binascii
import struct
import sys
from collections import namedtuple
import time
from Queue import *
from random import *
import math

#set struct format and size
HEADER_STRUCT = "!BBBBHHLLQQLL"
HEADER_SIZE = struct.calcsize(HEADER_STRUCT)

#set header flags
SYN_VAL = 0x1
FIN_VAL = 0x2
ACK_VAL = 0x4
RESET_VAL = 0x8
OPTION_VAL = 0xA0

#set packet size
packet_size=5000
#number of packets to send before a check to see if the ack is correct
window_size=6
#variable to keep track of how many packets we've sent within the window size
packet_count=0

#new_address=None


#header object for referencing
class packHeader:
    def __init__(self, theHeader=None):
        self.header_struct = struct.Struct(HEADER_STRUCT)

        #constructor for header fields
        if (theHeader is None):
            self.flags = 0
            self.version = 1
            self.opt_ptr = 0
            self.protocol = 0
            self.checksum = 0
            self.sequence_no = 0
            self.source_port = 0
            self.ack_no = 0
            self.dest_port = 0
            self.window = 0
            self.payload_len = 0
        else:
            #unpack header for receive function
            self.unpackHeader(theHeader)

    #Returns a packed header object
    def getPacketHeader(self):
        return self.header_struct.pack(self.version, self.flags, self.opt_ptr, self.protocol, struct.calcsize(HEADER_STRUCT), self.checksum, self.source_port, self.dest_port, self.sequence_no, self.ack_no, self.window, self.payload_len)

    #Returns an unpacked header
    def unpackHeader(self, theHeader):
        if len(theHeader) < 40:
            print ("Invalid Header")
            return -1

        header_array = self.header_struct.unpack(theHeader)
        self.version = header_array[0]
        self.flags = header_array[1]
        self.opt_ptr = header_array[2]
        self.protocol = header_array[3]
        self.header_len = header_array[4]
        self.checksum = header_array[5]
        self.source_port = header_array[6]
        self.dest_port = header_array[7]
        self.sequence_no = header_array[8]
        self.ack_no = header_array[9]
        self.window = header_array[10]
        self.payload_len = header_array[11]
        return header_array 

#packet object
class new_packet:
    def __init__(self, header=None, payload=None):
        #constructor for packet fields, differs from header by adding payload
        if header is None:
            self.header = packHeader()
        else:
            self.header = header
        if payload is None:
            self.payload = None
        else:
            self.payload = payload
            self.header.payload_len = len(self.payload)
        pass
    #Packs the packetheader and payload and combines them into one packet object
    def packPacket(self):
        packed_header = self.header.getPacketHeader()

        if (self.payload is None):
            packed_packet = packed_header
        else:
            packed_packet = packed_header + self.payload

        return packed_packet

    #Creates an ack packet
    def create_ack(self, rHeader):
        self.header.ack_no = rHeader.sequence_no + rHeader.payload_len
        self.header.sequence_no = rHeader.ack_no + 1;
        self.header.flags = ACK_VAL;
    #Creates a SYN packet
    def create_syn(self, seq_num):
        self.header.flags = SYN_VAL
        self.header.sequence_no = seq_num

def init(UDPportTx, UDPportRx):  # initialize your UDP socket here

    #init global socket for sending and receiving
    global global_socket
    global_socket = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
    print "Global socket created"

    if UDPportTx not in range(1, 65535):
        UDPportTx = 27182

    if UDPportRx not in range(1, 65535):
        UDPportRx = 27182

class socket:
    #constructor for socket fields, need these fields to keep track of ack and sequence number and whether there is a socket connection
    def _init_(self):
        self.connected=False
        self.address=None
        self.prev_ack=0
        self.next_ack=0
        self.init_seq=0
        self.next_seq=0

        return
    #n/a for this part of the project
    def bind (self, address):
        print "Binding..."
        global_socket.bind(address)
        return
    #creates a syn packet to be sent to initialize a connection
    def connect (self, address):
        print "In Connect"
        #sets sequence and ack numbers to be referenced in the new syn packet
        self.init_seq=randint(0, 2**64)
        self.ack_no=0
        print "creating SYN Packet"
        #creates a new packet
        syn=new_packet()

        #specifies new packet as a syn packet
        syn.create_syn(self.init_seq)

        #packages the syn packet
        packsyn=syn.packPacket()
        
        #send out the syn packet to setup connection
        while True:

            #sends syn packet through global socket to address provided
            global_socket.sendto(packsyn, address)
            print "Sending SYN to", address
            try:
                #sets timeout of .2 seconds, keep trying to send packet during this timeout

                #print "not getting here"
                global_socket.settimeout(.2)

                #returns packet size in rpacket
                (rpacket, sender)=global_socket.recvfrom(packet_size)
                print "Received ACK Packet"
                break
            #fails if timeout exception
            except syssock.timeout:
                print "Socket timeout..."
                time.sleep(5)
            finally:

                print "Syn Packet sent and ACK SYN packet received successfully"
                #resets timer
                global_socket.settimeout(None)
        #retrieves packet header of 'syn' packet, packet header is the first 40 bytes of the packet as denoted by [:40]
        rec_packet=packHeader(rpacket[:40])
        
        print "Getting ACK SYN packet header"
        #checks flag to verify that it is indeed a SYN flag OR checks ack number to verify it is the sequence number +1 as denoted in class
        if (rec_packet.flags != 5 or rec_packet.ack_no != (syn.header.sequence_no + 1)):
            print "Bad ACK for the SYN we sent"
        else:
            print "Proper ACK for the SYN we sent"
            #proper ACKSYN, connect set to true, seq numbers set to proper values
            self.connected= True
            self.address=address
            self.next_seq = rec_packet.ack_no
            self.prev_ack = rec_packet.ack_no - 1
            print "Connected"
        return

        #n/a for part 1
    def listen (self, backlog):
        print "In listen..."
        pass

    #called by server to accept the SYN packet, sending proper ACK, setting up new socket, and returning new socket for continued communication
    def accept(self):

        while True:

            try:
                #sets timeout for receiving
                global_socket.settimeout(.2)
                (rpacket, sender)=global_socket.recvfrom(packet_size)
                rec_packet=packHeader(rpacket[:40])
                print "Server accepting from...", sender
                if (rec_packet.flags != SYN_VAL):
                    print "Non connection flag"
                else:
                    break
            except syssock.timeout:
                print "Socket timed out"
                time.sleep(5)
                continue
            finally:
                global_socket.settimeout(None)
        print "Server accepted connection"
        #initial sequence number should be random between this range 0-2^64
        self.init_seq=randint(0, 2**64)
        #prev ack should be sequence number -1
        self.prev_ack=rec_packet.sequence_no-1
        #creates new packet of type ACK
        ack=new_packet()
        print "Creating ACK Packet"
        #sets flags of ACK pack, ACKING a SYN packet
        ack.header.flags=ACK_VAL+SYN_VAL
        ack.header.sequence_no=self.init_seq

        #ack number is sequence number +1
        ack.header.ack_no=rec_packet.sequence_no+1
        #packages the ack packet
        packed_ack=ack.packPacket()

        #returns the number of bytes sent
        print "Sending ACK Packet back to client"
        bytes_s=global_socket.sendto(packed_ack, sender)

        #sets new socket
        print "Creating new socket"
        clientsocket=self
        print "New socket created"
        print "Sender is", sender
        #returns new socket with address
        self.address=sender
        return(clientsocket, sender)

    #function to close socket after finalizing communication
    def close(self):  # fill in your code here
        # send a FIN packet (flags with FIN bit set)
        # remove the connection from the list of connections
        #initializes FIN packet
        FIN = new_packet()
        FIN.header.flags = FIN_VAL
        packed_FIN = FIN.packPacket()
        global_socket.sendto(packed_FIN, self.address)
        print "Closing socket"
        self.connected = False
        self.address=None
        self.prev_ack = 0
        self.next_seq = 0
        self.next_ack = 0
        self.init_seq = 0
        return

    #function to continue communication
    def send(self, buffer):
        print "In send function"
        bytessent = 0  # fill in your code here
        #assigns the data in buffer up until the 5000th byte to payload
        payload = buffer[:4098]
        #creates new packet of type payload
        print "Creating payload packet"
        data = new_packet()
        #assigns payload length
        data.header.payload_len = len(payload)
        print "payload length is", data.header.payload_len
        #sets sequence and ack numbers
        print "Setting ACK and SEQ numbers of payload packet"
        data.header.sequence_no = self.next_seq
        print "sequence number", self.next_seq
        
        data.header.ack_no = data.header.sequence_no+1
        print "ack number", data.header.ack_no

        #assigns payload to the payload field of data packet
        data.payload = payload

        #packages the data packet
        print "Packaging payload packet"
        packed_data = data.packPacket()
        #count += count
        print "Sending payload packet"
        while True:
        
            bytesSent = global_socket.sendto(packed_data, self.address)

            try:
                global_socket.settimeout(.2)
                (raw_packet, sender) = global_socket.recvfrom(HEADER_SIZE)
                rec_packet = packHeader(raw_packet)
                print "Packet received..."
                if (rec_packet.flags != ACK_VAL or rec_packet.ack_no != (data.header.sequence_no + 1)):
                    print "Wrong ACK, Going Back N"
                    #go back n protocol implemented here

                break
            except syssock.timeout:
                print "Socket Timed Out.."
                #continue

            finally:
                global_socket.settimeout(None)
        #sets ack and sequence numbers of data packet
        self.next_seq= rec_packet.ack_no 
        self.prev_ack = rec_packet.ack_no - 1
        self.next_ack = rec_packet.ack_no + 1

        return bytesSent - HEADER_SIZE

    #function for server to receive
    def recv(self, nBytes):
        #standard code of timeout and receive from functions
        while True:
            try:
                global_socket.settimeout(.2)
                rPack, sender = global_socket.recvfrom(5000)
                print "received packet"
                rec_packet_header = packHeader(rPack[:40])
                print "getting packet header"

                if (rec_packet_header.flags > 0):
                    print "Not data packet"
                    if (rec_packet_header.flags == FIN_VAL):
                        global_socket.close()
                        break;

                else:
                    break

            except syssock.timeout:
                print "Socket timed out recieving"

            finally:
                print "Its a data packet!"
                global_socket.settimeout(None)
        self.next_seq = rec_packet_header.ack_no
        self.prev_ack= rec_packet_header.ack_no - 1
        self.next_ack = rec_packet_header.ack_no + 1
    
        #payload is now everything after the 40th byte of the received packet
        payload = rPack[40:] #(40+bytessent)?
        ack = new_packet()
        print "creating ACK packet in recv"
        ack.create_ack(rec_packet_header)
        packed_ack = ack.packPacket()
        print "sending ACK packet in recv"
        global_socket.sendto(packed_ack, sender)

        return payload

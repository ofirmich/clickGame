from socket import *
import struct
import msvcrt
import time

# the client chooses group name
val = input("enter your team name: ")
# print(val)
team_name = val

udpServerPort = 13117

# create udp socket to listen to the broadcast
print("Client started, listening for offer requests... ")
UDPclientSocket = socket(AF_INET, SOCK_DGRAM)
UDPclientSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
UDPclientSocket.bind(('', udpServerPort))

# for 10 sec receive the broadcast and ask the server for tcp connection
timer = time.time() +10
while time.time() < timer:
    # recive broadcast from server
    data, serverAddress = UDPclientSocket.recvfrom(28)
    TCPclientSocket = socket(AF_INET, SOCK_STREAM)
    # get and unpack the message and if its suitable to the format close udp socket and open tcp socket
    openMessage = struct.unpack('Ibh', data)
    if openMessage[0] == 0xfeedbeef and openMessage[1] == 0x2:
        tcpServerPort = openMessage[2]
        UDPclientSocket.close()
        print(tcpServerPort)
        TCPclientSocket.connect((serverAddress[0], tcpServerPort))
        TCPclientSocket.send((team_name + '\n').encode())
        # receive message from server - about the game starting
        firstMessage = TCPclientSocket.recv(1024).decode()
        print(firstMessage)
        # for 10 sec send every key press
        timer = time.time() + 10
        while time.time() < timer:
            if msvcrt.kbhit():
                char = msvcrt.getch()
                print(char)
                TCPclientSocket.send(char)
    else:
        continue
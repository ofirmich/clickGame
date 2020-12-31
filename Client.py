from socket import *
import struct
import msvcrt
import time

val = input("enter your team name: ")
print(val)
team_name = val
udpServerPort = 13117

print("Client started, listening for offer requests... ")
UDPclientSocket = socket(AF_INET, SOCK_DGRAM)
UDPclientSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
UDPclientSocket.bind(('', udpServerPort))

timer = time.time() +10
while time.time() < timer:
    # recive message from server
    data, serverAddress = UDPclientSocket.recvfrom(28)
    TCPclientSocket = socket(AF_INET, SOCK_STREAM)
    openMessage = struct.unpack('Ibh', data)
    if openMessage[0] == 0xfeedbeef and openMessage[1] == 0x2:
        tcpServerPort = openMessage[2]
        UDPclientSocket.close()
        TCPclientSocket.connect(("localhost", tcpServerPort))
        TCPclientSocket.send((team_name + '\n').encode())
        firstMessage = TCPclientSocket.recv(1024).decode()
        print(firstMessage)
        timer = time.time() + 10
        while time.time() < timer:
            c = msvcrt.getch()
            print(c)
            TCPclientSocket.send(c)
    else:
        continue
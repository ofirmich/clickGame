from socket import *
import time
import struct
import threading
import random
import scapy.all as scapy

def connectTCP():
    # create tcp socket
    tcpServerPort = 2019
    tcpServerSocket = socket(AF_INET, SOCK_STREAM)
    tcpServerSocket.bind((scapy.get_if_addr(scapy.conf.iface), tcpServerPort))
    tcpServerSocket.settimeout(10)
    tcpServerSocket.listen()

def waiting_for_clients(group1, group2, tcpServerSocket):
    # Sending out broadcast to all clients telling them i'm wainting
    threading.Thread(target=broadcast).start()
    # receive messages for 10 sec on tcp and save for each group its data in suitable db

    timer = time.time() + 10
    while time.time() < timer:
        try:
            connectionSocket, address = tcpServerSocket.accept()
            data = connectionSocket.recv(1024)
            num = random.choice([1, 2])
            # print(data.decode('utf-8'))
            if num == 1:
                group1.append([data.decode('utf-8'), connectionSocket, 0])
            else:
                group2.append([data.decode('utf-8'), connectionSocket, 0])
        except:
            pass


def broadcast():
    # brodcast to all users on UDP
    udp_port = 13117
    tcp_port = 2019

    # create udp socket
    udpServerSocket = socket(AF_INET, SOCK_DGRAM)
    udpServerSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    udpServerSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    udpServerSocket.settimeout(0.2)
    print('Server started, listening on IP address ' + 'localhost'.format())

    # the message to broadcast in udp connection- for 10 sec
    message = struct.pack('Ibh', 0xfeedbeef, 0x2, tcp_port)
    for i in range(10):
        udpServerSocket.sendto(message, ('<broadcast>', udp_port))
        #print("Sent offer message")
        time.sleep(1)
    udpServerSocket.close()


def threadForEachClient(socketPerClient, allMassage):
    # each client will be treated in thread at the same time as the others
    socketPerClient[1].send(bytes(allMassage, 'utf-8'))
    t = time.time() + 10
    while time.time() <= t:
        try:
        # count key pressess of each client
            char = socketPerClient[1].recv(1024)
            if char:
                socketPerClient[2] += 1
        except:
            pass


def main():
    tcpServerPort = 2019
    tcpServerSocket = socket(AF_INET, SOCK_STREAM)
    tcpServerSocket.bind((scapy.get_if_addr(scapy.conf.iface), tcpServerPort))
    tcpServerSocket.settimeout(10)
    tcpServerSocket.listen()
    while True:
        try:
            ### GLOBALS ###
            group1 = []
            group2 = []
            # list of lists - the first cell- the team name, the second cell- the teams tcp socket
            # the last cell - the teams counter - the number of chars sended
            waiting_for_clients(group1, group2, tcpServerSocket)

            while True:       
                # the first message sent on tcp:
                startString = "Welcome to Keyboard Spamming Battle Royale.\n"
                group1String = "Group1:\n==\n"
                group2String = "Group2:\n==\n"
                for i in group1:
                    group1String = group1String+i[0]+"\n"
                for i in group2:
                    group2String = group2String+i[0]+"\n"
                endString = "\nStart pressing keys on your keyboard as fast as you can!!"
                allMassage = startString + group1String + group2String + endString

                # sending the message to each client
                threads = []
                for socketPerClient in group1 + group2:
                    t3 = threading.Thread(target=threadForEachClient, args=(socketPerClient, allMassage))
                    t3.start()
                    threads.append(t3)
                
                for thread in threads:
                    thread.join()

                group1_score = 0
                group2_score = 0

                # adding score to each group
                for socketPerClient in group1:
                    group1_score += socketPerClient[2]

                for socketPerClient in group2:
                    group2_score += socketPerClient[2]

                # print the win message
                print("Game over!\nGroup 1 typed in "+ str(group1_score) +" characters. Group 2 typed in "+str(group2_score)+" characters.\n")
                if group1_score > group2_score:
                    print("Group 1 wins!")
                    print("Congratulations to the winners:\n==")
                    for socketPerClient in group1:
                        print(socketPerClient[0])
                elif group1_score < group2_score:
                    print("Group 2 wins!")
                    print("Congratulations to the winners:\n==")
                    for socketPerClient in group2:
                        print(socketPerClient[0])

                else:
                    print("Its a tie! You are all winners")

                group1 = []
                group2 = []
                break
        
        except (ConnectionError,ConnectionResetError):
            print("Error in connection")
            continue

main()
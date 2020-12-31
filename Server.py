from socket import *
import time
import struct
import threading
import random

### GLOBALS ###
group1 = []
group2 = []
# list of lists - the first cell- the team name, the second cell- the teams tcp socket
# the last cell - the teams counter - the number of chars sended

def connectTCP():
    tcpServerPort = 2019
    tcpServerSocket = socket(AF_INET, SOCK_STREAM)
    tcpServerSocket.bind(("localhost", tcpServerPort))
    tcpServerSocket.settimeout(10)
    tcpServerSocket.listen(10)

    timer = time.time() + 10
    while time.time() < timer:
        try:
            connectionSocket, address = tcpServerSocket.accept()
            data = connectionSocket.recv(1024)
            num = random.choice([1, 2])
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

    udpServerSocket = socket(AF_INET, SOCK_DGRAM)
    udpServerSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    udpServerSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    udpServerSocket.settimeout(0.2)
    print('Server started, listening on IP address ' + 'localhost'.format())

    message = struct.pack('Ibh', 0xfeedbeef, 0x2, tcp_port)
    for i in range(10):
        udpServerSocket.sendto(message, ('<broadcast>', udp_port))
        time.sleep(1)
    udpServerSocket.close()


def threadForEachClient(socketPerClient, allMassage):
    # each client will be treated in thread at the same ti,e as the others
    socketPerClient[1].send(bytes(allMassage, 'utf-8'))
    t = time.time() + 10
    while time.time() <= t:
        socketPerClient[1].recv(1024)
        socketPerClient[2] += 1


def main():
    while True:
        udpServerPort = 13117
        tcpServerPort = 2019

        t1 = threading.Thread(target=broadcast)
        t2 = threading.Thread(target=connectTCP)

        t1.start()  # broadcast announcements
        t2.start()  # accepting clients and assigning groups
        t1.join()
        t2.join()

        startString = "Welcome to Keyboard Spamming Battle Royale.\n"
        group1String = "Group1:\n==\n"
        group2String = "Group2:\n==\n"
        for i in group1:
            group1String = group1String+i[0]+"\n"
        for i in group2:
            group2String = group2String+i[0]+"\n"
        endString = "\nStart pressing keys on your keyboard as fast as you can!!"
        allMassage = startString + group1String + group2String + endString

        for socketPerClient in group1 + group2:
            t3 = threading.Thread(target=threadForEachClient, args=(socketPerClient, allMassage))
            t3.start()
            t3.join()

        group1_score = 0
        group2_score = 0

        for socketPerClient in group1:
            group1_score += socketPerClient[2]

        for socketPerClient in group2:
            group2_score += socketPerClient[2]

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


main()
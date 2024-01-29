import socket
import sys
import threading
import re

rendezvous = ('192.168.56.1', 55555)

msgbox=[]



# connect to rendezvous
print('connecting to rendezvous server')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 50003))
print('sending')
sock.sendto(b'0', rendezvous)
print('sent')

neighbors = []

while True:
    data = sock.recv(1024).decode()
    if data.strip() == 'ready':
        print('checked in with server, waiting')
        break

data = sock.recv(1024).decode()
print(data)
ip1, sport1, dport1, ip2, sport2, dport2 = data.split(' ')
sport1 = int(sport1)
dport1 = int(dport1)
sport2 = int(sport2)
dport2 = int(dport2)

print('\ngot peers')
print('  ip1:          {}'.format(ip1))
print('  source port1: {}'.format(sport1))
print('  dest port1:   {}'.format(dport1))
print('  ip2:          {}'.format(ip2))
print('  source port2: {}'.format(sport2))
print('  dest port2:   {}'.format(dport2))

# connect to neighbors
if ip1 != '':
    print('connecting to neighbor 1: {}:{}'.format(ip1, dport1))
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock1.connect((ip1, dport1))
    neighbors.append(sock1)
if ip2 != '':
    print('connecting to neighbor 2: {}:{}'.format(ip2, dport2))
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock2.connect((ip2, dport2))
    neighbors.append(sock2)

print('ready to exchange messages\n')


# listen for incoming messages
def listen():
    while True:
        data = sock.recv(1024)
        normal_msg = re.sub(r'^c\d+c\d+', '', data.decode())
        if normal_msg in msgbox:
            print('dup found')
        else:
            msgbox.append(normal_msg)
            print('\rneighbor: {}\n> '.format(data.decode()), end='')
        pattern = r"^c\d+c\d+.*$"
        reg_match=re.match(pattern, data.decode())
        if not reg_match:
            for neighbor in neighbors:
                msg='c2'+data.decode()
                neighbor.send(msg.encode())
                print('broadcasted')

listener = threading.Thread(target=listen, daemon=True)
listener.start()

# send messages to neighbors
while True:
    msg = input('> ')
    msg='c2'+msg
    for neighbor in neighbors:
        neighbor.send(msg.encode())
        print('sent')

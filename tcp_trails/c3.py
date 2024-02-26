# client1.py

import socket
import threading
import json

rendezvous = ('172.25.100.53',1234)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.bind(('0.0.0.0', 1239))
print('Sending connection request to server')

#connect to server
client.connect((rendezvous))

neighbor=[]

def get_peers():
    #wait for server to send details of the clients
    data=client.recv(1024).decode()
    data = json.loads(data)
    neighbor.append(data)
    print('got peers',neighbor)


        

def listen():
    #accept connection from the other client
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('0.0.0.0', 12310))
    listener.listen(2)
    print('listening')
    conn, addr = listener.accept()
    print('connected')
    while True:
        data = conn.recv(1024).decode()
        print('peer : ',data)
        if not data:
            break
    conn.close()
    


def sendtopeers(msg):
    #have temporary sending socket
    peerdata=neighbor[0]['peerdata']
    for peer in peerdata:
        temp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(peer)
        ip=peer['ip']
        port=peer['port']+1
        temp.connect((ip,port))
        temp.send(msg.encode())
        print('sent')
        # temp.close()


print('Connected to server')
#wait for server to send details of the clients
data=client.recv(1024).decode()
if data.strip() == 'ready':
    print('checked in with server, waiting')
    get_peers()
    try:
        listener = threading.Thread(target=listen, args=(), daemon=True)
        listener.start()
    except:
        print('error')
    

while True:
    #connect to the other client
    msg=input('c3: $ ')
    sendtopeers(msg)
    print('sent')




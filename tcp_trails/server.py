# bootstrap_server.py

import socket
import threading
import json


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 4443))
print('Server listening on port 4443')

clients = []
clients_address = []

server.listen(4)


def handlesending(details,client):
    #send details of the clients to the clients
    # print(clients)
    data={
        "peerdata": [{
            'ip':details[0][0],
            'port':details[0][1]
        },
        {
            'ip':details[1][0],
            'port':details[1][1]
        }]
    }
    data = json.dumps(data)
    client.send(data.encode())
    print('sent')
    client.close()
    print('closed')

while True:
    if len(clients)<4:
        #get clients data and append to clients list
        client, address = server.accept()
        clients.append(client)
        clients_address.append(address)
        print(f"Connection from {address} has been established.")
        # print(clients)
        client.send((b'ready'))
    
    if len(clients)==4:
        #send details of the clients to the clients
        print('sending')
        handlesending(details=[clients_address[0],clients_address[3]],client=clients[1])
        handlesending(details=[clients_address[1],clients_address[2]],client=clients[0])
        handlesending(details=[clients_address[1],clients_address[2]],client=clients[3])
        handlesending(details=[clients_address[0],clients_address[3]],client=clients[2])
        print('sent')
        break
        


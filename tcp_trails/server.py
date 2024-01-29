# bootstrap_server.py

import socket
import threading
import json

def handle_client(client_socket, client_address, clients):
    with clients_lock:
        clients.append((client_socket, client_address))

        if len(clients) == 2:
            # Send client details to each other
            print('Sending client details to each other')
            # Send serialized address
            clients[0][0].send(json.dumps(clients[1][1]).encode())
            clients[1][0].send(json.dumps(clients[0][1]).encode())
            print('Clients can now communicate directly')

def bootstrap_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8888))
    server.listen(2)
    print('Server listening on port 8888')

    clients = []
    global clients_lock
    clients_lock = threading.Lock()

    while True:
        client_socket, client_address = server.accept()
        print('Received connection from {}'.format(client_address))
        client_handler = threading.Thread(
            target=handle_client,
            args=(client_socket, client_address, clients)
        )
        client_handler.start()

bootstrap_server()

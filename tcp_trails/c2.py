# client2.py

import socket
import threading
import json

def listen_for_connections(client_socket):
    while True:
        try:
            data = client_socket.recv(1024).decode()
            print(f"Received data from client 1: {data}")
            # Add your processing logic here
        except ConnectionResetError:
            print("Connection with client 1 closed.")
            break

def client2():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 8888))

    # Receive details of the other client
    data=client.recv(1024).decode()
    other_client_address = json.loads(data)
    print(other_client_address)
    other_client_address=tuple(other_client_address)

    # Start a thread to listen for connections from the other client
    listening_thread = threading.Thread(target=listen_for_connections, args=(other_client,))
    listening_thread.start()

    # Connect to the other client
    other_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    other_client.connect(other_client_address)



    while True:
        # Add your client2 main logic here
        msg=input('>')
        #send to other client   
        other_client.send(msg.encode())
        pass

client2()

import socket
import signal


def signal_handler(sig, frame):
    raise KeyboardInterrupt

known_port = 50001

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 55555))
normal_node_weight=5
authority_node_weight=61
threshold=60
sock.listen(4)

while True:
    signal.signal(signal.SIGINT, signal_handler)
    print('waiting for connections')
    clients = []
    
    while len(clients) < 4:
        conn,address=sock.accept()
        print('connection from: {}'.format(address))
        clients.append((conn,address))
        conn.sendall(b'ready')
    

    c1 = clients[0]
    c2 = clients[1]
    c3 = clients[2]
    c4 = clients[3]
    print(clients )
    c1_addr, c1_port = clients[0]
    c2_addr, c2_port = clients[1]
    c3_addr, c3_port = clients[2]
    c4_addr, c4_port = clients[3]

    print(c1_addr, c1_port, known_port)
    print(c2_addr, c2_port, known_port)
    print(c3_addr, c3_port, known_port)
    print(c4_addr, c4_port, known_port)

    # send messages to neighbors
    c1[0].sendall('{} {} {} {} {} {} {} {}'.format(c3_addr, c2_port, c3_port,c1_addr, c2_port, c1_port,normal_node_weight,threshold).encode(), c2)
    c2[0].sendall('{} {} {} {} {} {} {} {}'.format(c4_addr, c3_port, c4_port,c2_addr, c3_port, c2_port,normal_node_weight,threshold).encode(), c3)
    c3[0].sendall('{} {} {} {} {} {} {} {}'.format(c2_addr, c1_port, c2_port,c4_addr, c1_port, c4_port,normal_node_weight,threshold).encode(), c1)
    c4[0].sendall('{} {} {} {} {} {} {} {}'.format(c1_addr, c4_port, c3_port,c3_addr, c4_port, c1_port,authority_node_weight,threshold).encode(), c4)

    msg=input(">")
    if msg=="exit":
        break
    if msg=="restart":
        clients=[]
        continue

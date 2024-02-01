import socket

known_port = 50001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 55555))

normal_node_weight = 5
authority_weight=61
threshold=60


while True:
    try:
        clients = []

        while len(clients) < 4:
            data, address = sock.recvfrom(128)

            print('connection from: {}'.format(address))
            clients.append(address)

            sock.sendto(b'ready', address)

        c1 = clients[0]
        c2 = clients[1]
        c3 = clients[2]
        c4 = clients[3]

        c1_addr, c1_port = clients[0]
        c2_addr, c2_port = clients[1]
        c3_addr, c3_port = clients[2]
        c4_addr, c4_port = clients[3]

        print(c1_addr, c1_port, known_port)
        print(c2_addr, c2_port, known_port)
        print(c3_addr, c3_port, known_port)
        print(c4_addr, c4_port, known_port)

        # send messages to neighbors
        sock.sendto('{} {} {} {} {} {} {} {}'.format(c2_addr, c1_port, c2_port,c4_addr, c1_port, c4_port,normal_node_weight,threshold).encode(), c1)
        sock.sendto('{} {} {} {} {} {} {} {}'.format(c3_addr, c2_port, c3_port,c1_addr, c2_port, c1_port,normal_node_weight,threshold).encode(), c2)
        sock.sendto('{} {} {} {} {} {} {} {}'.format(c4_addr, c3_port, c4_port,c2_addr, c3_port, c2_port,normal_node_weight,threshold).encode(), c3)
        sock.sendto('{} {} {} {} {} {} {} {}'.format(c1_addr, c4_port, c3_port,c3_addr, c4_port, c1_port,authority_weight,threshold).encode(), c4)
    except KeyboardInterrupt:
        break
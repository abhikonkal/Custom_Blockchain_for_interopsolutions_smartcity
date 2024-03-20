# client1.py

import socket
import threading
import json
import time


#code for digital signature 

import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding
import cryptography

def rsa_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    return (private_key, private_key.public_key())

def sign(message, private_key):
    padding_instance = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
    return base64.b64encode(private_key.sign(message, padding_instance, hashes.SHA256()))

def verify(message, signature, public_key):
    sig = base64.b64decode(signature)
    padding_instance = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
    try:
        public_key.verify(sig, message, padding_instance, hashes.SHA256())
        return True
    except cryptography.exceptions.InvalidSignature:
        return False


def deserialize_public_key(pub_key_string):
    pub_key_bytes = pub_key_string.encode('utf-8')
    pub_key = serialization.load_pem_public_key(pub_key_bytes, backend=default_backend())
    return pub_key

#digital signature code ends 



rendezvous = ('172.25.100.53',4443)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.bind(('0.0.0.0', 6000))
print('Sending connection request to server')

#connect to server
client.connect((rendezvous))

neighbor=[]
conn_peers = []
msgbox = []



def get_peers():
    #wait for server to send details of the clients
    data=client.recv(1024).decode()
    data = json.loads(data)
    neighbor.append(data)
    print('got peers',neighbor)


        

def listen():
    #accept connection from the other client
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('0.0.0.0', 6001))
    listener.listen(2)
    print('listening')
    conn, addr = listener.accept()
    print(conn,addr)
    print('connected')
    while True:
        rawdata = conn.recv(1024).decode()
        data = json.loads(rawdata)
        if not data:
            break
        msg_to_append = data['raw_message']
        sender_pub_key = deserialize_public_key(data['publickey'])
        signature = data['sign']
        msg_timestamp = data['timestamp']
        my_timestamp = time.time()
        if my_timestamp - msg_timestamp > 60:
            print('message too old')
            continue
        if verify(msg_to_append.encode(), signature.encode(), sender_pub_key):
            print('verified')
            print('peer : '+data['sender'],msg_to_append)
            if msg_to_append not in msgbox:
                msgbox.append(msg_to_append)
                print('peer : ',data)
                sendtopeers(rawdata)
            else:
                print('message already received')
        else:
            print('Message Verification Failed!!.Message is Tampered')

    conn.close()
    
    



def sendtopeers(msg):
    for peer in conn_peers:
        peer.send(msg.encode())
    print('sent to peers')


def makeconnections(neighbors):
    #connect to the other clients
    peerdata = neighbors[0]['peerdata']
    for neighbor in peerdata:
        temp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp.connect((neighbor['ip'],neighbor['port']+1))
        conn_peers.append(temp)
        print('connected to ',neighbor)
    print(conn_peers)



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
    makeconnections(neighbor)
    


#public private key pair
my_private_key, my_public_key = rsa_keypair()
pub_key_bytes = my_public_key.public_bytes(Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
pub_key_string = pub_key_bytes.decode('utf-8')

self_stake_val = 20
while True:
    #connect to the other client
    msg=input('c1: $ ')
    msgbox.append(msg)
    msg = msg.encode()
    signature = sign(msg, my_private_key)
    msg = msg.decode()
    signature = signature.decode()
    datajson={
        'sender':'c1',
        'receiver':'',
        'sek_bit':'0',
        'hash_value':'0',
        'timestamp':time.time(),
        'eb_bit':'0',
        'acc_stack_val':self_stake_val,
        'node_id':'c1',
        'raw_message':msg,
        'sign':signature,
        'publickey':pub_key_string
    }
    datajson=json.dumps(datajson)
    sendtopeers(datajson)
    print('sent')




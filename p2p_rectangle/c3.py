import socket
import sys
import threading
import re
import time
import json

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

msgbox=[]

rendezvous = ('172.25.100.53', 55555)

# connect to rendezvous
print('connecting to rendezvous server')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 50004))
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
ip1, sport1, dport1, ip2, sport2, dport2 ,self_stake_val,threshold= data.split(' ')
sport1 = int(sport1)
dport1 = int(dport1)
sport2 = int(sport2)
dport2 = int(dport2)
self_stake_val=int(self_stake_val)
threshold=int(threshold)

print('\ngot peers')
print('  ip1:          {}'.format(ip1))
print('  source port1: {}'.format(sport1))
print('  dest port1:   {}'.format(dport1))
print('  ip2:          {}'.format(ip2))
print('  source port2: {}'.format(sport2))
print('  dest port2:   {}'.format(dport2))
print('  self stake value:   {}'.format(self_stake_val))
print('  threshold:   {}'.format(threshold))


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

#creating pvt,pub pairs 
pvt3, pub3 = rsa_keypair()


# listen for incoming messages
def listen():
    while True:
        datajson = sock.recv(1024)
        datajson = datajson.decode()
        fetched_data=json.loads(datajson)
        fetch_msg=fetched_data['raw_message']
        topass_key=fetched_data['publickey']
        sign=fetched_data['sign']
        normal_msg = re.sub(r'^c\d+c\d+', '', fetch_msg)
        data=normal_msg
        ver_msg=fetch_msg.encode()
        ver_sign=sign.encode()
        ver_pub=deserialize_public_key(topass_key)
        if(verify(ver_msg,ver_sign,ver_pub)):
            if normal_msg in msgbox:
                print('dup found')
            else:
                msgbox.append(normal_msg)
                print('\rneighbor: {}\n> '.format(data), end='')
                pattern = r"^c\d+c\d+.*$"
                reg_match=re.match(pattern, fetch_msg)
                if not reg_match:
                    for neighbor in neighbors:
                        msg=data
                        datajson={
                            'raw_message':msg,
                            'sign':sign,
                            'publickey':topass_key
                        }
                        datajson=json.dumps(datajson)
                        neighbor.send(datajson.encode())
                        # print(datajson)
                        print('broadcasted')
        else:
            print('Message Verification Failed!!.Message is Tampered')
        
        
        
    
listener = threading.Thread(target=listen, daemon=True)
listener.start()

# send messages to neighbors
pub_key_bytes = pub3.public_bytes(Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
# Convert bytes to string (optional)
pub_key_string = pub_key_bytes.decode('utf-8')
while True:
    msg = input('> ')
    msg = 'c3'+msg
    msgbox.append(msg)
    msg=msg.encode()
    signmsg = sign(msg, pvt3)
    msg=msg.decode()
    datajson={
        'sender':'c1',
        'receiver':'c2',
        'sek_bit':'0',
        'hash_value':'0',
        'timestamp':time.time(),
        'eb_bit':'0',
        'acc_stack_val':self_stake_val,
        'node_id':'c1',
        'raw_message':msg,
        'sign':signmsg,
        'publickey':pub_key_string
    }
    datajson=json.dumps(datajson)
    for neighbor in neighbors:
        neighbor.send(datajson.encode())
        print('sent')


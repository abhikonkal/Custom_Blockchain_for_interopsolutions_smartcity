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

rendezvous = ('172.25.100.53', 55555)

msgbox=[]


# connect to rendezvous
print('connecting to rendezvous server')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 50004))
print('sending')
sock.connect(rendezvous)
sock.sendall(b'0')
print('sent')

neighbors = []

while True:
    data = sock.recv(4096).decode()
    if data.strip() == 'ready':
        print('checked in with server, waiting')
        break

data = sock.recv(4096).decode()
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
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect((ip1, dport1))
    neighbors.append(sock1)
if ip2 != '':
    print('connecting to neighbor 2: {}:{}'.format(ip2, dport2))
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect((ip2, dport2))
    neighbors.append(sock2)

print('ready to exchange messages\n')

#creating pvt,pub pairs 
pvt3, pub3 = rsa_keypair()


# listen for incoming messages


def broadcastemessage(msg):
    for neighbor in neighbors:
        print('broadcasting')
        neighbor.sendall(msg.encode())
        print('sent')


def listen():
    while True:
        datajson = sock.recv(4096)
        datajson = datajson.decode()
        fetched_data=json.loads(datajson)
        sender_pub_key=fetched_data['publickey']
        sender_pub_key=deserialize_public_key(sender_pub_key)
        tx_sign=fetched_data['sign'][0].encode()
        tx_msg=fetched_data['raw_message'].encode()
        normal_msg = re.sub(r'^c\d+c\d+', '', fetched_data['raw_message'])
        tx_timestamp=fetched_data['timestamp']
        tx_stake_val=fetched_data['acc_stake_val']
        og_timestamp=time.time()

        if og_timestamp-tx_timestamp>60:
            print('Redirecting to Authority Node for Verification')


        #local consensus mechanism 
        if fetched_data['protocol']=='p1':
            #excuting local stake consensus mechanism
            #addding your stake and send back to sender
            new_stake_val=self_stake_val+tx_stake_val
            fetched_data['acc_stake_val']=new_stake_val
            #add your signature and send back to sender
            my_sign=sign(tx_msg,pvt3)
            fetched_data['sign'].append(my_sign.decode())
            datajson=json.dumps(fetched_data)
            sender_ip=fetched_data['sender']['ip']
            sender_port=int(fetched_data['sender']['port'])
            tempsock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tempsock.connect((sender_ip,sender_port))
            tempsock.send(datajson.encode())
            print('sent')



        #add your stake and checek thershold 
        #if less than threshold then broadcast else add to ledger
        #if added to ledger then broadcast to neighbors
        # if verify(tx_msg,tx_sign,sender_pub_key):
        #     print('Message Verified')
        #     if normal_msg in msgbox:
        #         print('dup found')
        #         break
        #     new_stake_val=self_stake_val+tx_stake_val
        #     if new_stake_val>threshold:
        #         #alter stake val in datajson and broad cast
        #         fetched_data['acc_stake_val']=new_stake_val
        #         datajson=json.dumps(fetched_data)
        #         broadcastemessage(datajson)
        #     else:
        #         #add to ledger and broadcast
        #         msgbox.append(datajson)
        #         broadcastemessage(datajson)
        # else:
        #     print('Message Verification Failed!!.Message is Tampered')
        



                
                

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
        'sender':{
            #my ip and port
            'ip':'172.25.100.53',
            'port':'50004'
        },
        'receiver':'c2',
        'sek_bit':'0',
        'hash_value':'0',
        'timestamp':time.time(),
        'eb_bit':'0',
        'acc_stake_val':self_stake_val,
        'node_id':'c1',
        'raw_message':msg,
        'verification_list':[0],
        'sign':[signmsg],
        'publickey':pub_key_string,
        'protocol':'p1'
    }
    datajson=json.dumps(datajson)
    for neighbor in neighbors:
        neighbor.send(datajson.encode())
        print('sent')
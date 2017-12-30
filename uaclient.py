#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa cliente que abre un socket a un servidor."""

import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaserver import ConfigHandler
from uaserver import log_maker

if len(sys.argv) == 4:
        CONFIG = sys.argv[1]
        print(CONFIG)
        parser = make_parser()
        cHandler = ConfigHandler()
        parser.setContentHandler(cHandler)
        parser.parse(open(CONFIG))
        config = cHandler.get_config()
        print(config)
else:
    sys.exit('Usage: uaclient.py config method option')

print(config[6])
print(config[5])
Metodo = sys.argv[2]
Methods = ['register','invite', 'bye']

if Metodo not in Methods:
    sys.exit('Los metodos utilizados son: invite o register')
else:
    if Metodo == "register":
        Usuario = config[0]
        PORT = config[5]
        Expired = sys.argv[3]
        USER_M = Metodo.upper() + ' sip:' + Usuario
        Data = USER_M + ' ' + 'SIP/2.0\r\n'+ 'Expires: ' + Expired + '\r\n\r\n'

    elif Metodo == "invite":
        Destination = sys.argv[3]
        USER_M = Metodo.upper() + ' sip:' + Destination + ' SIP/2.0\r\n'
        USER_M += 'Content-Type: application/sdp\r\n\r\n'
        Cuerpo = 'v=0\r\n' + 'o=' + config[0] + ' ' + config[2] + '\r\n'
        Cuerpo += 's=misesion\r\n' + 't=0\r\n'
        Cuerpo += 'm=audio ' + config[3] + ' RTP\r\n'
        Data = USER_M + Cuerpo
    print(Data) #ATENCION TRAZA A QUITAR....


"""
        # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect(('127.0.0.1', PORT))
        Data = USER_M + ' ' + 'SIP/2.0\r\n\r\n'


        print("Enviando:", USER_M)
        my_socket.send(bytes(Data, 'utf-8'))

    Usuario = sys.argv[2].split(':')
    PORT = int(Usuario[1])
    USER = Usuario[0]
    SERVER = USER.split('@')[1]
    Methods = ['register','invite', 'bye']
    USER_M = ''
    if sys.argv[1] in Methods:
        USER_M = sys.argv[1].upper() + ' sip:' + USER
    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((SERVER, PORT))
        Data = USER_M + ' ' + 'SIP/2.0\r\n\r\n'


        print("Enviando:", USER_M)
        my_socket.send(bytes(Data, 'utf-8'))
        data = my_socket.recv(1024)
        print('Recibido -- ', data.decode('utf-8'))
        respuesta = data.decode('utf-8').split('\r\n\r\n')[0:-1]
        "" If register --> TACATA

        if sys.argv[1] == 'invite' and respuesta == ['SIP/2.0 100 Trying',
                                                     'SIP/2.0 180 Ringing',
                                                     'SIP/2.0 200 OK']:
            USER_M = 'ACK' + ' sip:' + USER
            Data = USER_M + ' ' + 'SIP/2.0\r\n\r\n'
            print("Enviando:", USER_M)
            my_socket.send(bytes(Data, 'utf-8'))
    print("Socket terminado.")
else:
    sys.exit('Usage: client.py method receiver@ip:SIPport')

    """

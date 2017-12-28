#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa cliente que abre un socket a un servidor."""

import socket
import sys

if len(sys.argv) == 3:
    Usuario = sys.argv[2].split(':')
    PORT = int(Usuario[1])
    USER = Usuario[0]
    SERVER = USER.split('@')[1]
    Methods = ['invite', 'bye']
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

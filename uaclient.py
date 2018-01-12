#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa cliente que abre un socket a un servidor."""

import socket
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaserver import ConfigHandler
from uaserver import log_maker
import hashlib


def checking_nonce(nonce):
    """devuelve numero encriptado."""
    function_check = hashlib.md5()
    function_check.update(bytes(str(nonce), "utf-8"))
    print('EL Nonce : "' + str(nonce) + '"')
    print(config[1])
    function_check.update(bytes(config[1], "utf-8"))
    print('LA CONTRASEÑA ES : "' + config[1] + '"')
    function_check.digest()
    print('RESPONSE PROXY: ' + function_check.hexdigest())
    return function_check.hexdigest()


if len(sys.argv) == 4:
        CONFIG = sys.argv[1]
        parser = make_parser()
        cHandler = ConfigHandler()
        parser.setContentHandler(cHandler)
        parser.parse(open(CONFIG))
        config = cHandler.get_config()
else:
    sys.exit('Usage: uaclient.py config method option')

Metodo = sys.argv[2]
Methods = ['register', 'invite', 'bye']

if Metodo not in Methods:
    conf = []
    log_maker(config[7], "error", "metodos erroneos",conf)
    sys.exit('Los metodos utilizados son: invite,register,bye')
else:

    Usuario = config[0]
    PORT = config[6]
    RTP_PORT = config[4]
    IP_Client = config[2]
    PORT_UA2 = config[3]
    Audio_path = config[8]

    if Metodo == "register":
        Expired = sys.argv[3]
        USER_M = Metodo.upper() + ' sip:' + Usuario + ':' + PORT_UA2
        Data = USER_M + ' ' + 'SIP/2.0\r\n' + 'Expires: '
        Data += Expired + '\r\n\r\n'

    elif Metodo == "invite":
        Destination = sys.argv[3]
        USER_M = Metodo.upper() + ' sip:' + Destination + ' SIP/2.0\r\n'
        USER_M += 'Content-Type: application/sdp\r\n\r\n'
        Cuerpo = 'v=0\r\n' + 'o=' + config[0] + ' ' + config[2] + '\r\n'
        Cuerpo += 's=misesion\r\n' + 't=0\r\n'
        Cuerpo += 'm=audio ' + config[4] + ' RTP\r\n\r\n'
        Data = USER_M + Cuerpo

    elif Metodo == 'bye':
        Destination = sys.argv[3]
        USER_M = Metodo.upper() + ' sip:' + Destination
        Data = USER_M + ' SIP/2.0\r\n\r\n'

    IP_Proxy = config[5]
    PORT_Proxy = int(config[6])

    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((IP_Proxy, PORT_Proxy))
            print("Enviando:", USER_M)
            conf = [IP_Proxy, PORT_Proxy]
            my_socket.send(bytes(Data, 'utf-8'))
            log_maker(config[7], "envia", Data, conf)
            data = my_socket.recv(1024)
            respuesta = data.decode('utf-8').split('\r\n\r\n')[0:3]
            response = respuesta[0]
            if Metodo == 'invite' and respuesta == ['SIP/2.0 100 Trying',
                                                    'SIP/2.0 180 Ringing',
                                                    'SIP/2.0 200 OK']:
                conf = [IP_Proxy, PORT_Proxy]
                log_maker(config[7], "recibe", data.decode('utf-8'), conf)
                Destination = sys.argv[3]
                RTP_PORT_S = data.decode('utf-8').split(' ')[9]
                USER_M = 'ACK' + ' sip:' + Destination
                Data = USER_M + ' ' + 'SIP/2.0\r\n\r\n'
                print("Enviando:", USER_M)
                log_maker(config[7], "envia", Data, conf)
                my_socket.send(bytes(Data, 'utf-8'))
                print("Socket terminado.")
                print('config ', config)
                toRun = ('./mp32rtp -i ' + IP_Client + ' -p ')
                toRun += (RTP_PORT_S + ' < ' + Audio_path)
                print("Vamos a ejecutar", toRun)
                log_maker(config[7], "ejecuta", toRun, conf)
                os.system(toRun)
                print(" *=====================*\n",
                      " |The file is sended...|\n",
                      "*=====================*\n")
            elif response == 'SIP/2.0 200 OK':
                log_maker(config[7], "recibe", response, conf)
            elif Metodo == 'register':
                conf = [IP_Proxy, PORT_Proxy]
                respons = response.split('\r\n')[0]
                if respons == 'SIP/2.0 401 Unauthorized':
                    log_maker(config[7], "error", response, conf)
                    nonce_large = respuesta[0].split(' ')[4]
                    nonce = nonce_large.split('=')[1]
                    non_ce = checking_nonce(nonce)
                    USER_M = Metodo.upper() + ' sip:'
                    USER_M += Usuario + ':' + PORT_UA2
                    Data = USER_M + ' ' + 'SIP/2.0\r\n' + 'Expires: '
                    Data += Expired + '\r\n'
                    Data += 'Authenticate: ' + non_ce + '\r\n\r\n'
                    print("EnviandoR:", USER_M)
                    log_maker(config[7], "envia", Data, conf)
                    my_socket.send(bytes(Data, 'utf-8'))
                    print("Socket terminado.")
                elif respons == 'SIP/2.0 404 User Not Found':
                    log_maker(config[7], "error", response, conf)
                    print("No es posible conectarse")
                elif respons == 'SIP/2.0 400 Bad Request':
                    print("Esta mal formado la peticion")
                    log_maker(config[7], "error", response, conf)
    except ConnectionRefusedError:
        conf = []
        log_maker(config[7], "error", "ConnectionRefusedError", conf)
        print("Escribir en el log")

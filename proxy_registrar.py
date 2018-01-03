#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor de eco en UDP simple."""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import socketserver
import sys
import json
import time
import random

class ConfigHandler(ContentHandler):
    """Funcion para leer el xml."""

    def __init__(self):
        """Creación de lista de configuración."""
        self.config = []

    def startElement(self, name, attr):
        """Obtención de atributos del archivo de configuración."""

        if name == "server":
            Name = attr.get('name', "")
            self.config.append(Name)
            ip = attr.get('ip', "")
            self.config.append(ip)
            Port = attr.get('puerto',"")
            self.config.append(Port)

        elif name == "database":
            User_Path = attr.get('path', "")

            self.config.append(User_Path)
            Passwd_Path = attr.get('passwdpath', "")
            self.config.append(Passwd_Path)

        elif name == "log":
            log_path = attr.get('path',"")
            self.config.append(log_path)

    def get_config(self):
        """ Devuelve la lista de configuración. """
        return self.config

class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    Client_data = {}

    def register2json(self):
        """Json creator."""
        with open('registered.json', "w") as outfile:
            json.dump(self.Client_data, outfile, sort_keys=True, indent=4)

    def json2registered(self):
        """Json file checker."""
        with open("registered.json", "r") as data_file:
            self.Client_data = json.load(data_file)

    def comprobar_cad_del(self):
        """Output time and user's delete checker."""
        time_str = time.strftime('%Y-%m-%d %H:%M:%S +%Z',
                                 time.gmtime(time.time()))
        deleted = []
        for cosas in self.Client_data:
            if self.Client_data[cosas]['Reg_time'] <= time_str:
                deleted.append(cosas)
        for users in deleted:
            self.Client_data.pop(users)

    def comprobar_usuario(self, usuario):
        """ FUNCION PARA COMPROBAR USUARIOS"""

        #cliente = usuario.split(":")[1]
        #print(cliente)
        user_pass = open("passwords", "r")
        self.user_pass = user_pass.read()
        usuarios_pass = self.user_pass.split('\n')
        #print(usuarios_pass)
        esta = False
        for i in range(len(usuarios_pass)):
            cliente = usuarios_pass[i].split(':')[0]
            if cliente == usuario :
                esta = True

        return esta

    def handle(self):
        """handle method of the server class."""
        atributos = {}  # Value de datos del cliente.



        if not self.Client_data:
            self.json2registered()

        Methods = ['REGISTER','BYE','INVITE']

        LINE = self.rfile.read()
        DATA = LINE.decode('utf-8')
        CORTES = DATA.split(' ')
        Method_Check = CORTES[0]
        USUARIO = CORTES[1]
        print("ESTE ES EL DATA: ", DATA)
        Expire = CORTES[3].split('\r')[0]
        Final_Check = CORTES[2].split('\r\n')[0]
        Protocol_Check = USUARIO.split(':')[0]
        USER = USUARIO.split(':')[1]
        cuerpo = DATA.split('\r\n\r\n')[1].split(' ')[0]
        print(cuerpo)
        nonce = random.randint(0,999999999999999999999)

        if Method_Check not in Methods:
            Answer = ('SIP/2.0 405 Method Not allowed' + '\r\n\r\n')
            self.wfile.write(bytes(Answer, 'utf-8'))

        elif Final_Check != 'SIP/2.0' or Protocol_Check != 'sip':
            Answer = ('SIP/2.0 400 Bad Request' + '\r\n\r\n')
            self.wfile.write(bytes(Answer, 'utf-8'))

        elif Method_Check == 'REGISTER':
            #print(USUARIO)

            if self.comprobar_usuario(USER) and cuerpo =='Authenticate:':
                print("entra en locura")
                time_expire_str = time.strftime('%Y-%m-%d %H:%M:%S +%Z',
                                                time.gmtime(time.time() +
                                                int(Expire)))
                atributos['address'] = self.client_address[0]
                atributos['port'] = str(self.client_address[1])
                atributos['Reg_time'] = time_expire_str
                atributos['t_expiracion[s]'] = Expire

                self.Client_data[USER] = atributos
                self.comprobar_cad_del()
                Answer = ('SIP/2.0 200 OK' + '\r\n\r\n')
                self.wfile.write(bytes(Answer, 'utf-8'))

            elif not self.comprobar_usuario(USER):
                print("NO ESTA EL USUARIO")
                Answer = ('SIP/2.0 404 User Not Found' + '\r\n\r\n')
                self.wfile.write(bytes(Answer, 'utf-8'))

            elif cuerpo != 'Authenticate:':
                Answer = ('SIP/2.0 401 Unauthorized' + '\r\n')
                Answer += ('WWW Authenticate: nonce=' + str(nonce)+ '\r\n\r\n')
                self.wfile.write(bytes(Answer, 'utf-8'))
                print('estamos dentro')

        elif Method_Check == 'INVITE':
            print("Pues es un invite loco")
            cabecera = DATA[:-4]
            Send_Inf =DATA.split('\r\n')
            RTPSENDER = Send_Inf[7].split(' ')[1]

            SENDER = DATA.split('\r\n')[4].split(' ')[0].split('=')[1]
            cliente = cabecera.split(' ')[1].split(':')[1]
            print(cliente)
            value = self.Client_data.get(cliente,"")
            print(cuerpo)
            #CREAMOS EL PAQUETE A ENVIAR
            USER_M = 'INVITE' + ' sip:' + value.get('address') + ' SIP/2.0\r\n'
            USER_M += 'Content-Type: application/sdp\r\n\r\n'
            Cuerpo = 'v=0\r\n' + 'o=' + SENDER + ' ' + value.get('port') + '\r\n'
            Cuerpo += 's=misesion\r\n' + 't=0\r\n'
            Cuerpo += 'm=audio ' + RTPSENDER + ' RTP\r\n\r\n'
            Data = USER_M + Cuerpo
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                my_socket.connect(('127.0.0.1' , int('6060')))
                print("Enviando:", USER_M)
                my_socket.send(bytes(Data, 'utf-8'))
                data = my_socket.recv(1024)
                print('Recibido -- ', data.decode('utf-8'))
                respuesta = data.decode('utf-8').split('\r\n\r\n')[0:3]
                response = respuesta[0]
                if Metodo == 'invite' and respuesta == ['SIP/2.0 100 Trying',
                                                    'SIP/2.0 180 Ringing',
                                                    'SIP/2.0 200 OK']:
                    USER_M = 'ACK' + ' sip:' + Destination
                    Data = USER_M + ' ' + 'SIP/2.0\r\n\r\n'
                    print("Enviando:", USER_M)
                    my_socket.send(bytes(Data, 'utf-8'))
                    print("Socket terminado.")
            except ConnectionRefusedError:
                print("Escribir en el log")
           # print("Datos cliente(IP, puerto): " + str(self.client_address))
           # print("El cliente nos manda ", DATA[:-4])
           #self.register2json()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        CONFIG = sys.argv[1]
        # print(CONFIG)         ESTO DE MOMENTO LO HACE BIEN
    else:
        sys.exit('Usage: python3 proxy_registrar.py config')

    parser = make_parser()
    pHandler = ConfigHandler()
    parser.setContentHandler(pHandler)
    parser.parse(open(CONFIG))
    config = pHandler.get_config()
    #print(config)
    Server_port = int(config[2])

    serv = socketserver.UDPServer(('', Server_port), SIPRegisterHandler)

    print("Server ",config[0],' listening at port',config[2],'...')
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")

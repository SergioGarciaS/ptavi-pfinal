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
import hashlib
from uaserver import log_maker

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
    Client_nonce = {}

    def register2json(self):
        """Json creator."""
        f = open('registered.txt', "w")
        for User in self.Client_data:
            value = self.Client_data[User]
            Line = User + ': Registro:' + value['Reg_time'] + ' Address:'
            Line += value['address'] + ':' + value['port']
            Line += ' Expire:' + value['t_expiracion[s]'] + "\r\n"
            f.write(Line)
        f.close()

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
        user_pass = open("passwords", "r")
        self.user_pass = user_pass.read()
        usuarios_pass = self.user_pass.split('\n')
        esta = False
        for i in range(len(usuarios_pass)):
            cliente = usuarios_pass[i].split(':')[0]
            if cliente == usuario :
                esta = True
        return esta

    def devolver_pass(self, usuario):
        """ FUNCION PARA COMPROBAR USUARIOS"""

        user_pass = open("passwords", "r")
        self.user_pass = user_pass.read()
        usuarios_pass = self.user_pass.split('\n')
        passwd = " "
        for i in range(len(usuarios_pass)):
            cliente = usuarios_pass[i].split(':')[0]
            if cliente == usuario :
                passwd = usuarios_pass[i].split(':')[1]

        return passwd

    def checking_nonce(self, nonce, user):
        """
        method to get the number result of hash function
        with password and nonce
        """
        function_check = hashlib.md5()
        function_check.update(bytes(str(nonce), "utf-8"))
        function_check.update(bytes(self.devolver_pass(user), "utf-8"))
        function_check.digest()
        return function_check.hexdigest()


    def send_to_server(self, ip, puerto, data, cabecera):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as pr_socket:
                pr_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                pr_socket.connect((ip , puerto))
                print("Enviando:", cabecera)
                pr_socket.send(bytes(data, 'utf-8'))
                print('Socket terminado')
                data = pr_socket.recv(1024)
                Recv = data.decode('utf-8')
                log_maker(config[5], "recibe", Recv)
                print('Recibido -- ', data.decode('utf-8'))
                respuesta = data.decode('utf-8').split('\r\n\r\n')[0:3]
                response = respuesta[0]
                corp = data.decode('utf-8').split('\r\n\r\n')[4:]
                self.wfile.write(bytes(Recv, 'utf-8'))

        except ConnectionRefusedError:
            print("Escribir en el log")

    def handle(self):
        """handle method of the server class."""
        atributos = {}  # Value de datos del cliente.
        Methods = ['REGISTER','BYE','INVITE','ACK']
        LINE = self.rfile.read()
        DATA = LINE.decode('utf-8')
        CORTES = DATA.split(' ')
        Method_Check = CORTES[0]
        USUARIO = CORTES[1]
        Final_Check = CORTES[2].split('\r\n')[0]
        Protocol_Check = USUARIO.split(':')[0]
        USER = USUARIO.split(':')[1]
        cuerpo = DATA.split('\r\n')[2].split(' ')[0]
        nonce = random.randint(0,99999)
        print("Datos cliente(IP, puerto): " + str(self.client_address))
        print("El cliente nos manda", DATA[:-4])

        if Method_Check not in Methods:
            Answer = ('SIP/2.0 405 Method Not allowed' + '\r\n\r\n')
            log_maker(config[5], "error", Answer)
            self.wfile.write(bytes(Answer, 'utf-8'))

        elif Final_Check != 'SIP/2.0' or Protocol_Check != 'sip':
            Answer = ('SIP/2.0 400 Bad Request' + '\r\n\r\n')
            log_maker(config[5], "error", Answer)
            self.wfile.write(bytes(Answer, 'utf-8'))

        elif Method_Check == 'REGISTER':
            Expire = CORTES[3].split('\r\n')[0]
            log_maker(config[5], "recibe", DATA)
            if self.comprobar_usuario(USER) and cuerpo =='Authenticate:':
                print("ENTRA CON AUTENTICATE")
                replica = DATA.split('\r\n')[2].split(' ')[1]
                n_client = self.Client_nonce.get(USER,"")
                resultado = self.checking_nonce(n_client,USER)
                if  resultado == replica:
                    print("ENTRA CON CONTRASEÑA Y ESTA EN LISTA")
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
                    log_maker(config[5], "envia", Answer)

                    self.wfile.write(bytes(Answer, 'utf-8'))
                else:
                    Answer = ('SIP/2.0 400 Bad Request' + '\r\n\r\n')
                    log_maker(config[5], "error", Answer)
                    self.wfile.write(bytes(Answer, 'utf-8'))
                    print("ENVIANDO: ",Answer)

            elif not self.comprobar_usuario(USER):
                print("NO ESTA EL USUARIO")
                Answer = ('SIP/2.0 404 User Not Found' + '\r\n\r\n')
                log_maker(config[5], "error", Answer)
                self.wfile.write(bytes(Answer, 'utf-8'))

            elif cuerpo != 'Authenticate:':
                print('VIENE SIN AUTORIZACION --->\r\n')
                self.Client_nonce[USER] = nonce
                Answer = ('SIP/2.0 401 Unauthorized' + '\r\n')
                Answer += ('WWW Authenticate: nonce=' + str(self.Client_nonce[USER])+ '\r\n\r\n')
                log_maker(config[5], "error", Answer)
                self.wfile.write(bytes(Answer, 'utf-8'))

        elif Method_Check == 'ACK' or Method_Check == 'BYE':

            print("ACK ES NUESTRO DESTINO")
            log_maker(config[5], "recibe", DATA)
            cabecera =  DATA[:-4]
            cliente = cabecera.split(' ')[1].split(':')[1]
            USER_M = Method_Check + ' sip:' + cliente + ' SIP/2.0'
            Datar = USER_M + '\r\n\r\n'
            IP = '127.0.0.1'
            puerto = 6060
            log_maker(config[5], "envia", Datar)
            self.send_to_server(IP, puerto, Datar, USER_M)

        elif Method_Check == 'INVITE':

            print("Pues es un invite loco")
            print("DATATONICA: ",DATA)
            log_maker(config[5], "recibe", DATA)
            cabecera = DATA[:-4]
            Send_Inf =DATA.split('\r\n')
            RTPSENDER = Send_Inf[7].split(' ')[1]
            SENDER = DATA.split('\r\n')[4].split(' ')[0].split('=')[1]
            cliente = cabecera.split(' ')[1].split(':')[1]
            value = self.Client_data.get(cliente,"")
            USER_M = 'INVITE' + ' sip:' + cliente + ' SIP/2.0\r\n\r\n'
            USER_M += 'Content-Type: application/sdp\r\n'
            Cuerpo = 'v=0\r\n' + 'o=' + SENDER + ' ' + value.get('address')
            Cuerpo += '\r\n' + 's=misesion\r\n' + 't=0\r\n'
            Cuerpo += 'm=audio ' + RTPSENDER + ' RTP\r\n\r\n'
            Data = USER_M + Cuerpo


            #MOVIDAS DE PRUEBA:
            IP = '127.0.0.1'
            puerto = 6060

            self.send_to_server(IP, puerto, Data, USER_M) #FUNCION ENVIAR.
            log_maker(config[5], "envia", Data)
        self.register2json()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        CONFIG = sys.argv[1]
    else:
        sys.exit('Usage: python3 proxy_registrar.py config')

    parser = make_parser()
    pHandler = ConfigHandler()
    parser.setContentHandler(pHandler)
    parser.parse(open(CONFIG))
    config = pHandler.get_config()
    Server_port = int(config[2])

    serv = socketserver.UDPServer(('', Server_port), SIPRegisterHandler)
    log_maker(config[5], "start", " ")
    print("Server ",config[0],' listening at port',config[2],'...')
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        log_maker(config[5], "fin", " ")
        print("Finalizado servidor")

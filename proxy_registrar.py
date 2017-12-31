#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor de eco en UDP simple."""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socketserver
import sys
import json
import time

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
            if self.Client_data[cosas]['expires'] <= time_str:
                deleted.append(cosas)
        for users in deleted:
            self.Client_data.pop(users)

    def handle(self):
        """handle method of the server class."""
        atributos = {}  # Value de datos del cliente.
        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")

        if not self.Client_data:
            self.json2registered()

        LINE = self.rfile.read()
        DATA = LINE.decode('utf-8')
        CORTES = DATA.split(' ')
        time_expire_str = time.strftime('%Y-%m-%d %H:%M:%S +%Z',
                                        time.gmtime(time.time() +
                                                    int(CORTES[3][:-4])))
        if CORTES[0] == 'REGISTER':
            atributos['address'] = self.client_address[0]
            if CORTES[3][:-4] != '0':
                atributos['expires'] = time_expire_str
            else:
                atributos['expires'] = time.strftime('%Y-%m-%d %H:%M:%S +%Z',
                                                     time.gmtime(time.time()))
            self.Client_data[CORTES[1]] = atributos
            self.comprobar_cad_del()

        print("Datos cliente(IP, puerto): " + str(self.client_address))
        print("El cliente nos manda ", DATA[:-4])

        self.register2json()


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
    print(config)
    Server_port = int(config[2])

    serv = socketserver.UDPServer(('', Server_port), SIPRegisterHandler)

    print("Server ",config[0],' listening at port',config[2],'...')
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")

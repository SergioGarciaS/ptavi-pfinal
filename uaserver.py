#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor de eco en UDP simple."""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socketserver
import sys
import os
import time


class ConfigHandler(ContentHandler):
    """Funcion para leer el xml."""

    def __init__(self):
        """Creación de lista de configuración."""
        self.config = []

    def startElement(self, name, attr):
        """Obtención de atributos del archivo de configuración."""
        if name == "account":
            username = attr.get('username', "")
            self.config.append(username)
            passwd = attr.get('passwd', "")
            self.config.append(passwd)

        elif name == "uaserver":
            ip = attr.get('ip', "")
            if ip == "":
                ip = "127.0.0.1"
            else:
                """ COMPROBAR SI ES VALIDA LA IP"""
            self.config.append(ip)
            port = attr.get('puerto', "")
            self.config.append(port)

        elif name == "rtpaudio":
            puerto_rtp = attr.get('puerto',"")
            self.config.append(puerto_rtp)

        elif name == "regproxy":
            dir_proxy = attr.get('ip', "")
            self.config.append(dir_proxy)
            port_proxy = attr.get('puerto',"")
            self.config.append(port_proxy)

        elif name == "log":
            log_path = attr.get('path',"")
            self.config.append(log_path)

        elif name == "audio":
            Audio_path = attr.get('path',"")
            self.config.append(Audio_path)

    def get_config(self):
        """ Devuelve la lista de configuración. """
        return self.config

def log_maker(path, hora, Evento):
    """ Función que escribe en el archivo log. """
    Log_file = open(path, 'a')
    hora = time.gmtime(float(hora))
    Log_file.write(time.strftime('%Y%m%d%h%M%S',hora)) #Escriba la hora.
    Log_file.write(Evento.replace("\r\n", " ") + '\r\n') #Escribo evento.
    Log_file.close()

class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""
    PORT_SEND_RTP = []

    def handle(self):
        """Programa principal."""
        Methods = ['INVITE', 'BYE', 'ACK']
        IP_Client = str(self.client_address[0])

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            PORT_SEND_RTP = '0000'
            line = self.rfile.read()
            if not line:
                break

            probar = line.decode('utf-8').split(' ')
            Protocol_Check = probar[1].split(':')[0]  #print(Protocol_Check)
            Method_Check = line.decode('utf-8').split(' ')[0]
            Final_Check = probar[2].split('\r\n')[0] # print(Final_Check)

            Audio_path = config[8]
            print(Audio_path)
            print("El cliente nos manda " + line.decode('utf-8'))

            if Method_Check not in Methods:
                Answer = ('SIP/2.0 405 Method Not allowed' + '\r\n\r\n')
                self.wfile.write(bytes(Answer, 'utf-8'))

            elif Final_Check != 'SIP/2.0' or Protocol_Check != 'sip':
                Answer = ('SIP/2.0 400 Bad Request' + '\r\n\r\n')
                self.wfile.write(bytes(Answer, 'utf-8'))

            elif Method_Check == 'INVITE':
                self.PORT_SEND_RTP.append(probar[5])
                cuerpo = ("Content-type: application/sdp\r\n"+
                          "\r\nv=0\r\n" + "o=" + str(config[0]) +
                          " " + str(config[2]) + "\r\ns=Pacticafinal\r\n" +
                          "t=0\r\nm=audio " + str(config[4]) + " RTP\r\n\r\n")

                Answer = ('SIP/2.0 100 Trying' + '\r\n\r\n' +
                          'SIP/2.0 180 Ringing' + '\r\n\r\n' +
                          'SIP/2.0 200 OK' + '\r\n\r\n' +
                          cuerpo)
                self.wfile.write(bytes(Answer, 'utf-8'))

            elif Method_Check == 'BYE':
                Answer = ('SIP/2.0 200 OK' + '\r\n\r\n')
                self.wfile.write(bytes(Answer, 'utf-8'))

            elif Method_Check == 'ACK':

                toRun = ('mp32rtp -i ' + IP_Client + ' -p ')
                toRun += (self.PORT_SEND_RTP[0] + ' < ' + Audio_path)
                print("Vamos a ejecutar", toRun)
                os.system(toRun)
                print(" *=====================*\n",
                      " |The file is send...|\n",
                      "*=====================*\n")

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    if len(sys.argv) == 2:
        CONFIG = sys.argv[1]
        # print(CONFIG)         ESTO DE MOMENTO LO HACE BIEN
    else:
        sys.exit('Usage: uaserver.py config')

    parser = make_parser()
    sHandler = ConfigHandler()
    parser.setContentHandler(sHandler)
    parser.parse(open(CONFIG))
    config = sHandler.get_config()
    #print('===================================',config,'======================')
    Direction = config[2]
    PORT = int(config[3])
    serv = socketserver.UDPServer((Direction, PORT), EchoHandler)
    print("Listening...")
    serv.serve_forever()

    #except KeyboardInterrupt:
     #   print("END OF SERVER")

#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor de eco en UDP simple."""

import socketserver
import sys
import os


class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    def handle(self):
        """Programa principal."""
        Methods = ['INVITE', 'BYE', 'ACK']
        IP_Client = str(self.client_address[0])
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            if not line:
                break
            probar = line.decode('utf-8').split(' ')
            Protocol_Check = probar[1].split(':')[0]
            Method_Check = line.decode('utf-8').split(' ')[0]
            Final_Check = probar[2]

            print("El cliente nos manda " + line.decode('utf-8'))

            if line.decode('utf-8').split(' ')[0] not in Methods:
                Answer = ('SIP/2.0 405 Method Not allowed' + '\r\n\r\n')
                self.wfile.write(bytes(Answer, 'utf-8'))

            elif Final_Check != 'SIP/2.0\r\n\r\n' or Protocol_Check != 'sip':
                Answer = ('SIP/2.0 400 Bad Request' + '\r\n\r\n')
                self.wfile.write(bytes(Answer, 'utf-8'))

            elif Method_Check == 'INVITE':
                Answer = ('SIP/2.0 100 Trying' + '\r\n\r\n' +
                          'SIP/2.0 180 Ringing' + '\r\n\r\n' +
                          'SIP/2.0 200 OK' + '\r\n\r\n')
                self.wfile.write(bytes(Answer, 'utf-8'))

            elif Method_Check == 'BYE':
                Answer = ('SIP/2.0 200 OK' + '\r\n\r\n')
                self.wfile.write(bytes(Answer, 'utf-8'))

            elif Method_Check == 'ACK':
                toRun = ('mp32rtp -i ' + IP_Client + ' -p 23032 < ' + FILE)
                print("Vamos a ejecutar", toRun)
                os.system(toRun)
                print(" *=====================*\n",
                      " |The file is send...|\n",
                      "*=====================*\n")

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    if len(sys.argv) == 4:
        IP = sys.argv[1]
        PORT = int(sys.argv[2])
        FILE = sys.argv[3]
    else:
        sys.exit('Usage: server.py IP PORT AUDIOFILE')

    serv = socketserver.UDPServer(('', PORT), EchoHandler)
    print("Listening...")
    serv.serve_forever()

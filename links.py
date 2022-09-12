import os
from sys import argv
import socket
from psutil import process_iter

APP_NAME = 'OceanShipsWar.exe'
processes = [p.name() for p in process_iter()]
if APP_NAME in processes:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.settimeout(1)
    sock.connect(('localhost', 6666))
    sock.send("|".join(argv))
    sock.recv(1024)
    sock.close()
else:
    os.system(f'python {os.path.split(__file__)[0]}\API.py {" ".join(argv)}')
input()

import socket

HOST = '192.168.0.43'
PORT = 9056

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'PING')
    data = s.recv(1024)

print(repr(data))

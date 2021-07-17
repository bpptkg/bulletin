import socket

HOST = '192.168.0.43'
PORT = 9056

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print('Listening on {}:{}'.format(HOST, PORT))
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected:', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(b'PONG')

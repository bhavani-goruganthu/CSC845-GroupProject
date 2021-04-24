import socket
from socket import AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET, SHUT_RDWR
import ssl

HOST = 'localhost'
PORT = 9993
server_cert = "../newcerts/server-cert.pem"
server_key = '../newcerts/server-key.pem'
ca_cert = '../newcerts/ca-cert.pem'

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(cafile=ca_cert)

bindsocket = socket.socket()
bindsocket.bind((HOST, PORT))
bindsocket.listen(5)

while True:
    print("Waiting for client")
    newsocket, fromaddr = bindsocket.accept()
    print("Client connected: {}:{}".format(fromaddr[0], fromaddr[1]))
    conn = context.wrap_socket(newsocket, server_side=True)
    print("SSL established. Peer: {}".format(conn.getpeercert()))
    try:
        while True:
            data = conn.recv(256).decode('utf-8')
            if data:
                print("Received:", data)
                break
    finally:
        print("Closing connection")
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
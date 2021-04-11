import socket
import ssl

HOST = 'localhost'
PORT = 9993
server_sni_hostname = 'aspirants'
ca_cert= "../newcerts/CA-cert.pem"

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=ca_cert)
context.load_cert_chain(certfile="../newcerts/server-cert.pem", keyfile="../newcerts/server-key.pem")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)
conn.connect((HOST, PORT))
print("SSL established. Peer: {}".format(conn.getpeercert()))
print("Sending: 'Hello, world!")
msg = input(" => ")
enc_msg = msg.encode('utf-8')
conn.sendall(enc_msg)
print("Closing connection")
conn.close()
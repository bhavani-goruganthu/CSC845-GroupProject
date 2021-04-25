import sys
import socket  # used to send and receive data between endpoints
import ssl # wrapper for socket objects - TLS encryption
from threading import Thread
from chatui import ChatUI
import m2proto
from getpass import getpass

HOST = "localhost"
PORT = int(sys.argv[1])
TLS = (sys.argv[-1] == "tls")

# create a socket object
# AF_INET similar to ipv4, SOCK_STREAM represents TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

if TLS:
    server_sni_hostname = 'aspirants'  # Common Name

    # create a SSLContext object
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile="newcerts/CA-cert.pem")
    context.load_cert_chain(certfile="newcerts/server-cert.pem", keyfile="newcerts/server-key.pem")

    client = context.wrap_socket(client_socket, server_side=False, server_hostname=server_sni_hostname)
else:
    client = client_socket

# connect to the host and port the server socket is on
client.connect((HOST, PORT))
print("Connected to the Server Socket..!!")

if TLS:
    cert = client.getpeercert()
    print(cert)

def receive():
    response = m2proto.recv(client)
    while response != None: # receive and print responses from the server (can be many)
        (msg_type, payload) = response
        if msg_type == 13:
            ui.set_prefix(payload)
        elif msg_type == 0:
            ui.add_output(payload)
            ui.set_prefix(None)
        response = m2proto.recv(client)
    ui.send_exit_signals()


def login():
    while True:
        username = input("Username: ")
        if not username:
            return False
        password = getpass("Password: ")
        if not password:
            return False
        if not m2proto.send(client, 8, username):
            print("Connection closed1.")
            return False
        if not m2proto.send(client, 9, password):
            print("Connection closed2.")
            return False
        response = m2proto.recv(client)
        if not response:
            print("Connection closed3.")
            return False
        elif response[0] == 10:
            print("Login successful.")
            return True
        elif response[0] == 12:
            print("New user registered.")
            return True
        elif response[0] == 11:
            print("Login failed.")
        else:
            print(f"Unexpected message type: {response[0]}")
            return False


try:
    if login():
        with ChatUI() as ui:
            receive_thread = Thread(target=receive, daemon=True)
            receive_thread.start() # start the receive thread
            message = ui.get_input() # get input from user
            while message != None:
                if not m2proto.send(client, 0, message): # send msgs from user to the server
                    break
                message = ui.get_input()
except KeyboardInterrupt:
    pass
finally:
    try:
        client.shutdown(socket.SHUT_RDWR)
        client.close()
    except:
        pass

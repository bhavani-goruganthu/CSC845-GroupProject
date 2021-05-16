import sys
import socket  # used to send and receive data between endpoints
import ssl # wrapper for socket objects - TLS encryption
from threading import Thread, Lock
from chatui import ChatUI
import m2proto
from getpass import getpass
import time

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

file_to_send = None
client_lock = Lock()


def receive():
    global file_to_send
    prefix = None
    file_sender = None
    file_to_receive = None
    response = m2proto.recv(client)
    while response is not None:  # receive and print responses from the server (can be many)
        (msg_type, payload) = response
        if msg_type == 13:
            prefix = payload
        elif msg_type == 0:
            ui.add_output(prefix, payload)
            prefix = None
        elif msg_type == 14:
            file_sender = payload
        elif msg_type == 15:
            incoming_filename = payload
            try:
                file_to_receive = open(incoming_filename, "xb")
            except:  # likely either FileExistsError or PermissionError, but we don't really care
                ui.add_output(None, "Unable to receive file from " + file_sender + ": " + incoming_filename)
                file_sender = None
                file_to_receive = None
                with client_lock:
                    m2proto.send(client, 17)
            else:
                with client_lock:
                    m2proto.send(client, 16)
                ui.add_output(None, "Receiving file from " + file_sender + ": " + incoming_filename)
        elif msg_type == 4:
            file_to_receive.write(payload)
        elif msg_type == 18:
            file_to_receive.close()
            ui.add_output(None, "Finished receiving file.")
        elif msg_type == 16:
            ui.add_output(None, "Sending file...")
            with client_lock:
                fd = file_to_send
                file_to_send = None
            Thread(target=send_file, daemon=True, args=(fd,)).start()
        elif msg_type == 17:
            ui.add_output(None, "Cannot send file.")
            with client_lock:
                if file_to_send is not None:
                    file_to_send.close()
                    file_to_send = None
        response = m2proto.recv(client)
    ui.send_exit_signals()


def send_file(fd):
    with fd:
        b = fd.read(4096)
        while b:
            time.sleep(1.0)  # just to simulate slow file transfer
            with client_lock:
                m2proto.send(client, 4, b)
            b = fd.read(4096)
        m2proto.send(client, 18)
    ui.add_output(None, "Finished sending file.")


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


def handle_command(command):
    global file_to_send
    parts = command.split()
    if len(parts) == 1 and (parts[0] == "q" or parts[0] == "quit"):
        raise KeyboardInterrupt
    elif len(parts) == 3 and parts[0] == "send":
        recipient = parts[1]
        filename = parts[2]
        try:
            fd = open(filename, "rb")
        except PermissionError:
            ui.add_output(None, "Cannot open file.")
        else:
            file_to_send = fd
            m2proto.send(client, 14, recipient)
            m2proto.send(client, 15, filename)
    else:
        ui.add_output(None, "Unrecognized command.")


try:
    if login():
        with ChatUI() as ui:
            receive_thread = Thread(target=receive, daemon=True)
            receive_thread.start() # start the receive thread
            message = ui.get_input() # get input from user
            while message is not None:
                with client_lock:
                    if message[0] == "/":
                        handle_command(message[1:])
                    elif not m2proto.send(client, 0, message): # send msgs from user to the server
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

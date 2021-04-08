import socket  # used to send and receive data between endpoints
import ssl # wrapper for socket objects - TLS encryption
from threading import Thread
from chatui import ChatUI
import m2proto
from getpass import getpass

# HOST = sys.argv[1]
# PORT = int(sys.argv[2])
HOST="localhost"
PORT=9996

# returns a new context with secure default settings
context = ssl.SSLContext(ssl.PROTOCOL_TLS)

# create a socket object
 # AF_INET similar to ipv4, SOCK_STREAM represents TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# to create a client-side SSL socket for the connection:
# conn = context.wrap_socket(client, server_side=False, server_hostname=server_hostname)
conn = context.wrap_socket(client, server_side=False, do_handshake_on_connect=False, 
    suppress_ragged_eofs=True, session=None)

# connect to the host and port the server socket is on
conn.connect((HOST, PORT))
print("Connected to the Server Socket..!!")


def receive():
    response = m2proto.recv(conn)
    while response != None: # receive and print responses from the server (can be many)
        (msg_type, payload) = response
        if msg_type == 13:
            ui.set_prefix(payload)
        elif msg_type == 0:
            ui.add_output(payload)
            ui.set_prefix(None)
        response = m2proto.recv(conn)
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
            print("Connection closed.")
            return False
        if not m2proto.send(client, 9, password):
            print("Connection closed.")
            return False
        response = m2proto.recv(client)
        if not response:
            print("Connection closed.")
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
                if not m2proto.send(conn, 0, message): # send msgs from user to the server
                    break
                message = ui.get_input()
except KeyboardInterrupt:
    pass
finally:
    try:
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
    except:
        pass

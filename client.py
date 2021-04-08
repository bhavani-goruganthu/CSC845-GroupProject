import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
import ssl # wrapper for socket objects - TLS encryption
from threading import Thread
from chatui import ChatUI
import m2proto

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
    while response != None:
        (msg_type , payload) = response
    # while response != None: # receive and print responses from the server (can be many)
        ui.add_output(payload)
        response = m2proto.recv(conn)
        # (msg_type , payload) = response
    ui.send_exit_signals()

try:
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

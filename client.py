import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
from threading import Thread
from chatui import ChatUI
import m2proto

# HOST = sys.argv[1]
# PORT = int(sys.argv[2])
HOST="localhost"
PORT=9996

# create a socket object
 # AF_INET similar to ipv4, SOCK_STREAM represents TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# connect to the host and port the server socket is on
client.connect((HOST, PORT))
print("Connected to the Server Socket..!!")

def receive():
    while True: # receive and print responses from the server (can be many)
        response = m2proto.recv(client)
        ui.add_output(response)

try:
    with ChatUI() as ui: 
        receive_thread = Thread(target=receive, daemon=True)
        receive_thread.start() # start the receive thread
        message = ui.get_input() # get input from user
        while message != None:
            m2proto.send(client,0,message) # send msgs from user to the server
            message = ui.get_input()
except KeyboardInterrupt:
    pass
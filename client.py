import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
from threading import Thread
from chatui import ChatUI
import m1proto

HOST = sys.argv[1]
PORT = int(sys.argv[2])
# HOST="localhost"
# PORT=9996

# create a socket object
 # AF_INET similar to ipv4, SOCK_STREAM represents TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to the host and port the server socket is on
client.connect((HOST, PORT))
print("Connected to the Server Socket..!!")

def receive():
    response = m1proto.recv(client)
    while response != None: # receive and print responses from the server (can be many)
        ui.add_output(response)
        response = m1proto.recv(client)
    ui.send_exit_signals()

try:
    with ChatUI() as ui:
        receive_thread = Thread(target=receive, daemon=True)
        receive_thread.start() # start the receive thread
        message = ui.get_input() # get input from user
        while message != None:
            if not m1proto.send(client, message): # send msgs from user to the server
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

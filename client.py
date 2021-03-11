import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
from m1proto import M1Protocol
from chatui import ChatUI

HOST = sys.argv[1]
PORT = int(sys.argv[2])
# create a socket object
 # AF_INET similar to ipv4, SOCK_STREAM represents TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to the host and port the server socket is on
client.connect((HOST, PORT))
print("Connected to the Server Socket..!!")

try:
    with M1Protocol(client) as proto, ChatUI() as ui:
        message = ui.get_input()
        while message != None:
            proto.send(message)
            response = proto.recv()
            if response == None:
                break
            ui.add_output(response)
            message = ui.get_input()
except KeyboardInterrupt:
    pass
finally:
    client.close()
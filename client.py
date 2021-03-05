import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
import m1proto
from chatui import ChatUI

HOST = sys.argv[1]
PORT = int(sys.argv[2])
# create a socket object
 # AF_INET similar to ipv4, SOCK_STREAM represents TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to the host and port the server socket is on
client.connect((HOST, PORT))
print("Connected to the Server Socket..!!")

proto = m1proto.M1Protocol(client)

try:
    with ChatUI() as ui:
        message = ui.get_input()
        while message != None:
            proto.send(message)
            response = proto.recv()
            ui.add_output(response)
            message = ui.get_input()
except KeyboardInterrupt:
    pass
finally:
    print(f"Closing connection to {HOST}.")
    client.shutdown(socket.SHUT_RDWR)
    client.close()

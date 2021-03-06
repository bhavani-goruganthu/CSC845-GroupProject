import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
from _thread import * # to accept multiple client connections
from m1proto import M1Protocol

HOST = sys.argv[1]
PORT = int(sys.argv[2])
# create a socket object
# AF_INET similar to ipv4, SOCK_STREAM represents TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print('Socket Created')
threadCount = 0

# bind to the host & port passed in the commandline
server.bind((HOST,PORT))
print('Waiting for Connection')
server.listen(5) # listen to connections

def client_thread(connection, address):
    with M1Protocol(connection) as proto:
        while True:
            data = proto.recv()
            if data is None:
                break # if data is not received break
            print(f"From connected Client {address}): " + str(data))
            if not proto.send(data):
                break

try:
    while True:
        connection, address = server.accept() # establish connection, blocking call, waits until there is a connection
        print("Connection successful! Address: " + address[0] + ':' + str(address[1]))
        start_new_thread(client_thread, (connection, address)) # create a new thread for every connected client
        threadCount +=1
        print('Thread Number: ' + str(threadCount))
except KeyboardInterrupt:
    pass
finally:
    server.close()

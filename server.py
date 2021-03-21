import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
from threading import Thread
from m1proto import M1Protocol

HOST = sys.argv[1]
PORT = int(sys.argv[2])
# HOST="localhost"
# PORT=9996

# create a socket object
# AF_INET similar to ipv4, SOCK_STREAM represents TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print('Socket Created')

threadCount = 0 # keep a count of no. of clients
clients = {} # to store list of clients

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
            # broadcast msg to all clients
            for single_client in clients:
                with M1Protocol(single_client) as proto_broadcast: # use connection object as single_client
                    proto_broadcast.send(data)

try:
    while True:
        connection, address = server.accept() # establish connection, blocking call, waits until there is a connection
        print("Connection successful! Address: " + address[0] + ':' + str(address[1]))
        # mark each client thread as daemon so that it exits when the main program exits
        client_thread_obj = Thread(target=client_thread, args=(connection, address),  daemon=True)
        client_thread_obj.start()
        clients[connection]= address[1] # store the connection object and the address
        threadCount +=1
        print('Thread Number: ' + str(threadCount))
except KeyboardInterrupt:
    sys.exit()
finally:
    server.close()
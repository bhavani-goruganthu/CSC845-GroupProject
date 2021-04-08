import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
import ssl # wrapper for socket objects - TLS encryption
from threading import Thread
import m2proto

# HOST = sys.argv[1]
# PORT = int(sys.argv[2])
HOST="localhost"
PORT=9996

# returns a new context with secure default settings
context = ssl.SSLContext(ssl.PROTOCOL_TLS)

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
    try:
        while True:
            data = m2proto.recv(connection)
            if data is not None:
                (msg_type , payload) = data
                if payload == '':
                    break # if payload is empty break
                print(f"From connected Client {address}): " + str(payload))
                # broadcast msg to all clients
                for single_client in clients:
                    m2proto.send(single_client, 0, payload)
            else:
                break
    finally:
        try:
            connection.shutdown(socket.SHUT_RDWR)
            connection.close()
        except:
            pass

try:
    while True:
        connection, address = server.accept() # establish connection, blocking call, waits until there is a connection
        print("Connection successful! Address: " + address[0] + ':' + str(address[1]))
        # to create a server-side SSL socket for the connection:
        # conn = context.wrap_socket(connection, server_side=True)
        conn = context.wrap_socket(connection, server_side=True, do_handshake_on_connect=False,suppress_ragged_eofs=True, session=None) 
        print("SSL established")
        # mark each client thread as daemon so that it exits when the main program exits
        client_thread_obj = Thread(target=client_thread, args=(conn, address),  daemon=True)
        client_thread_obj.start()
        clients[conn]= address[1] # store the connection object and the address
        threadCount +=1
        print('Thread Number: ' + str(threadCount))
except KeyboardInterrupt:
    sys.exit()
finally:
    try:
        server.shutdown(socket.SHUT_RDWR)
        server.close()
    except:
        pass

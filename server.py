import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
import ssl # wrapper for socket objects - TLS encryption
from threading import Thread, Lock
import m2proto
from auth import start_auth_thread, check_user_credentials_in_auth_thread

HOST = "localhost"
PORT = int(sys.argv[1])
TLS = (sys.argv[-1] == "tls")

if TLS:
    # certificate paths
    server_cert = "newcerts/server-cert.pem"
    server_key = 'newcerts/server-key.pem'
    ca_cert = 'newcerts/ca-cert.pem'

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(certfile=server_cert, keyfile=server_key)
    context.load_verify_locations(cafile=ca_cert)
else:
    context = None

# create a socket object
# AF_INET similar to ipv4, SOCK_STREAM represents TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print('Socket Created')

threadCount = 0 # keep a count of no. of clients
clients = {} # to store list of clients
clients_lock = Lock()
file_transfer_source_connection = None
file_transfer_target_connection = None

# bind to the host & port passed in the commandline
server.bind((HOST,PORT))
print('Waiting for Connection')
server.listen(5) # listen to connections

auth_queue = start_auth_thread("users.db")


def receive_login(connection):
    while True:
        username_msg = m2proto.recv(connection)
        if not username_msg or username_msg[0] != 8:
            return None
        password_msg = m2proto.recv(connection)
        if not password_msg or password_msg[0] != 9:
            return None

        result = check_user_credentials_in_auth_thread(auth_queue, username_msg[1], password_msg[1])
        if result == 10 or result == 12:
            m2proto.send(connection, result)
            print(username_msg[1])
            return username_msg[1]
        else:
            m2proto.send(connection, 11)


def client_thread(connection, address, threadNumber):
    global file_transfer_source_connection, file_transfer_target_connection
    try:
        username = receive_login(connection)
        if username is not None:
            with clients_lock:
                clients[threadNumber] = (connection, username)
            while True:
                data = m2proto.recv(connection)
                if data is not None:
                    (msg_type, payload) = data
                    if msg_type == 0:
                        print(f"From connected Client {address}): " + str(payload))
                        with clients_lock:
                            # broadcast msg to all clients
                            for target_connection, target_username in clients.values():
                                m2proto.send(target_connection, 13, username)
                                m2proto.send(target_connection, 0, payload)
                    elif msg_type == 14:
                        with clients_lock:
                            if file_transfer_source_connection is None:
                                file_transfer_source_connection = connection
                                file_transfer_target_connection = None
                                for target_connection, target_username in clients.values():
                                    if payload == target_username:
                                        file_transfer_target_connection = target_connection
                                        break
                                if file_transfer_target_connection is None:
                                    file_transfer_source_connection = None
                    elif msg_type == 15:
                        with clients_lock:
                            if file_transfer_source_connection != connection or file_transfer_target_connection is None:
                                m2proto.send(connection, 17)
                            else:
                                m2proto.send(file_transfer_target_connection, 14, username)
                                m2proto.send(file_transfer_target_connection, 15, payload)
                    elif msg_type == 16:
                        with clients_lock:
                            if file_transfer_target_connection == connection:
                                m2proto.send(file_transfer_source_connection, 16)
                    elif msg_type == 17:
                        with clients_lock:
                            if file_transfer_target_connection == connection:
                                m2proto.send(file_transfer_source_connection, 17)
                                file_transfer_source_connection = None
                                file_transfer_target_connection = None
                    elif msg_type == 18:
                        with clients_lock:
                            if file_transfer_source_connection == connection:
                                m2proto.send(file_transfer_target_connection, 18)
                                file_transfer_source_connection = None
                                file_transfer_target_connection = None
                    elif msg_type == 4:
                        with clients_lock:
                            if file_transfer_source_connection == connection:
                                m2proto.send(file_transfer_target_connection, 4, payload)
                else:
                    break
    finally:
        with clients_lock:
            try:
                del clients[threadNumber]
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
            except:
                pass


try:
    while True:
        conn, address = server.accept() # establish connection, blocking call, waits until there is a connection
        print("Connection successful! Address: " + address[0] + ':' + str(address[1]))
        
        # to create a server-side SSL socket for the connection:
        if TLS:
            connection = context.wrap_socket(conn, server_side=True)
            print("TLS established")
        else:
            connection = conn

        # mark each client thread as daemon so that it exits when the main program exits
        threadCount +=1
        client_thread_obj = Thread(target=client_thread, args=(connection, address, threadCount),  daemon=True)
        client_thread_obj.start()
        print('Thread Number: ' + str(threadCount))
except KeyboardInterrupt:
    sys.exit()
finally:
    try:
        server.shutdown(socket.SHUT_RDWR)
        server.close()
    except:
        pass

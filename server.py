import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
from threading import Thread, Lock
import m2proto
from auth import check_user_credentials

# HOST = sys.argv[1]
# PORT = int(sys.argv[2])
HOST="localhost"
PORT=9996

# create a socket object
# AF_INET similar to ipv4, SOCK_STREAM represents TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print('Socket Created')

threadCount = 0 # keep a count of no. of clients
clients = {} # to store list of clients
clients_lock = Lock()

# bind to the host & port passed in the commandline
server.bind((HOST,PORT))
print('Waiting for Connection')
server.listen(5) # listen to connections


def receive_login(connection):
    while True:
        username_msg = m2proto.recv(connection)
        if not username_msg or username_msg[0] != 8:
            return None
        password_msg = m2proto.recv(connection)
        if not password_msg or password_msg[0] != 9:
            return None
        if check_user_credentials(username_msg[1], password_msg[1]) == 10:
            m2proto.send(connection, 10, "")
            return username_msg[1]
        else:
            m2proto.send(connection, 11, "")


def client_thread(connection, address):
    try:
        username = receive_login(connection)
        if username is not None:
            clients_lock.acquire()
            try:
                clients[connection] = address[1]  # store the connection object and the address
            finally:
                clients_lock.release()
            while True:
                data = m2proto.recv(connection)
                if data is not None:
                    (msg_type , payload) = data
                    print(f"From connected Client {address}): " + str(payload))
                    clients_lock.acquire()
                    try:
                        # broadcast msg to all clients
                        for single_client in clients:
                            m2proto.send(single_client, 13, username)
                            m2proto.send(single_client, 0, payload)
                    finally:
                        clients_lock.release()
                else:
                    break
    finally:
        clients_lock.acquire()
        try:
            del clients[connection]
            connection.shutdown(socket.SHUT_RDWR)
            connection.close()
        except:
            pass
        finally:
            clients_lock.release()


try:
    while True:
        connection, address = server.accept() # establish connection, blocking call, waits until there is a connection
        print("Connection successful! Address: " + address[0] + ':' + str(address[1]))
        # mark each client thread as daemon so that it exits when the main program exits
        client_thread_obj = Thread(target=client_thread, args=(connection, address),  daemon=True)
        client_thread_obj.start()
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

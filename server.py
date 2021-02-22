import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
HOST = sys.argv[1]
PORT = int(sys.argv[2])
# create a socket object
# AF_INET similar to ipv4, SOCK_STREAM represents TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print('Socket Created')
# bind to the host & port passed in the commandline
server.bind((HOST,PORT))
server.listen(2) # listen to a connection
print('Waiting for Connection')

while True:
    try:
        connection, address = server.accept() # establish connection
        print(f"Connection successful! Address: {address}")
        while True:
            # receive data stream
            data = connection.recv(255).decode()
            if not data:
                # if data is not received break
                break
            print("From connected User: " + str(data))
            connection.send(data.encode())  # echo the same message to the client
        connection.close(); server.close();break
    except KeyboardInterrupt:
        print(f"closing connection to {address}.")
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        sys.exit()
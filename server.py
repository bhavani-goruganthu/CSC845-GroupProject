import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
from _thread import * # to accept multiple client connections

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
    while True:
        data_len = int.from_bytes(connection.recv(1), "big") # receive data stream
        data = connection.recv(data_len, socket.MSG_WAITALL).decode('utf-8')
        if not data:
            break # if data is not received break
        print(f"From connected Client {address}): " + str(data))
        enc_data = data.encode('utf-8')
        len_encdata = len(enc_data) # or can use data_len
        len_encdata = len_encdata.to_bytes(1,"big")
        enc_data = len_encdata + enc_data # add length to the msg before sending it
        connection.sendall(enc_data)  # echo the same message to the client        
    connection.close()

while True:
    try:
        connection, address = server.accept() # establish connection, blocking call, waits until there is a connection
        print("Connection successful! Address: " + address[0] + ':' + str(address[1]))
        start_new_thread(client_thread, (connection, address)) # create a new thread for every connected client
        threadCount +=1
        print('Thread Number: ' + str(threadCount))
    except KeyboardInterrupt:
        print("Closing Connection to the Address: " + address[0] + ':' + str(address[1]))
        connection.shutdown(socket.SHUT_RDWR)
        server.close()
        connection.close()
        sys.exit()
import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
HOST = sys.argv[1]
PORT = int(sys.argv[2])
# create a socket object
 # AF_INET similar to ipv4, SOCK_STREAM represents TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to the host and port the server socket is on
client.connect((HOST, PORT))

print("Enter Something: ")
message = input(" -> ")  # take input
while message.lower().strip() != 'bye':
    client.send(message.encode())  # send message
    data = client.recv(255).decode()  # receive response
    print('Received from Server: ' + data)  # show in terminal
    message = input(" -> ")  # again take input
    # print(message.lower().strip())
client.close()
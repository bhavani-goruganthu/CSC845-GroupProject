import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
import m1proto
HOST = sys.argv[1]
PORT = int(sys.argv[2])
# create a socket object
 # AF_INET similar to ipv4, SOCK_STREAM represents TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to the host and port the server socket is on
client.connect((HOST, PORT))

proto = m1proto.M1Protocol(client)

while True:
    try:
        print("Enter Something: ")
        message = input(" -> ")  # take input
        while message.lower().strip() != 'bye':
            proto.send(message)
            response = proto.recv()
            print('Received from Server: ' + response)  # show in terminal
            message = input(" -> ")  # again take input
        client.close()
    except KeyboardInterrupt:
        print(f"Closing connection to {HOST}.")
        client.shutdown(socket.SHUT_RDWR)
        client.close()
        sys.exit()

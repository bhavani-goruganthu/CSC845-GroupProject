import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
HOST = sys.argv[1]
PORT = int(sys.argv[2])
# create a socket object
 # AF_INET similar to ipv4, SOCK_STREAM represents TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to the host and port the server socket is on

while True:
    try:
        client.connect((HOST, PORT))
        print("Enter Something: ")
        message = input(" -> ")  # take input
        while message.lower().strip() != 'bye':
            enc_msg = message.encode('utf-8')
            len_encmsg = bin(len(enc_msg))
            len_encmsg = len_encmsg.encode('utf-8')
            print(len_encmsg)
            enc_msg = len_encmsg + enc_msg
            client.sendall(enc_msg)  # send message
            data = client.recv(255).decode('utf-8')  # receive response
            print('Received from Server: ' + str(data))  # show in terminal
            message = input(" -> ")  # again take input
            # print(message.lower().strip())
        client.close()
    except KeyboardInterrupt:
        print(f"Closing connection to {HOST}.")
        client.shutdown(socket.SHUT_RDWR)
        client.close()
        sys.exit()
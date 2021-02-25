import sys # to accept commandline arguments
import socket  # used to send and receive data between endpoints
HOST = sys.argv[1]
PORT = int(sys.argv[2])
# create a socket object
 # AF_INET similar to ipv4, SOCK_STREAM represents TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to the host and port the server socket is on
client.connect((HOST, PORT))

while True:
    try:
        print("Enter Something: ")
        message = input(" -> ")  # take input
        while message.lower().strip() != 'bye':
            enc_msg = message.encode('utf-8')
            len_encmsg = len(enc_msg)
            if len_encmsg <= 255:
                len_encmsg = len_encmsg.to_bytes(1,"big")
                enc_msg = len_encmsg + enc_msg
                client.sendall(enc_msg)  # send message
                data_len = int.from_bytes(client.recv(1),"big")
                data = client.recv(data_len, socket.MSG_WAITALL).decode('utf-8')  # receive response
                print('Received from Server: ' + str(data))  # show in terminal
                message = input(" -> ")  # again take input
            else:
                print("Character Limit is 255.. Try Again..")
                message = input(" -> ")  # again take input
        client.close()
    except KeyboardInterrupt:
        print(f"Closing connection to {HOST}.")
        client.shutdown(socket.SHUT_RDWR)
        client.close()
        sys.exit()
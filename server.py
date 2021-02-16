import socket  # used to send and receive data between endpoints

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET similar to ipv4, SOCK_STREAM represents TCP

# reserve a port 1234 & bind to it
s.bind((socket.gethostname(),1234))
s.listen(5) # listen to any connections

# until an interruption
while True:
    clientsocket, address = s.accept() # establish connection
    print(f"Connction successful! Address: {address}")
    clientsocket.send(bytes("Hello..", "utf-8"))
    # close the connection  
    clientsocket.close()
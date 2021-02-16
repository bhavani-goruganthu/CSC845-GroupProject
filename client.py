import socket  # used to send and receive data between endpoints

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET similar to ipv4, SOCK_STREAM represents TCP

# connect to the port 1234
s.connect((socket.gethostname(),1234))

# receive data from the server
msg= s.recv(1024)  # buffer size
print(msg.decode("utf-8")) # specify encoding

# close the connection  
s.close()  
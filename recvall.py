def recvall(socket, length):
    result = b''
    while len(result) < length:
        next_bytes = socket.recv(length - len(result))
        if next_bytes:
            result += next_bytes
        else:
            break
    return result

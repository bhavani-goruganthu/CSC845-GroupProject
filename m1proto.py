from recvall import recvall

class PayloadTooBig(Exception):
    """Exception raised when attempting to send a payload that is too large for
    the protocol to handle."""
    pass

def send(socket, message):
    """Send a message to the socket. Returns True if the message is sent
    successfully and False if the socket has been closed."""
    enc_msg = message.encode('utf-8')
    len_encmsg = len(enc_msg)
    if len_encmsg <= 255:
        len_encmsg = len_encmsg.to_bytes(1, "big")
        enc_msg = len_encmsg + enc_msg
        try:
            socket.sendall(enc_msg)
            return True
        except:
            return False
    else:
        raise PayloadTooBig

def recv(socket):
    """Receive a message from the socket. Returns a character string with
    the received payload. Returns None if the socket has been closed."""
    try:
        len_byte = recvall(socket, 1)
        if len_byte == b'':
            return None
        else:
            data_len = int.from_bytes(len_byte, "big")
            data = recvall(socket, data_len)
            if len(data) != data_len:
                return None
            else:
                return data.decode('utf-8')
    except:
        return None

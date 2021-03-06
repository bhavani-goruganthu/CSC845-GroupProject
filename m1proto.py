from socket import MSG_WAITALL

class PayloadTooBig(Exception):
    """Exception raised when attempting to send a payload that is too large for
    the protocol to handle."""
    pass

class M1Protocol:

    def __init__(self, socket):
        self.socket = socket

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except:
            pass
        return False

    def send(self, message):
        """Send a message to the socket. Returns True if the message is sent
        successfully and False if the socket has been closed."""
        enc_msg = message.encode('utf-8')
        len_encmsg = len(enc_msg)
        if len_encmsg <= 255:
            len_encmsg = len_encmsg.to_bytes(1, "big")
            enc_msg = len_encmsg + enc_msg
            try:
                self.socket.sendall(enc_msg)
                return True
            except:
                return False
        else:
            raise PayloadTooBig

    def recv(self):
        """Receive a message from the socket. Returns a character string with
        the received payload. Returns None if the socket has been closed."""
        try:
            len_byte = self.socket.recv(1)
            if len_byte == b'':
                return None
            else:
                data_len = int.from_bytes(len_byte, "big")
                data = self.socket.recv(data_len, MSG_WAITALL)
                if len(data) != data_len:
                    return None
                else:
                    return data.decode('utf-8')
        except:
            return None

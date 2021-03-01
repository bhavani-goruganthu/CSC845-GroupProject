from socket import MSG_WAITALL

class PayloadTooBig(Exception):
    """Exception raised when attempting to send a payload that is too large for
    the protocol to handle."""
    pass

class M1Protocol:

    def __init__(self, socket):
        self.socket = socket

    def send(self, message):
        """Send a message to the socket. Returns True if the message is sent
        successfully and False if the socket has been closed."""
        enc_msg = message.encode('utf-8')
        len_encmsg = len(enc_msg)
        if len_encmsg <= 255:
            len_encmsg = len_encmsg.to_bytes(1,"big")
            enc_msg = len_encmsg + enc_msg
            self.socket.sendall(enc_msg)
            return True
        else:
            raise PayloadTooBig

    def recv(self):
        """Receive a message from the socket. Returns a character string with
        the received payload. Returns None if the socket has been closed."""
        len_byte = self.socket.recv(1)
        if len_byte == b'':
            return None
        else:
            data_len = int.from_bytes(len_byte, "big")
            return self.socket.recv(data_len, MSG_WAITALL).decode('utf-8')

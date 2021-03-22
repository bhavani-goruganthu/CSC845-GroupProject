class PayloadTooBig(Exception):
    """Exception raised when attempting to send a payload that is too large for
    the protocol to handle for the provided message type."""
    pass

class InvalidType(Exception):
    """Exception raised when attempting to send a message with an invalid type
    (outside the range 0 to 63, inclusive)."""
    pass

def send(socket, msg_type, payload):
    """Send a message to the socket, given the message type as an integer
    value and the payload as a character string. Returns True if the
    message is sent successfully and False if the socket has been closed.
    Raises InvalidType if type is outside the range 0 to 63, inclusive.
    Raises PayloadTooBig is the payload is too big for the message type."""
    enc_msg = payload.encode('utf-8')
    len_encmsg = len(enc_msg)
    if len_encmsg == 0: # Empty Header Format
        # for message type = 0
        if msg_type >= 0 and msg_type <= 63:
            if msg_type == 0:
                arranged_bits = "11000000"
                msg_tosend = int(arranged_bits,2).to_bytes(1, "big")
                try:
                    socket.sendall(msg_tosend)
                    return True
                except:
                    return False
            # elif(msg_type >= 1 and msg_type <= 7):
            #     return True
        else:
            raise InvalidType        
    elif len_encmsg > 0 and len_encmsg <= 256: # Short Header Format
        if(msg_type >= 0 and msg_type <= 63):
            if(msg_type == 0):
                l_value = len_encmsg - 1
                arranged_bits = "10000000" # 1st byte
                byte_x = int(arranged_bits,2).to_bytes(1, "big")
                byte_y = l_value.to_bytes(1, "big")
                msg_tosend = byte_x+byte_y+enc_msg
                try:
                    socket.sendall(msg_tosend)
                    return True
                except:
                    return False
            # elif(msg_type >= 1 and msg_type <= 7):
            #     return True # to change it later
        else:
            raise InvalidType
    elif len_encmsg > 256 and len_encmsg<=4096: # Long Header Format
        if(msg_type >=0 and msg_type <= 63):
            if(msg_type == 0):
                l_value = len_encmsg - 1
                arranged_bits = "0000" # 4 bits
                byte_x = int(arranged_bits,2).to_bytes(1, "big")
                byte_y = l_value.to_bytes(2, "big") # rest bits -> 12
                # msg_tosend = byte_x+byte_y+enc_msg # why not this?
                msg_tosend = byte_y+enc_msg
                try:
                    socket.sendall(msg_tosend)
                    return True
                except:
                    return False
            # elif(msg_type >= 1 and msg_type <= 7):
            #     return True # to change it later
        else:
            raise InvalidType
    elif(len_encmsg > 4096): # Invalid Payload Size
        raise PayloadTooBig


def recv(socket):
    """Receive a message from the socket. Returns a pair containing the
    message type as an integer value and the payload as a character
    string. Returns None if the socket has been closed."""
    pass
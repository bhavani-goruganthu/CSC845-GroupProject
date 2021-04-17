from recvall import recvall

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
    l_value = len_encmsg - 1
    if len_encmsg == 0: # Empty Header Format
        # for message type = 0
        if msg_type >= 0 and msg_type <= 63:
            msg_tosend = (int(bin(msg_type),2)  | 0b11000000 ).to_bytes(1, "big") # 1st byte
            try:
                socket.sendall(msg_tosend)
                return True
            except:
                return False
        else:
            raise InvalidType        
    elif len_encmsg > 0 and len_encmsg <= 256: # Short Header Format
        # types for which max payload is 0
        if (msg_type >= 0 and  msg_type <=9) or (msg_type >=13 and msg_type <= 63):
                byte_x = (int(bin(msg_type),2)  | 0b10000000 ).to_bytes(1, "big") # 1st byte
                byte_y = l_value.to_bytes(1, "big")
                msg_tosend = byte_x+byte_y+enc_msg
                try:
                    socket.sendall(msg_tosend)
                    return True
                except:
                    return False
        else:
            raise InvalidType
    elif len_encmsg > 256 and len_encmsg<=4096: # Long Header Format
        if msg_type >=0 and msg_type <= 7:
            if msg_type == 0:                
                byte_y = l_value.to_bytes(2, "big") 
                msg_tosend = byte_y+enc_msg
                try:
                    socket.sendall(msg_tosend)
                    return True
                except:
                    return False
            elif(msg_type >= 1 and msg_type <= 7):
                byte_x_int = ((int(bin(msg_type),2) << 4) & 0b01110000 ) | ((int(bin(l_value),2) & 0b111100000000) >> 8)
                byte_y_int = int(bin(l_value),2) & 0b000011111111                
                byte_x = byte_x_int.to_bytes(1, "big") 
                byte_y = byte_y_int.to_bytes(1, "big") 
                msg_tosend = byte_x+byte_y+enc_msg
                try:
                    socket.sendall(msg_tosend)
                    return True
                except:
                    return False            
        else:
            raise InvalidType
    elif len_encmsg > 4096: # Invalid Payload Size
        raise PayloadTooBig

def recv(socket):
    """Receive a message from the socket. Returns a pair containing the
    message type as an integer value and the payload as a character
    string. Returns None if the socket has been closed."""
    try:
        byte_x = int.from_bytes(recvall(socket, 1), "big")
        if byte_x == b'':
            return None
        elif (byte_x >> 7 & 1) == 1:
            if (byte_x >> 6 & 1) == 1: # Empty Header Format
                msg_type = byte_x & 0b00111111
                return (msg_type,'')
            elif (byte_x >> 6 & 0) == 0: # Short Header Format
                msg_type = byte_x & 0b00111111
                try:
                    byte_y = int.from_bytes(recvall(socket, 1), 'big') # read byte_y which is the payload length - 1
                    if byte_y == b'':
                        return None
                    else:
                        payload = recvall(socket, byte_y + 1)
                        if len(payload) != byte_y + 1:
                            return None
                        else:                        
                            return (msg_type, payload.decode('utf-8'))
                except:
                    return None
        elif (byte_x >> 7 & 1) == 0: # Long Header Format            
            try:
                msg_type = ( byte_x & 0b01110000 ) >> 4
                byte_y = int.from_bytes(recvall(socket, 1), 'big') # read byte_y which is the payload length - 1
                if byte_y == b'':
                        return None
                else:
                    l_value = ((byte_x & 0b00001111) << 8) | byte_y
                    payload = recvall(socket, l_value + 1)
                    if len(payload) != l_value + 1:
                        return None
                    else:                    
                        return (msg_type, payload.decode('utf-8'))
            except:
                return None
        else:
            return None        
    except:
        return None

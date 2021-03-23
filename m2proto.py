from socket import MSG_WAITALL
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
                msg_tosend = 0b11000000.to_bytes(1, "big") # 1st byte
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
        if msg_type >= 0 and msg_type <= 63:
            if msg_type == 0:
                l_value = len_encmsg - 1
                byte_x = 0b10000000.to_bytes(1, "big") # 1st byte
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
        if msg_type >=0 and msg_type <= 63:
            if msg_type == 0:
                l_value = len_encmsg - 1
                # byte_x = 0b0000.to_bytes(1, "big") # 4 bits
                byte_y = l_value.to_bytes(2, "big") # rest bits -> 12
                # msg_tosend = byte_x+byte_y+enc_msg
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
    elif len_encmsg > 4096: # Invalid Payload Size
        raise PayloadTooBig

def recv(socket):
    """Receive a message from the socket. Returns a pair containing the
    message type as an integer value and the payload as a character
    string. Returns None if the socket has been closed."""
    try:
        byte_x = int.from_bytes(socket.recv(1),"big")
        msg_type_bits = [] # bits put in a list for decoding the message type T
        l_value_bits = [] # bits put in a list for decoding the value of L (Long Header Format)
        if (byte_x >> 7 & 1) == 1:
            if (byte_x >> 6 & 1) == 1: # Empty Header Format
                for bit_x in range(5,-1,-1):
                    msg_type_bits.append(byte_x >> bit_x & 1)
                msg_type = int(''.join(map(str,msg_type_bits)),2) # msg type integer 0 to 63
                if (msg_type == 0): # type 0
                    return (0,'')
                else: # for other types
                    return None
            elif (byte_x >> 6 & 0) == 0: # Short Header Format
                for bit_x in range(5,-1,-1):
                    msg_type_bits.append(byte_x >> bit_x & 1)
                msg_type = int(''.join(map(str,msg_type_bits)),2) # msg type integer 0 to 63
                byte_y = int.from_bytes(socket.recv(1),'big') # read byte_y which is the payload length - 1
                payload = socket.recv(byte_y+1, MSG_WAITALL)
                if (msg_type == 0): # type 0                
                    return (0, payload.decode('utf-8'))
                else: # for other types
                    return None
        elif (byte_x >> 7 & 1) == 0: # Long Header Format
            # for msg_type
            for bit_x in range(6,3,-1):
                msg_type_bits.append(byte_x >> bit_x & 1)
            msg_type = int(''.join(map(str,msg_type_bits)),2) # msg type integer 0 to 63
            
            # for value of L
            for bit_x in range(3,-1,-1):
                l_value_bits.append(byte_x >> bit_x & 1)
            l_value_fromx = int(''.join(map(str,l_value_bits)),2)
            byte_y = int.from_bytes(socket.recv(1),'big') # read byte_y which is the payload length - 1
            
            l_value = (l_value_fromx << 8) + byte_y

            payload = socket.recv(l_value+1, MSG_WAITALL)
            
            if (msg_type == 0): # type 0
                return (0, payload.decode('utf-8'))
            else: # for other types
                return None
        else:
            return None
    except:
        pass
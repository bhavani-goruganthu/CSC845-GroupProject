class PayloadTooBig(Exception):
    """Exception raised when attempting to send a payload that is too large for
    the protocol to handle for the provided message type."""
    pass

class InvalidType(Exception):
    """Exception raised when attempting to send a message with an invalid type
    (outside the range 0 to 63, inclusive)."""
    pass

def send(socket, type, payload):
    """Send a message to the socket, given the message type as an integer
    value and the payload as a character string. Returns True if the
    message is sent successfully and False if the socket has been closed.
    Raises InvalidType if type is outside the range 0 to 63, inclusive.
    Raises PayloadTooBig is the payload is too big for the message type."""
    pass

def recv(socket):
    """Receive a message from the socket. Returns a pair containing the
    message type as an integer value and the payload as a character
    string. Returns None if the socket has been closed."""
    pass

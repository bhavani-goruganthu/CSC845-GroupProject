from socket import MSG_WAITALL

class FakeReadableSocket:

    def __init__(self, data, raise_at_end = False):
        self.data = data
        self.raise_at_end = raise_at_end

    def recv(self, max_bytes, flags = 0):
        data = self.data
        if flags != 0 and flags != MSG_WAITALL:
            raise AssertionError("The ony flag supported by FakeReadableSocket"
                " is MSG_WAITALL")
        elif len(data) == 0:
            if self.raise_at_end:
                raise Exception
            else:
                return data
        elif flags == 0:
            self.data = data[1:]
            return data[:1]
        else:
            self.data = data[max_bytes:]
            return data[:max_bytes]

    def fake_data(self):
        return self.data

class FakeWritableSocket:

    def __init__(self, max_bytes = None):
        self.data = b''
        self.max_bytes = max_bytes

    def send(self, data):
        if data == b'' or len(self.data) == self.max_bytes:
            return 0
        else:
            self.data += data[:1]
            return 1

    def sendall(self, data):
        actual_sent = (len(data) if self.max_bytes == None
            else min(len(data), self.max_bytes - len(self.data)))
        self.data += data[:actual_sent]
        if actual_sent < len(data):
            raise Exception
        else:
            return None

    def fake_data(self):
        return self.data

from socket import MSG_WAITALL

class FakeReadableSocket:

    def __init__(self, data):
        self.data = data

    def recv(self, max_bytes, flags = 0):
        data = self.data
        if flags != 0 and flags != MSG_WAITALL:
            raise ValueError("The ony flag supported by FakeReadableSocket"
                " is MSG_WAITALL")
        elif len(data) == 0:
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

    def __init__(self):
        self.data = b''

    def send(self, data):
        if data == b'':
            return 0
        else:
            self.data += data[:1]
            return 1

    def sendall(self, data):
        self.data += data
        return len(data)

    def fake_data(self):
        return self.data

from m1proto import M1Protocol, PayloadTooBig
from fake_sockets import FakeReadableSocket, FakeWritableSocket
from unittest import TestCase

class M1ProtocolTests(TestCase):

    def test_send_empty(self):
        socket = FakeWritableSocket()
        proto = M1Protocol(socket)
        self.assertTrue(proto.send(''))
        self.assertEqual(socket.fake_data(), b'\0')

    def test_send_ascii(self):
        socket = FakeWritableSocket()
        proto = M1Protocol(socket)
        self.assertTrue(proto.send('abc'))
        self.assertEqual(socket.fake_data(), b'\x03abc')

    def test_send_unicode(self):
        socket = FakeWritableSocket()
        proto = M1Protocol(socket)
        self.assertTrue(proto.send('\xA0'))
        self.assertEqual(socket.fake_data(), b'\x02\xC2\xA0')

    def test_send_max(self):
        socket = FakeWritableSocket()
        proto = M1Protocol(socket)
        self.assertTrue(proto.send('x' * 255))
        self.assertEqual(socket.fake_data(), b'\xFF' + (b'x' * 255))

    def test_send_too_big(self):
        socket = FakeWritableSocket()
        proto = M1Protocol(socket)
        with self.assertRaises(PayloadTooBig):
            proto.send('x' * 256)
        self.assertEqual(socket.fake_data(), b'')

    def test_send_error(self):
        socket = FakeWritableSocket(0)
        proto = M1Protocol(socket)
        self.assertFalse(proto.send('abcde'))

    def test_send_error_after_first_byte(self):
        socket = FakeWritableSocket(1)
        proto = M1Protocol(socket)
        self.assertFalse(proto.send('abcde'))

    def test_send_error_with_partial_paload(self):
        socket = FakeWritableSocket(3)
        proto = M1Protocol(socket)
        self.assertFalse(proto.send('abcde'))

    def test_recv_empty(self):
        socket = FakeReadableSocket(b'\0')
        proto = M1Protocol(socket)
        self.assertEqual(proto.recv(), '')

    def test_recv_ascii(self):
        socket = FakeReadableSocket(b'\x03abc')
        proto = M1Protocol(socket)
        self.assertEqual(proto.recv(), 'abc')

    def test_recv_unicode(self):
        socket = FakeReadableSocket(b'\x02\xC2\xA0')
        proto = M1Protocol(socket)
        self.assertEqual(proto.recv(), '\xA0')

    def test_recv_max(self):
        socket = FakeReadableSocket(b'\xFF' + (b'x' * 254) + b'X')
        proto = M1Protocol(socket)
        self.assertEqual(proto.recv(), ('x' * 254) + 'X')

    def test_recv_end(self):
        socket = FakeReadableSocket(b'')
        proto = M1Protocol(socket)
        self.assertIsNone(proto.recv())

    def test_recv_end_after_first_byte(self):
        socket = FakeReadableSocket(b'\x05')
        proto = M1Protocol(socket)
        self.assertIsNone(proto.recv())

    def test_recv_end_with_partial_payload(self):
        socket = FakeReadableSocket(b'\x05abc')
        proto = M1Protocol(socket)
        self.assertIsNone(proto.recv())

    def test_recv_error(self):
        socket = FakeReadableSocket(b'', True)
        proto = M1Protocol(socket)
        self.assertIsNone(proto.recv())

    def test_recv_error_after_first_byte(self):
        socket = FakeReadableSocket(b'\x05', True)
        proto = M1Protocol(socket)
        self.assertIsNone(proto.recv())

    def test_recv_error_with_partial_payload(self):
        socket = FakeReadableSocket(b'\x05abc', True)
        proto = M1Protocol(socket)
        self.assertIsNone(proto.recv())

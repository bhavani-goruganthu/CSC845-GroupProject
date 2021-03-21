import m1proto
from fake_sockets import FakeReadableSocket, FakeWritableSocket
from unittest import TestCase

class M1ProtocolTests(TestCase):

    def test_send_empty(self):
        socket = FakeWritableSocket()
        self.assertTrue(m1proto.send(socket, ''))
        self.assertEqual(socket.fake_data(), b'\0')

    def test_send_ascii(self):
        socket = FakeWritableSocket()
        self.assertTrue(m1proto.send(socket, 'abc'))
        self.assertEqual(socket.fake_data(), b'\x03abc')

    def test_send_unicode(self):
        socket = FakeWritableSocket()
        self.assertTrue(m1proto.send(socket, '\xA0'))
        self.assertEqual(socket.fake_data(), b'\x02\xC2\xA0')

    def test_send_max(self):
        socket = FakeWritableSocket()
        self.assertTrue(m1proto.send(socket, 'x' * 255))
        self.assertEqual(socket.fake_data(), b'\xFF' + (b'x' * 255))

    def test_send_too_big(self):
        socket = FakeWritableSocket()
        with self.assertRaises(m1proto.PayloadTooBig):
            m1proto.send(socket, 'x' * 256)
        self.assertEqual(socket.fake_data(), b'')

    def test_send_error(self):
        socket = FakeWritableSocket(0)
        self.assertFalse(m1proto.send(socket, 'abcde'))

    def test_send_error_after_first_byte(self):
        socket = FakeWritableSocket(1)
        self.assertFalse(m1proto.send(socket, 'abcde'))

    def test_send_error_with_partial_paload(self):
        socket = FakeWritableSocket(3)
        self.assertFalse(m1proto.send(socket, 'abcde'))

    def test_recv_empty(self):
        socket = FakeReadableSocket(b'\0')
        self.assertEqual(m1proto.recv(socket), '')

    def test_recv_ascii(self):
        socket = FakeReadableSocket(b'\x03abc')
        self.assertEqual(m1proto.recv(socket), 'abc')

    def test_recv_unicode(self):
        socket = FakeReadableSocket(b'\x02\xC2\xA0')
        self.assertEqual(m1proto.recv(socket), '\xA0')

    def test_recv_max(self):
        socket = FakeReadableSocket(b'\xFF' + (b'x' * 254) + b'X')
        self.assertEqual(m1proto.recv(socket), ('x' * 254) + 'X')

    def test_recv_end(self):
        socket = FakeReadableSocket(b'')
        self.assertIsNone(m1proto.recv(socket))

    def test_recv_end_after_first_byte(self):
        socket = FakeReadableSocket(b'\x05')
        self.assertIsNone(m1proto.recv(socket))

    def test_recv_end_with_partial_payload(self):
        socket = FakeReadableSocket(b'\x05abc')
        self.assertIsNone(m1proto.recv(socket))

    def test_recv_error(self):
        socket = FakeReadableSocket(b'', True)
        self.assertIsNone(m1proto.recv(socket))

    def test_recv_error_after_first_byte(self):
        socket = FakeReadableSocket(b'\x05', True)
        self.assertIsNone(m1proto.recv(socket))

    def test_recv_error_with_partial_payload(self):
        socket = FakeReadableSocket(b'\x05abc', True)
        self.assertIsNone(m1proto.recv(socket))

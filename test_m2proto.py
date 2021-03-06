from m2proto import M2Protocol, PayloadTooBig, InvalidType
from fake_sockets import FakeReadableSocket, FakeWritableSocket
from unittest import TestCase

class M2ProtocolTests(TestCase):

    def __test_send(self, type, payload, expected_data):
        socket = FakeWritableSocket()
        proto = M2Protocol(socket)
        self.assertTrue(proto.send(type, payload))
        self.assertEqual(socket.fake_data(), expected_data)

    def __test_send_raises(self, type, payload, expected_exception):
        socket = FakeWritableSocket()
        proto = M2Protocol(socket)
        with self.assertRaises(expected_exception):
            proto.send(type, payload)
        self.assertEqual(socket.fake_data(), b'')

    def __test_recv(self, socket_data, expected_type, expected_payload):
        socket = FakeReadableSocket(socket_data)
        proto = M2Protocol(socket)
        self.assertEqual(proto.recv(), (expected_type, expected_payload))

    def test_send_empty(self):
        self.__test_send(0, '', b'\xC0')

    def test_send_ascii_short(self):
        self.__test_send(0, 'abc', b'\x80\x02abc')

    def test_send_unicode_short(self):
        self.__test_send(0, '\xA0', b'\x80\x01\xC2\xA0')

    def test_send_max_short(self):
        self.__test_send(0, 'x' * 256, b'\x80\xFF' + (b'x' * 256))

    def test_send_min_long(self):
        self.__test_send(0, 'x' * 257, b'\x01\x00' + (b'x' * 257))

    def test_send_max_long(self):
        self.__test_send(0, 'x' * 4096, b'\x0F\xFF' + (b'x' * 4096))

    def test_send_max_type_for_long(self):
        self.__test_send(7, 'x' * 4096, b'\x7F\xFF' + (b'x' * 4096))

    def test_send_too_big_for_long(self):
        self.__test_send_raises(0, 'x' * 4097, PayloadTooBig)

    def test_send_too_big_for_short(self):
        self.__test_send_raises(8, 'x' * 257, PayloadTooBig)

    def test_send_negative_type(self):
        self.__test_send_raises(-1, '', InvalidType)

    def test_send_type_too_large(self):
        self.__test_send_raises(64, '', InvalidType)

    def test_send_empty_other_type(self):
        self.__test_send(18, '', b'\xD2')

    def test_send_short_other_type(self):
        self.__test_send(23, 'abc', b'\x97\x02abc')

    def test_send_long_other_type(self):
        self.__test_send(5, 'x' * 257, b'\x51\x00' + (b'x' * 257))

    def test_send_unicode_long(self):
        self.__test_send(3, '\xA0' * 200, b'\x31\x8F' + (b'\xC2\xA0' * 200))

    def test_send_error(self):
        socket = FakeWritableSocket(0)
        proto = M2Protocol(socket)
        self.assertFalse(proto.send(0, 'abcde'))

    def test_send_error_after_first_byte(self):
        socket = FakeWritableSocket(1)
        proto = M2Protocol(socket)
        self.assertFalse(proto.send(0, 'abcde'))

    def test_send_error_after_second_byte(self):
        socket = FakeWritableSocket(2)
        proto = M2Protocol(socket)
        self.assertFalse(proto.send(0, 'abcde'))

    def test_send_error_with_partial_payload(self):
        socket = FakeWritableSocket(4)
        proto = M2Protocol(socket)
        self.assertFalse(proto.send(0, 'abcde'))

    def test_recv_empty(self):
        self.__test_recv(b'\xC0', 0, '')

    def test_recv_ascii_short(self):
        self.__test_recv(b'\x80\x02abc', 0, 'abc')

    def test_recv_unicode_short(self):
        self.__test_recv(b'\x80\x01\xC2\xA0', 0, '\xA0')

    def test_recv_max_short(self):
        self.__test_recv(b'\x80\xFF' + (b'x' * 255) + b'X', 0, ('x' * 255) + 'X')

    def test_recv_max_long(self):
        self.__test_recv(b'\x0F\xFF' + (b'x' * 4095) + b'X', 0, ('x' * 4095) + 'X')

    def test_recv_empty_other_type(self):
        self.__test_recv(b'\xD2', 18, '')

    def test_recv_short_other_type(self):
        self.__test_recv(b'\x97\x02abc', 23, 'abc')

    def test_recv_long_other_type(self):
        self.__test_recv(b'\x51\x00' + (b'x' * 257), 5, 'x' * 257)

    def test_recv_unicode_long(self):
        self.__test_recv(b'\x31\x8F' + (b'\xC2\xA0' * 200), 3, '\xA0' * 200)

    def test_recv_end(self):
        socket = FakeReadableSocket(b'')
        proto = M2Protocol(socket)
        self.assertIsNone(proto.recv())

    def test_recv_end_after_first_byte(self):
        socket = FakeReadableSocket(b'\x00')
        proto = M2Protocol(socket)
        self.assertIsNone(proto.recv())

    def test_recv_end_after_second_byte(self):
        socket = FakeReadableSocket(b'\x00\x05')
        proto = M2Protocol(socket)
        self.assertIsNone(proto.recv())

    def test_recv_end_with_partial_payload(self):
        socket = FakeReadableSocket(b'\x00\x05abc')
        proto = M2Protocol(socket)
        self.assertIsNone(proto.recv())

    def test_recv_error(self):
        socket = FakeReadableSocket(b'', True)
        proto = M2Protocol(socket)
        self.assertIsNone(proto.recv())

    def test_recv_error_after_first_byte(self):
        socket = FakeReadableSocket(b'\x00', True)
        proto = M2Protocol(socket)
        self.assertIsNone(proto.recv())

    def test_recv_error_after_second_byte(self):
        socket = FakeReadableSocket(b'\x00\x05', True)
        proto = M2Protocol(socket)
        self.assertIsNone(proto.recv())

    def test_recv_error_with_partial_payload(self):
        socket = FakeReadableSocket(b'\x00\x05abc', True)
        proto = M2Protocol(socket)
        self.assertIsNone(proto.recv())

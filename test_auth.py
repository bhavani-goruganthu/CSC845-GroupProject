import unittest
from auth import *


class MyTestCase(unittest.TestCase):
    def test_user_insert(self):
        salt = b' the spammish repetition'
        password = b'\x03\x1e\xdd}Ae\x15\x93\xc5\xfe\\\x00o\xa5u+7\xfd\xdf\xf7\xbcN\x84:\xa6\xaf\x0c\x95\x0fK\x94\x06'
        id = insert_user("test_user", salt, password)
        self.assertGreater(id, 0)

    def test_random_user_insert(self):
        id = insert_random_user()
        self.assertGreater(id, 0)

    def test_view_users(self):
        records = view_users()
        self.assertFalse(records is None)

    def test_get_table_schema(self):
        schema = get_table_schema()
        self.assertFalse(schema is None)

    def test_salted_password_hashing(self):
        password = "Nobody inspects"
        salt = b" the spammish repetition"
        value = salted_password_hashing(password, salt)
        true_val = b'\x03\x1e\xdd}Ae\x15\x93\xc5\xfe\\\x00o\xa5u+7\xfd\xdf\xf7\xbcN\x84:\xa6\xaf\x0c\x95\x0fK\x94\x06'
        self.assertEqual(value, true_val)

    def test_valid_credentials(self):
        password = "Nobody inspects"
        res = check_user_credentials('test_user', password)
        self.assertEqual(res, 10)

    def test_invalid_password(self):
        password = "not valid"
        res = check_user_credentials('test_user', password)
        self.assertEqual(res, 11)

    def test_invalid_username(self):
        password = "Nobody inspects"
        res = check_user_credentials('not_user', password)
        self.assertEqual(res, 11)

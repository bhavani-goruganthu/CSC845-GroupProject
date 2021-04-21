import unittest
from auth import *
import sqlite3 as sql


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = sql.connect(":memory:")
        c = self.conn.cursor()
        cmd = "CREATE TABLE users (login TEXT NOT NULL, salt BLOB NOT NULL, hash TEXT NOT NULL)"
        c.execute(cmd)
        self.conn.commit()

    def test_user_insert(self):
        salt = b'1\xf0;\xe0\xaf\x02\xf2\x16'
        password = b"P'\x9d\xbbX\x0e\x1b0\xe6\xfd\x02:\x18\x9e3E\x92\x867\xe7\x18\xc8k7\xcfkW\x92\x86\xb7\xa4l"
        id = insert_user("sally", salt, password, self.conn)
        self.assertGreater(id, 0)

    def test_random_user_insert(self):
        id = insert_random_user(self.conn)
        self.assertGreater(id, 0)

    def test_register(self):
        id = register("cool", "sfsu", self.conn)
        self.assertGreater(id, 0)

    def test_view_users(self):
        self.test_random_user_insert()
        records = view_users(self.conn)
        self.assertFalse(records is None)

    def test_get_table_schema(self):
        schema = get_table_schema(self.conn)
        self.assertFalse(schema is None)

    def test_salted_password_hashing(self):
        password = "Nobody inspects"
        salt = b" the spammish repetition"
        value = salted_password_hashing(password, salt)
        true_val = b'\xf1\x92e(Oo4M\x93\xa81\xe1T\xd6\x92\x04^\x02\xdbi\xb1\xc3\xfd%'b'\xcc\x15\xf0\x83\xdex\xea\xfc'
        self.assertEqual(value, true_val)

    def test_valid_credentials(self):
        self.test_user_insert()
        password = "yllas"
        res = check_user_credentials('sally', password, self.conn)
        self.assertEqual(res, 10)

    def test_invalid_password(self):
        self.test_user_insert()
        password = "wrong"
        res = check_user_credentials('sally', password, self.conn)
        self.assertEqual(res, 11)

    def test_username_not_exist(self):
        password = "Nobody inspects"
        res = check_user_credentials('not_user', password, self.conn)
        self.assertEqual(res, 12)

import sqlite3 as sql
import hashlib
import string
import random
from secrets import token_bytes

connection = sql.connect("users.db")


def execute_users_statement(statement, con=None, fetchone=True, params=None):
    if not con:
        con = connection
    cur = con.cursor()
    if params:
        cur.execute(statement, params)
    else:
        cur.execute(statement)
    if fetchone:
        return cur.fetchone()
    else:
        return cur.fetchall()


def get_table_schema(con=None):
    # [(0, 'login', 'TEXT', 0, None, 1), (1, 'salt', 'BLOB', 0, None, 0), (2, 'hash', 'BLOB', 0, None, 0)]
    statement = "PRAGMA table_info('users')"
    schema = execute_users_statement(statement, con, fetchone=False)
    print(schema)
    return schema


def view_users(con=None):
    statement = "SELECT * FROM users"
    records = execute_users_statement(statement, con, fetchone=False)
    print(records)
    return records


def salted_password_hashing(password, salt):
    encoded_password = password.encode()  # encode to bytes
    hash_obj = hashlib.sha256()
    hash_obj.update(salt)
    hash_obj.update(encoded_password)
    digest = hash_obj.digest()
    print(digest)
    return digest


def get_user_info(login, con=None):
    statement = f"SELECT salt, hash, rowid from users WHERE login= ?"
    user = execute_users_statement(statement, con, fetchone=True, params=(login,))
    return user


def check_user_credentials(login, password, con=None):
    credentials = get_user_info(login, con)
    if not credentials:
        print("User name does not exit!")
        register(login, password, con)
        return 12
    else:
        user_input = salted_password_hashing(password, credentials[0])
        if user_input == credentials[1]:
            print("Welcome")
            return 10
        else:
            print("Password invalid!")
            return 11


def insert_random_user(con=None):
    letters = string.ascii_letters
    login = ''.join(random.choice(letters) for i in range(5))
    salt = token_bytes(16)
    password = ''.join(random.choice(letters) for i in range(10))
    hashed_password = salted_password_hashing(password, salt)
    print(f"Inserting random user login={login}, salt={salt}, password={password}, hashed_password={hashed_password}")
    return insert_user(login, salt, hashed_password, con)


def register(login, password, con=None):
    salt = token_bytes(16)
    hashed_password = salted_password_hashing(password, salt)
    print(f"Register user login={login}, salt={salt}, password={password}, hashed_password={hashed_password}")
    return insert_user(login, salt, hashed_password, con)


def insert_user(login, salt, hashed_password, con=None):
    user = get_user_info(login, con)
    if user is None:
        if not con:
            con = connection
        c = con.cursor()
        salt = sql.Binary(salt)
        hashed_password = sql.Binary(hashed_password)
        c.execute('INSERT INTO users (login, salt, hash) VALUES (?, ?, ?)', (login, salt, hashed_password))
        row_id = c.lastrowid
        print(row_id)
        con.commit()
        return row_id
    else:
        print('user exists')
        print(user)
        return user[2]

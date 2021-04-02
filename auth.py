import sqlite3 as sql
import hashlib
import string
import random


def execute_users_statement(statement, fetchone=True):
    con = sql.connect("users.db")
    cur = con.cursor()
    cur.execute(statement)
    if fetchone:
        return cur.fetchone()
    else:
        return cur.fetchall()


def get_table_schema():
    # [(0, 'login', 'TEXT', 0, None, 1), (1, 'salt', 'BLOB', 0, None, 0), (2, 'hash', 'BLOB', 0, None, 0)]
    statement = "PRAGMA table_info('users')"
    schema = execute_users_statement(statement, fetchone=False)
    print(schema)
    return schema


def view_users():
    statement = "SELECT * FROM users"
    records = execute_users_statement(statement, fetchone=False)
    print(records)
    return records


def salted_password_hashing(password, salt):
    encoded_password = password.encode()  # encode to bytes
    hash_obj = hashlib.sha256()
    hash_obj.update(encoded_password)
    hash_obj.update(salt)
    digest = hash_obj.digest()
    print(digest)
    return digest


def get_user_info(login):
    statement = f"SELECT salt, hash, rowid from users WHERE login='{login}';"
    user = execute_users_statement(statement, fetchone=True)
    return user


def check_user_credentials(login, password):
    credentials = get_user_info(login)
    if not credentials:
        print("User name does not exit!")
        return 0
    else:
        user_input = salted_password_hashing(password, credentials[0])
        if user_input == credentials[1]:
            print("Welcome")
            return 1
        else:
            print("Password invalid!")
            return 11


def insert_random_user():
    letters = string.ascii_letters
    login = ''.join(random.choice(letters) for i in range(5))
    salt = ''.join(random.choice(letters) for i in range(3)).encode()
    password = ''.join(random.choice(letters) for i in range(10))
    hash = salted_password_hashing(password, salt)
    print(f"Inserting random user login={login}, login={salt}, login={password}")
    return  insert_user(login, salt, hash)


def insert_user(login, salt, hash):
    user = get_user_info(login)
    if user is None:
        con = sql.connect("users.db")
        c = con.cursor()
        salt = sql.Binary(salt)
        hash = sql.Binary(hash)
        c.execute('INSERT INTO users (login, salt, hash) VALUES (?, ?, ?)', (login, salt, hash))
        id = c.lastrowid
        print(id)
        con.commit()
        con.close()
        return id
    else:
        print('user exists')
        print(user)
        return user[2]

# Hash kata sandi dan sesi login
import hashlib
import hmac
import secrets

# token -> id user. Disimpan di memori, jadi hilang kalau server dimatikan.
sessions = {}


def hash_password(password):
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000).hex()
    return "pbkdf2$" + salt + "$" + hashed


def check_password(password, stored):
    parts = stored.split("$")
    if len(parts) != 3:
        return False
    salt, hashed = parts[1], parts[2]
    test = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000).hex()
    return hmac.compare_digest(test, hashed)


def create_session(user_id):
    token = secrets.token_urlsafe(32)
    sessions[token] = user_id
    return token


def get_user_id(token):
    return sessions.get(token)


def delete_session(token):
    sessions.pop(token, None)

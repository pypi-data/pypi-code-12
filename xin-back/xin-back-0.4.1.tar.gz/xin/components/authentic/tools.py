import jwt
from passlib.apps import custom_app_context as pwd_context

from .config import SECRET_KEY


def encrypt_password(password):
    return pwd_context.encrypt(password)


def verify_password(password, pwd_hash):
    return pwd_context.verify(password, pwd_hash)


def encode_token(payload):
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode()


def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY)
    except jwt.InvalidTokenError:
        return None

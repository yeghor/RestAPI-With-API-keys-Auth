import jwt
from schemas import UserSchema
from configparser import ConfigParser
import os
def get_jwt_secret_key():
    config = ConfigParser()
    config.read(os.path.join("config.ini"))
    return config.get("General", "secret_key")

def encode_jwt(username: str, expires_at):
    secret_key = get_jwt_secret_key()
    payload = {
        "username": username,
        "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S") 
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")

def decode_jwt(encoded_jwt):
    secret_key = get_jwt_secret_key()
    return jwt.decode(encoded_jwt, secret_key, algorithms=["HS256"])

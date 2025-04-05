import jwt
from schemas import UserSchema

def encode_jwt(username: str, api_key: str):
    payload = {
        "username": username,
    }
    return jwt.encode(payload, api_key, algorithm="HS256")

def decode_jwt(encoded_jwt, api_key):
    jwt.decode(encoded_jwt, api_key, algorithms=["HS256"])
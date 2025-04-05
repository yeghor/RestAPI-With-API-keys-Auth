import jwt
from schemas import UserSchema
def encode_jwt(userinfo: UserSchema):
    payload = {
        "username": userinfo.username,
        "date_joined": userinfo.date_joined,
    }
    encoded = jwt.encode(payload, userinfo.api_key, algorithm="HS256")

def decode_jwt(encoded_jwt, api_key):
    jwt.decode(encoded_jwt, api_key, algorithms=["HS256"])
import uuid
import string 
import secrets

def generate_api_key(salt: str = "") -> str:
    alphabet = string.ascii_letters + string.digits + salt
    random_part =  "".join(secrets.choice(alphabet) for _ in range(32))
    uuid_part = uuid.uuid4().hex
    return random_part + uuid_part

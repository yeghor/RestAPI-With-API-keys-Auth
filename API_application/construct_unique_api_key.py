import uuid
import string 
import secrets

def generate_api_key() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(32)) + str(uuid.uuid1())

print(generate_api_key())
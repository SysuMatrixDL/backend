import hmac
import hashlib
import bcrypt


def generate_user_token(password: str) -> str:
    salt = bcrypt.gensalt()
    # The length of this token is 256 / 4 = 64 bytes
    token = hmac.new(salt, password.encode("utf-8"), hashlib.sha256).hexdigest()
    return token


def generate_sha256_digest(password: str) -> str:
    # The length of this hash value is 256 / 4 = 64 bytes
    sha256_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return sha256_hash

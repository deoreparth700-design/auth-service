import bcrypt

SALT_ROUNDS = 12


async def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=SALT_ROUNDS)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


async def compare_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

import uuid


def generate_random_hash() -> str:
    return uuid.uuid4().hex
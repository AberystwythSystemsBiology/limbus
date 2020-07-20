import uuid

def generate_random_hash() -> str:
    """

    :return:
    """
    return uuid.uuid4().hex

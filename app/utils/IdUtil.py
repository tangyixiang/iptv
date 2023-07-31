import uuid

def get_id():
    return str(uuid.uuid4()).replace('-', '')
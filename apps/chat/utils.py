import uuid

def generate_session_id():
    '''
    生成会话id
    '''
    return str(uuid.uuid4())
mode = 0

INTENT_ENTITY_PORT = 8001
STT_PORT = 8002
CONV_PORT = 8003
QA_PORT = 8004
RETRIEVER_PORT = 8005

# Mode 0: Develop
if mode == 0:
    INTENT_ENTITY_HOST = '0.0.0.0'
    STT_HOST = '0.0.0.0'
    CONV_HOST = '0.0.0.0'
    QA_HOST = '0.0.0.0'
    RETRIEVER_HOST = '0.0.0.0'
    
    API_PATH = {
        "INTENT_ENTITY_URL" : "http://0.0.0.0:8001/bkheart/api/intent_entity_classify",
        "STT_URL" : "http://0.0.0.0:8002/bkheart/api/stt",
        "CONV_URL" : "http://0.0.0.0:8003/bkheart/api/conversation_update",
        "QA_URL" : "http://0.0.0.0:8004/bkheart/api/qa",
        "RETRIEVER_URL": "http://0.0.0.0:8005/bkheart/api/retrieve",
    }

# Mode 1: Deploy
if mode == 1:
    INTENT_ENTITY_HOST = '172.28.10.73'
    STT_HOST = '172.28.10.73'
    CONV_HOST = '172.28.10.73'
    QA_HOST = '172.28.10.73'

    API_PATH = {
        "INTENT_ENTITY_URL" : "https://172.28.10.73:8001/bkheart/api/intent_entity_classify",
        "STT_URL" : "https://172.28.10.73:8002/bkheart/api/stt",
        "CONV_URL" : "https://172.28.10.73:8003/bkheart/api/conversation_update",
        "QA_URL" : "https://172.28.10.73:8004/bkheart/api/qa",
        "RETRIEVER_URL": "http://172.28.10.73:8005/bkheart/api/retrieve",
    }


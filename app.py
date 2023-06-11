import logging
import uvicorn
import requests
from typing import List, Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

from database import Database
from api_url_config import *

INTENT_ENTITY_URL = API_PATH["INTENT_ENTITY_URL"]
STT_URL = API_PATH["STT_URL"]
CONV_URL = API_PATH["CONV_URL"]
QA_URL = API_PATH["QA_URL"]
RETRIEVER_URL = API_PATH["RETRIEVER_URL"]

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database = Database()
manager_list = {}
conversation_id_list = list()

class Text_Request_Item(BaseModel):
    conversation_id: str
    utterance: str


class Speech_Request_Item(BaseModel):
    conversation_id: str
    intent: str
    entity: Dict[str, str]
    utterance: str

class Feedback_Request_Item(BaseModel):
    conversation_id: str

class Response_Item(BaseModel):
    utterance: str
    response: List
    policy_response: str
    start_position: int
    end_position: int
    context: List


@app.post("/bkheart/api/text")
def text_response(Request: Text_Request_Item):
    input_dt = datetime.now(timezone.utc)

    conversation_id = Request.conversation_id
    utterance = Request.utterance

    result = process_text(conversation_id, utterance)
    response = result['response']
    policy_response = result['policy_response']
    start_position = result['start_position']
    end_position = result['end_position']
    context = result['context']
    paragraph_id = result['paragraph_id']
    
    output_dt = datetime.now(timezone.utc)

    update_database(
        input_dt,
        output_dt,
        conversation_id,
        utterance,
        "\n".join(response),
        policy_response,
        None,
        paragraph_id,
        None
    )

    return Response_Item(
        utterance=utterance,
        response=response,
        policy_response=policy_response,
        start_position=start_position,
        end_position=end_position,
        context=context,        
    )


@app.post("/bkheart/api/speech")
async def speech_response(conversation_id: str = Form(), file: UploadFile = File()):
    input_dt = datetime.now(timezone.utc)

    contents = await file.read()

    stt_response = requests.post(
        url=STT_URL,
        files={'file': contents}
    ).json()

    utterance = stt_response['utterance']
    voice_filename = stt_response['voice_filename']

    result = process_text(conversation_id, utterance)
    response = result['response']
    policy_response = result['policy_response']
    start_position = result['start_position']
    end_position = result['end_position']
    context = result['context']
    paragraph_id = result['paragraph_id']
    
    output_dt = datetime.now(timezone.utc)

    update_database(
        input_dt,
        output_dt,
        conversation_id,
        utterance,
        "\n".join(response),
        policy_response,
        None,
        paragraph_id,
        voice_filename
    )

    return Response_Item(
        utterance=utterance,
        response=response,
        policy_response=policy_response,
        start_position=start_position,
        end_position=end_position,
        context=context,        
    )
    
@app.post("/bkheart/api/feedback")
def feedback_response(Request: Feedback_Request_Item):
    raise HTTPException(status_code=501) 



def process_text(conversation_id, utterance):
    # Intent Classification and Named Entity Recognition
    intent_entity_response = requests.post(
        url=INTENT_ENTITY_URL,
        json={'utterance': utterance, 'conversation_id': conversation_id}
    ).json()

    intent=intent_entity_response['intent']
    intent_confidence= intent_entity_response['intent_confidence']
    entity_dict=intent_entity_response['entity_dict']

    # Conversation State Update
    conv_response = requests.post(
        url=CONV_URL,
        json={'conversation_id': conversation_id, 'intent': intent, 'entity_dict': entity_dict, 'utterance': utterance}
    ).json()

    action = conv_response['action']
    response = conv_response['response']
    role = conv_response['role']
    question = conv_response['question']

    start_position = -1
    end_position = -1
    context = []
    policy_response = ""
    paragraph_id = None
    
    # Get Question Answering Result
    if action == 'answering':
        retrieval_response = requests.post(
            url=RETRIEVER_URL,
            json={'role': role, 'question': question}
        ).json()

        context = retrieval_response['context']
        # paragraph_id = retrieval_response['paragraph_id']
        isFAQ = retrieval_response['isFAQ']
        end_position = 0

        if not isFAQ:
            qa_response = requests.post(
                url=QA_URL,
                json={'question': question, 'context': context[0]}
            ).json()

            policy_response = qa_response['text']
            start_position = qa_response['start_position']
            end_position = qa_response['end_position']


    logging.info('Conversation_id: %s', conversation_id)
    logging.info('Utterance: %s', utterance)
    logging.info('Inent: %s', intent)
    logging.info('Entity: %s', entity_dict)
    logging.info('Action: %s', action)
    logging.info('Response: %s', response)
    logging.info('Answer: %s', policy_response)
    
    return {
        'response': response,
        'policy_response': policy_response,
        'start_position': start_position,
        'end_position': end_position,
        'context': context,
        'paragraph_id': paragraph_id,
    }

def update_database(
        input_dt,
        output_dt,
        conversation_id,
        utterance,
        response,
        policy_response,
        voice_id,
        paragraph_id,
        voice_filename=None
    ):
    if conversation_id not in conversation_id_list:
        conversation_id_list.append(conversation_id)
        database.insert_conversation(conversation_id)

    if voice_filename:
        database.insert_voice(voice_filename)
        voice_id = database.get_voiceid()

    database.insert_utterance(voice_id, utterance, True, conversation_id, input_dt, None)
    database.insert_utterance(None, response + '\n' + policy_response, False, conversation_id, output_dt, paragraph_id)


if __name__ == '__main__':
    uvicorn.run("app:app", host='0.0.0.0', port=8000)
    database.close_connection()
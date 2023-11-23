import torch
import openai
import dotenv
import os
import time
import json

from fastapi import APIRouter

from typing import Union
from pydantic import BaseModel

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    AIMessage,
    HumanMessage,
)
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

import asyncio
import os
from typing import AsyncIterable, Awaitable
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.prompts import (
    FewShotChatMessagePromptTemplate,
    ChatPromptTemplate,
)

from databases import Database

## 데베 설정
DATABASE_URL = "mysql+pymysql://root:1234@127.0.0.1:3306/place_classification"
database = Database(DATABASE_URL)


## Open AI 설정
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

key = os.environ["OPENAI_API_KEY"]
openai.api_key = key

from openai import OpenAI
client = OpenAI()

## Fast api 연결
router = APIRouter(
    prefix="/chatbot",
)


## 프롬프트 데이터 가져오기
json_path='chat_data.json'

def connect_json():
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


######################################################
### 퀴즈 생성

class quiz_gen(BaseModel):
    text: str

@router.post("/quiz_gen")
def image_def(input: quiz_gen):
        print(input.text)

        ## json 연결
        json_data=connect_json()["quiz_gen"]

        messages = [
            {"role": "system", "content": json_data["system"]},
            {"role": "user", "content": json_data["input"][0]},
            {"role": "assistant", "content": json_data["output"][0]},
            {"role": "user", "content": json_data["input"][1]},
            {"role": "assistant", "content": json_data["output"][1]},
            {"role": "user", "content": json_data["input"][2]},
            {"role": "assistant", "content": json_data["output"][2]},
            {"role": "user", "content": input.text}
        ]
        try:
            chat_completion = client.chat.completions.create(  ## gpt 오브젝트 생성후 메세지 전달
                model="gpt-4",
                messages=messages,
                temperature=1,
                max_tokens=1000
            )
            result = chat_completion.choices[0].message.content
            output = json.loads(result)
        except Exception as e: #나중에 더미데이터 넣기
            output="{\"error\":\"gpt에러\"}"
            
        print(output)
        return output

######################################################




######################################################
#### 비동기 스트리밍 통신
final_token=""
async def send_message(text: str) -> AsyncIterable[str]:
    final_token=""
    callback = AsyncIteratorCallbackHandler()
    model = ChatOpenAI(
        model_name="gpt-4",
        streaming=True,
        verbose=True,
        callbacks=[callback],
    )

    async def wrap_done(fn: Awaitable, event: asyncio.Event):
        try:
            await fn
        except Exception as e:
            error_message = f"gpt 오류: {e}"
            print(error_message)
        finally:
            event.set()

    ## json 연결
    json_data=connect_json()["make_script"]

    task = asyncio.create_task(wrap_done(
        model.agenerate(messages=[[SystemMessage(content=json_data['system']),HumanMessage(content=json_data['input'][0]),
                                   AIMessage(content=json_data['output'][0]),HumanMessage(content=json_data['input'][1]),
                                   AIMessage(content=json_data['output'][1]),HumanMessage(content=json_data['input'][2]),
                                   AIMessage(content=json_data['output'][2]),  HumanMessage(content=text)]]),
        callback.done),
    )

    n=0
    print("스트리밍 데이터 통신 시작")
    # async for token in callback.aiter():
    #     print(n,end=" ")
    #     n+=1
    #     print(token)
    #     final_token+=token
    #     yield f"data: {token}\n\n"
    # print("출력결과 : ")
    # print(final_token)
    # await task

    error_message=None
    async for token in callback.aiter():
        if error_message:
            yield f"data: {error_message}\n\n"
            break  # 에러가 발생하면 스트리밍 루프 종료
        print(n, end=" ")
        n += 1
        print(token)
        final_token += token
        yield f"data: {token}\n\n"
    print("출력결과 : ")
    print(final_token)
    await task

class StreamRequest(BaseModel):
    text: str


@router.post("/make_script")
def stream(body: StreamRequest):
    print(body.text)
    return StreamingResponse(send_message(body.text), media_type="text/event-stream")
######################################################



######################################################
### 이미지 분류 통신
class Image_connect(BaseModel):
    text: str


@router.post("/image_connect")
async def image_def(input: Image_connect):
    print(input.text)

    ## json 연결
    json_data=connect_json()["image_connect"]

    messages = [
        {"role": "system", "content": json_data["system"]},
        {"role": "user", "content": json_data["input"][0]},
        {"role": "assistant", "content": json_data["output"][0]},
        {"role": "user", "content": input.text}
    ]
    try:
        chat_completion = client.chat.completions.create(  ## gpt 오브젝트 생성후 메세지 전달
            model="gpt-4",
            # model="gpt-4",
            messages=messages,
            temperature=1,
            max_tokens=1000
        )

        result = chat_completion.choices[0].message.content

        query = "INSERT INTO place_table (Q, A) VALUES (:Q, :A)"
        values = {"Q": input.text, "A": result}
        await database.execute(query=query, values=values)
    except Exception as e: #나중에 더미데이터 넣기
        result="gpt 에러"


    print("분류결과 : "+result)
    return {"place" : result}
######################################################


######################################################
### 음악 분류 통신
class Sound_connect(BaseModel):
    text: str


@router.post("/music_connect")
async def Sound_def(input: Sound_connect):
    print(input.text)
    
    ## json 연결
    json_data=connect_json()["music_connect"]

    messages = [
        {"role": "system", "content": json_data['system']},
        {"role": "user", "content": json_data['input'][0]},
        {"role": "assistant", "content": json_data['output'][0]},
        {"role": "user", "content": input.text}
    ]

    try:
        chat_completion = client.chat.completions.create(  ## gpt 오브젝트 생성후 메세지 전달
            model="gpt-4",
            messages=messages,
            temperature=1,
            max_tokens=1000
        )
        
        result = chat_completion.choices[0].message.content


        query = "INSERT INTO bgmusic_table (Q, A) VALUES (:Q, :A)"
        values = {"Q": input.text, "A": result}
        await database.execute(query=query, values=values)
    except Exception as e: #나중에 더미데이터 넣기
        result="gpt 에러"

    print("분류결과 : "+result)
    return {"mood" : result}
######################################################

@router.on_event("startup")
async def startup():
    await database.connect()

@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()
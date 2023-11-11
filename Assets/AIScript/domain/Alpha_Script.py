import torch
import openai
import dotenv
import os
import time

from fastapi import APIRouter

from typing import Union
from pydantic import BaseModel

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
)
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

import asyncio
import os
from typing import AsyncIterable, Awaitable
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler


dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

key = os.environ["OPENAI_API_KEY"]
openai.api_key = key

router = APIRouter(
    prefix="/chatbot",
)


######################################################
#### 비동기 스트리밍 통신
async def send_message(text: str) -> AsyncIterable[str]:

    callback = AsyncIteratorCallbackHandler()
    model = ChatOpenAI(
        model_name="gpt-4",
        streaming=True,
        verbose=True,
        callbacks=[callback],
    )
    
    # 시나리오용
    system_messages= '''
    해당 텍스트는 사용자의 경험담이야. 이 이야기로 약 60초 이내의 임팩트 있는 정보전달 목적의 영상을 만들거야.
    1.500자 이내로 쉽게 대학생 말투와 반말로 대본을 만들어줘.
    2.사용자는 상체만 나오고 소품을 활용하지 않아.
    3.행동은 3개 이내로 괄호()안에 지시어로 작성해줘.
    4.영상 제목, 오프닝, 내용, 결론 순으로 작성해줘.
    5.영어로 말한 경우는 영어로 답변해줘.
    6.한 문장이 끝날때 마다 "|"이 기호로 표현해줘
    7.보낼때 따옴표 표시를 없애서 보내줘
    '''

    # ## 테스트용
    # system_messages="10글자 이내로 답해줘"


    async def wrap_done(fn: Awaitable, event: asyncio.Event):
        try:
            await fn
        except Exception as e:
            print(f"Caught exception: {e}")
        finally:
            # Signal the aiter to stop.
            event.set()

    # Begin a task that runs in the background.
    task = asyncio.create_task(wrap_done(
        model.agenerate(messages=[[SystemMessage(content=system_messages),HumanMessage(content=text)]]),
        callback.done),
    )

    n=0
    async for token in callback.aiter():
        print(n,end=" ")
        n+=1
        print(token)
        
        yield f"data: {token}\n\n"

    await task


class StreamRequest(BaseModel):
    """Request body for streaming."""
    text: str


@router.post("/test_text")
def stream(body: StreamRequest):
    print(body.text)
    return StreamingResponse(send_message(body.text), media_type="text/event-stream")
######################################################



######################################################
### 이미지 분류 통신
class Image_connect(BaseModel):
    text: str


@router.post("/image_connect")
def image_def(input: Image_connect):
    print(input.text)

    system = '''
        장소 = {"Home","Library","University Campus","University Classroom","Park","Office"}
        1. 사용자의 시나리오를 보고 알려준 장소 중 1가지로 분류해줘
        2. 보기에 해당되지 않는 경우, 실외라면 "Park", 실내라면 "Home"으로 분류해줘.
        3. 장소에 해당되지 않는 입력이면 "Home"으로 분류해줘
        4. 입력이 없으면 "Home"만 나타내줘
        5. 출력으로는 장소만 나타내줘 
        
        '''
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": ""},
        {"role": "assistant", "content": "Home"},
        {"role": "user", "content": input.text}
    ]

    chat_completion = openai.ChatCompletion.create(  ## gpt 오브젝트 생성후 메세지 전달
        model="gpt-4",
        # model="gpt-4",
        messages=messages,
        temperature=1,
        max_tokens=1000
    )
    
    result = chat_completion.choices[0].message.content
    print("분류결과 : "+result)
    return {"Place" : result}
######################################################


######################################################
### 음악 분류 통신
class Sound_connect(BaseModel):
    text: str


@router.post("/music_connect")
def Sound_def(input: Sound_connect):
    print(input.text)

    system = '''
        장소 = {"Chill","Cool","Dramatic","Happy","Mysterious","Peaceful","Sad","Serious"}
        1. 사용자의 시나리오를 보고 알려준 시나리오의 무드 중 1가지로 분류해줘
        2. 무드를 분류할 수 없는 입력이면 "Peaceful"으로 분류해줘
        3. 입력이 없으면 "Peaceful"만 나타내줘
        5. 출력으로는 Mood만 나타내줘 
        
        '''
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": ""},
        {"role": "assistant", "content": "Peaceful"},
        {"role": "user", "content": input.text}
    ]

    chat_completion = openai.ChatCompletion.create(  ## gpt 오브젝트 생성후 메세지 전달
        model="gpt-4",
        # model="gpt-4",
        messages=messages,
        temperature=1,
        max_tokens=1000
    )
    
    result = chat_completion.choices[0].message.content
    print("분류결과 : "+result)
    return {"Mood" : result}
######################################################
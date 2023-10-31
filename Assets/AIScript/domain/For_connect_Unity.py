from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Response
from starlette.responses import FileResponse
from pathlib import Path
from typing import Union
from pydantic import BaseModel
from domain.sd_test_NR import loc_cls,make_image

import json
import re

import openai
import dotenv
import os


dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

key = os.environ["OPENAI_API_KEY"]
openai.api_key = key


router = APIRouter(
    prefix="/chatbot",
)



class Text(BaseModel):
    text: Union[str, None] = None

@router.post("/test_text")
def test(item: Text):
    text = item.dict()['text']
    print(text)

    system='''
    해당 텍스트는 사용자의 경험담이야. 이 이야기로 다수에게 전하는 약 60초 이내의 임팩트 있는 정보전달 목적의 영상을 만들거야.
    1.400자 이내로 쉽게 학생 말투와 반말로 대본을 만들어줘.
    2.사용자는 상체만 나오고 소품을 활용하지 않아. 댓글도 쓰지 않아.
    3.행동은 3개 이내로 괄호()안에 지시어로 작성해줘.
    4.영상 제목, 오프닝, 내용, 결론으로 나눠서 작성해줘
    5.영어로 말한 경우는 영어로, 한글로 말한 경우는 한글로 작성해줘.
    '''
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": text}
    ]

    chat_completion = openai.ChatCompletion.create( ## gpt 오브젝트 생성후 메세지 전달
        # model="gpt-3.5-turbo",
        model="gpt-4",
        messages=messages,
        temperature=1,
        max_tokens=1000
    )

    result = chat_completion.choices[0].message.content
    print(result)

    return result

@router.post("/test_image")
def test_image(item: Text):
    text = item.dict()['text']
    # print(text)

    if os.path.isfile('images/test.jpg'):
        os.remove('images/test.jpg')

    location = loc_cls(text)            # 장소를 분류함
    print(location)
    image_path = make_image(location)

    return FileResponse(image_path)
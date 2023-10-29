from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Response
from starlette.responses import FileResponse
from pathlib import Path
from typing import Union
from pydantic import BaseModel

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
    약 60초간의 짧은 임팩트 있는 정보전달 목적의 영상을 만들거야. 사용자가 겪은 경험을 간결하고 임팩트 있게 전달할 수 있도록 대본을 만들어줘.
    1.영어로 말한 경우는 번역을 하고, 다음 조건에 맞춰서 말해줘
    2.행동의 경우 괄호()안에 써서 제시해줘
    3.영상 제목, 오프닝, 내용, 결론 순으로 작성해줘
    4.다른 사람에게 편하게 말하듯이 반말로 작성해줘.
    5.영어로 말한 경우는 영어로 답변해줘.
    '''
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": text}
    ]

    chat_completion = openai.ChatCompletion.create( ## gpt 오브젝트 생성후 메세지 전달
    model="gpt-3.5-turbo", 
    messages=messages,
    temperature=1,
    max_tokens=1000
    )

    result = chat_completion.choices[0].message.content


    return result

@router.post("/test_image")
def test_image(item: Text):
    text = item.dict()['text']
    print(text)

    return FileResponse("warawara.jpg")\


@router.post("/send_image/")
async def send_image(request_str: str):
    if request_str == "말":
        image_path = Path("../images/말.jpg")  # 이미지 파일 경로
        if image_path.is_file():
            return FileResponse(image_path)
        else:
            raise HTTPException(status_code=500, detail="이미지를 찾을 수 없습니다.")
    else:
        raise HTTPException(status_code=400, detail="해당하는 이미지를 찾을 수 없습니다.")


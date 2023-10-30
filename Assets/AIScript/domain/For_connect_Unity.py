from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Response
from starlette.responses import FileResponse
from pathlib import Path
from typing import Union
from pydantic import BaseModel
from sd_test.sd_test_NR import loc_cls, make_image

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
    해당 텍스트는 사용자의 경험담이야. 이 이야기로 약 60초 이내의 임팩트 있는 정보전달 목적의 영상을 만들거야.
    1.500자 이내로 쉽게 대학생 말투와 반말로 대본을 만들어줘.
    2.사용자는 상체만 나오고 소품을 활용하지 않아.
    3.행동은 3개 이내로 괄호()안에 지시어로 작성해줘.
    4.영상 제목, 오프닝, 내용, 결론 순으로 작성해줘.
    5.영어로 말한 경우는 영어로 답변해줘.
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
    print(text)

    # location = loc_cls(text)            # 장소를 분류함
    # image = make_image(location)        # image를 images/test.jpg로 저장함.

    return FileResponse("images/test.jpg")


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


from fastapi import APIRouter
import os
import dotenv
from pydantic import BaseModel
import openai
from openai import OpenAI
import deepl


## DeepL 설정
deepl_key = os.environ["DEEPL_API_KEY"]
auth_key = deepl_key
translator = deepl.Translator(auth_key)

## Open AI 설정
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

key = os.environ["OPENAI_API_KEY"]
openai.api_key = key

client = OpenAI()

## Fast api 연결
router = APIRouter(
    prefix="/chat_translate",
)

class Text(BaseModel):
    lang: str
    text: str
@router.post("/chat")
def translate_def(input: Text):
    print(f'채팅 받았당: {input.text}')
    if input.lang == 'KO':
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "USER 문장을 다음 조건에 따라 영어로 번역해줘.\n1. 신조어를 찾아 쌍따옴표(\")로 표현해줘.\n2.신조어를 제외하고 문장을 번역해줘.\n3.신조어는 한글 발음대로 표현해줘.\n"
                },
                {
                    "role": "user",
                    "content": "역시 겨울은 아아지"
                },
                {
                    "role": "assistant",
                    "content": "After all, it's an \"ah-ah\" in the winter."
                },
                {
                    "role": "user",
                    "content": f"{input.text}"
                }
            ],
            temperature=1,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        result = response.choices[0].message.content
        print(f'한국어 번역했당: {result}')
    else:
        translate_text = translator.translate_text(input.text, target_lang="KO")
        print(f"영어 번역했당: {translate_text}")

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "User의 문장을 반말로 자연스럽게 바꿔줘"
                },
                {
                    "role": "user",
                    "content": f"{translate_text}"
                }
            ],
            temperature=1,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        result = response.choices[0].message.content
        print(f"영어 반말로 바꿨당: {result}")

    return {"output":result}
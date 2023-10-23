from fastapi import APIRouter
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


class Chat(BaseModel):
    user_input: Union[str, None] = None


@router.post("/chat")
def chat(item: Chat):

    user_input = item.dict()['user_input']

    system_text='''
        약 60초간의 짧은 임팩트 있는 정보전달 목적의 영상을 만들거야. 사용자가 겪은 경험을 간결하고 임팩트 있게 전달할 수 있도록 대본을 만들어줘.
        1. 행동의 경우 괄호()안에 써서 제시해줘
        2. 영상 제목, 오프닝, 내용, 결론 순으로 작성해줘
        3. 다른 사람에게 편하게 말하듯이 반말로 작성해줘.
    '''

    pre_input = '''
        내가 어제 새로운 말을 배웠어. 어제 누가 나보고 발이 넓다고 하는거야 나는 발이 남들보다 작은데 말이야 그 말을 처음에 이해하지 못했어 그런데 친구가 많다는 말이래 신기하지 않아?
    '''

    pre_output ='''
    영상 제목: "이런 신기한 속담도 있었네?"
    오프닝:(활기찬 모습으로) 안녕! 오늘 말하고 싶은 이야기가 생겨서 왔어. 바로 어제 나한테 생긴 신기한 경험에 대해서 말해볼게!
    내용:(생각하는 표정으로) 어제, 누군가 나에게 아주 이상한 말을 던졌어: "너 발이 넓다". 발이 작은 나는 이 말을 이해하지 못했지! 그치만, 알고보니 그게 단순히 친구가 많다는 뜻이라니! (놀라는 표정으로) 이런 아주 신기한 속담이 있었다니! 나, 평생 동안 상상도 못했었어. 
    결론:(웃으며) 이제부터 나는 "발이 넓다"고 했을 때, 그게 내가 많은 사람들과 괜찮은 관계를 갖고 있다는 속담의 하나라는 걸 알게될 거야. 일상 속에서 흔히 사용되는 말들 중에 어떤 깊은 뜻이 숨어있는지 모르니까, 새로운 것을 알게 되는건 정말 재밌어. 공부하는건 정말 재미있는일이야!
    '''


    messages=[
            {"role": "system", "content": system_text},
            {"role": "user", "content": pre_input},
            {"role": "assistant", "content": pre_output},
            {"role": "user", "content": user_input},
            
        ]

    chat_completion = openai.ChatCompletion.create( ## gpt 오브젝트 생성후 메세지 전달
    model="gpt-3.5-turbo", 
    messages=messages,
    temperature=1,
    max_tokens=1000
    )

    result = chat_completion.choices[0].message.content
    changed_result = re.sub(r'\\|\n', '', result)

    print(result)
    print("변경후")
    print(changed_result)
    

    return { "output" : changed_result }
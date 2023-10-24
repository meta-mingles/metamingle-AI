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


# 대본 작성 수정본
class Other_chat(BaseModel):
    other_user_input: Union[str, None] = None

@router.post("/other_chat")
def chat(item: Other_chat):

    user_input = item.dict()['other_user_input']

    system_text='''
        약 60초간의 짧은 임팩트 있는 정보전달 목적의 영상을 만들거야. 
        사용자가 겪은 경험을 간결하고 임팩트 있게 전달할 수 있도록 유투브 쇼츠 대본을 만들어줘.  흥미를 돋구는 말투로 재밌게 써 줘.

        1. 사용자가 움직이는 몸의 행동의 경우 괄호()안에 써서 제시해줘
        2. 영상 제목, 오프닝, 내용, 결론 순으로 작성해줘, 출력은 모두 감싸서 content로 줘야돼
        3. 자신감 있고 캐주얼한 말투로 주제에 대한 정보를 반말로 작성해줘
        4. 마지막으로 이 영상을 어디서 찍으면 좋을지 장소를 한 단어로 알려줘
        5. 출력할때 내용은 content 장소는 place에 매칭해서 json 형태로 만들어줘
    '''

    pre_input = '''
        내가 어제 새로운 말을 배웠어. 어제 누가 나보고 발이 넓다고 하는거야 나는 발이 남들보다 작은데 말이야 그 말을 처음에 이해하지 못했어 그런데 친구가 많다는 말이래 신기하지 않아?
    '''

    pre_output ='''
        {
        "content": {
            "영상 제목": "【미스터리 한국어】'발이 넓다' 뜻 알고 있었니?",
            "오프닝": "(카메라를 향해 미소 날리며) 이봐, 여기 좋은 이야기 들어봤니? 오늘 한 말에서 배운 새로운 표현 하나 소개해줄게.",
            "내용": "(두 손을 펼치며) '발이 넓다니?' 엥? 나한테? 아니, 나는 웬만한 사람보다 발이 작거든. 그게 무슨 말이야? (책을 넘기는 척) 그런데 여기서 꿀팁! '발이 넓다'란 말은 사실은 발 사이즈랑 전혀 상관 없어! 친구가 많다는 걸 의미하는 거래. 고마운 내 친구가 가르쳐줬어. 신기하지 않아?",
            "결론": "(큰 소리로) 그래서 요즘 내 스타일은 발이 아주~ 넓어지는 중! 그래서 너도 오늘부터 발을 넓혀봐. 어플로 친구 추가, SNS에 좋아요 누르고 새 친구들 만나기. 널 넓은 세상으로 초대할게. (카메라를 향해 손짓) 이번 영상이 좋았다면, 구독하고 좋아요 버튼 꾹 눌러줘! 다음 영상에서 만나자, 바이바이~"
        },
        "place": "서점"
        }
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
    max_tokens=1000,
    frequency_penalty=0.6
    )

    result = chat_completion.choices[0].message.content



    json_data = json.loads(result)
    chaged_result =json.dumps(json_data, indent=4, ensure_ascii=False)
    
    print(chaged_result)

    return chaged_result 
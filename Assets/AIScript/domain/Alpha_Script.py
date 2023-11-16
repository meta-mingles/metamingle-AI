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



dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

key = os.environ["OPENAI_API_KEY"]
openai.api_key = key

router = APIRouter(
    prefix="/chatbot",
)


######################################################
### 퀴즈 생성
class quiz_gen(BaseModel):
    text: str


@router.post("/quiz_gen")
def image_def(input: quiz_gen):
    print(input.text)

    system = '''
        사용자는 A이고 퀴즈를 보는 사람들은 B이야.
        사용자의 이야기를 듣고 한 가지 재치있는 퀴즈를 만들어줘
        1. 퀴즈는 사용자에 집중하지 않고 장소, 상황에 집중해서 문제를 내줘
        2. 퀴즈를 맞추는 사람은 사용자의 이야기를 모르고 있어
        3. 퀴즈를 맞추는 사람이 모를만한 사용자의 개인적인 경험은 퀴즈로 내지마
        4. 퀴즈는 질문만 알려줘
        5.한국어로 퀴즈를 알려주고 줄 바꿈 후  영어로 알려줘
        6. 퀴즈를 맞추는 사람이 유추 할 수 있으면 문제를 제공해
        7.퀴즈를 맞추는 사람이  유추 할 수 없으면 "Noquiz" 고 말해
        '''
    
    input1='''
    I ate yesterday
    '''
    output1='''
    Noquiz
    '''
    input2='''
    나는 어제 놀이동산에서 놀았는데 츄러스가 맛있더라 놀이동산에서는 츄러스를 꼭 먹어야지
    '''
    output2='''
    한국어 : 놀이동산에서 가장 대표적인 간식은 무엇일까요?

    English : What is the most representative snack in the amusement park?
    '''
    input3='''
    내가 어제 새로운 말을 배웠어. 어제 누가 나보고 발이 넓다고 하는거야 나는 발이 남들보다 작은데 말이야 그 말을 처음에 이해하지 못했어 그런데 친구가 많다는 말이래 신기하지 않아?
    '''
    output3='''
    한국어 : '발이 넓다'라는 표현은 무슨 뜻일까요?

    English : What does the expression 'having a wide foot' mean?
    '''

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": input1},
        {"role": "assistant", "content": output1},
        {"role": "user", "content": input2},
        {"role": "assistant", "content": output2},
        {"role": "user", "content": input3},
        {"role": "assistant", "content": output3},
        {"role": "user", "content": input.text}
    ]

    chat_completion = openai.ChatCompletion.create(  ## gpt 오브젝트 생성후 메세지 전달
        model="gpt-4",
        messages=messages,
        temperature=1,
        max_tokens=1000
    )
    
    result = chat_completion.choices[0].message.content
    print("퀴즈 생성 결과 : "+result)
    return {"Quiz" : result}
######################################################



final_token=""
######################################################
#### 비동기 스트리밍 통신
async def send_message(text: str) -> AsyncIterable[str]:
    final_token=""
    callback = AsyncIteratorCallbackHandler()
    model = ChatOpenAI(
        model_name="gpt-4",
        streaming=True,
        verbose=True,
        callbacks=[callback],
    )
    
    # 시나리오용
    system_messages= '''
    해당 텍스트는 사용자의 경험담이야. 이 이야기로 약 60초 이내의 임팩트 있는 영상을 만들거야.
    1.500자 이내로 쉽게 대학생 말투와 반말로 대본을 만들어줘.
    1-1. 자기자신을 대학생이라고 소개하지 마
    2.사용자는 상체만 나오고 소품을 활용하지 않아.
    3.행동은 3개 이내로 괄호()안에 지시어로 작성해줘.
    3.한 문장이 끝날때 마다 "|"이 기호로 표현해줘
    4. 좋아요와 구독,댓글 관련된 이야기는 말하지마
    5. 사용자의 입력이 영어인지 한국어인지 판단후 다음의 순서를 따라가줘
    6. 사용자의 입력이 한국어일때
    6-1.한국어로 말한 경우 영상 제목, 오프닝, 내용, 결론 순으로 한국어로 답변해줘
    6-2. 만약 사용자의 입력이 한국어 이고 시나리오로 변환하기 어렵다면 "시나리오를 생성하기 위해 더 다양한 이야기를 해주세요"라는 답변을 보내줘
    7. 사용자의 입력이 영어일때
    7-1.영어로 말한경우 Video title, opening, content, conclusion 순으로 영어로 답변해줘
    7-2.만약 사용자의 입력이 영어 이고 시나리오로 변환하기 어렵다면 "Please tell me more diverse stories to create scenarios"라는 답변을 보내줘
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
    
    few_shot_input1 = '''
        내가 외국에서 자주듣는말이 있어
        1. BTS알아?
        2. 북한이야 남한이야?
        3. 나 김치알아
        이렇게 있는데 이 세가지로 쇼츠 대본을 만들어줘
    '''
    few_shot_output1='''
    제목: "외국에서 BTS와 김치 얘기, 대체 왜?"|

    오프닝:|
    (작은 웃음으로 카메라를 바라봄)|
    "안녕? 난 대학생이야." |
    (손가락 세 개를 펼치면서)|
    "오늘 나랑 함께 외국에서 맨날 듣는 세 가지 말에 대해 이야기해 볼까?" | 

    내용:|
    (한 손으로 1의 동작을 하며)|
    "첫번째, 'BTS 알아?' 요즘 외국에서 젤 많이 듣는 말이지." |
    "한국인 보면 만나는 사람마다 다 BTS을 물어봐." |
    "이게 왜인지 알아?" |
    "한류의 위력이야. 인터넷 세상에서 BTS는 상상을 벗어난 인기를 얻고 있어." |

    (한 손으로 2의 동작을 하며)|
    "두번째, '북한이야 남한이야?' 내가 한국인인걸 알아차렸다면, 이게 바로 다음 질문이지." |
    "대체 왜 북한과 남한을 따지는 건지... 사실 나도 몰라." |
    "아마 북한과 남한이 다르다는 것을 알고 있긴 하지만 그게 어떤 건지 확실히 모르는 거 같아." | 

    (한 손으로 3의 동작을 하며)|
    "마지막, '나 김치 알아.' 아, 이게 진짜 웃겨." |
    "처음엔 좀 놀랐지만 이제 이 말에 익숙해졌어." |
    "다들 한국 음식에 대해 어느 정도 알고 있다는 것을 인정받고 싶은 거 같아." |

    결론 :|
    "그래서 이 세 가지 말을 외국에서 자주 듣는 것에 대해 어떻게 생각해?" |
    "그냥 웃기고 흥미로운 경험이야. 내가 한국인이라는 사실에 더 자부심을 가지게 해." |
    "이런 일화들을 통해 나도 스스로를 재검토하고 세상을 더 폭넓게 볼 수 있는 기회가 되더라고." |
    (일어나며, 카메라로 손을 흔듬) |
    "그럼 다음에 또 이런 이야기로 찾아올게. 바이바이~!"
    '''


    few_shot_input2='''
    하하하
    '''
    few_shot_output2='''
    시나리오를 생성하기 위해 더 다양한 이야기를 해주세요
    '''

    few_shot_input3='''
    빼빼로 데이가 사실 마케팅 전략이였대, 나는 우리나라의 긴 역사가 있는 날인 줄 알았는데 속은 느낌이야! 내 친구는 가래떡 데이라고 하던데 너희는 빼뺴로랑 가래떡중에 어떤걸 받고싶니?
    '''
    few_shot_output3='''
    제목: "빼빼로 데이 vs 가래떡 데이, 너는 어떤 걸 받고 싶어?"|

    오프닝:|
    (손가락으로 빼빼로 모양을 그리며)|
    "오늘은 빼빼로 데이에 대해서 이야기해봐야겠어." |

    내용:|
    (잠시 생각하는 척하며)|
    "너도 알겠지만, 사실 빼빼로 데이는 마케팅 전략이었어." |
    "우리나라의 긴 역사가 있는 날인줄 알았는데, 알고 보니 마케팅 전략이라니, 속은 느낌이지?" |
    (웃으며)|
    "그런데 내 친구가 가래떡 데이라는 걸 말하더라고." |

    (잠시 생각하는 척하며)|
    "그래서 생각해봤어. 빼빼로 데이와 가래떡 데이, 사실 둘 다 마음을 전하는 날이잖아?" |
    "그럼 너는 빼빼로와 가래떡, 어떤 걸 받고 싶을까?" |

    결론 :|
    (카메라를 바라보며 미소)|
    "나는 아직 고민 중이야. 빼빼로도 좋고 가래떡도 좋아." |
    "그런데 가래떡 데이라는 건 처음 들어봐서, 이번엔 가래떡 데이를 즐겨볼까 생각중이야." |
    (카메라로 손을 흔듬)|
    "그럼 너는 어떤 걸 받고 싶어? 그럼 다음에 또 만나. 바이바이~!"
    '''


    # Begin a task that runs in the background.
    task = asyncio.create_task(wrap_done(
        model.agenerate(messages=[[SystemMessage(content=system_messages),HumanMessage(content=few_shot_input1),
                                   AIMessage(content=few_shot_output1),HumanMessage(content=few_shot_input2),
                                   AIMessage(content=few_shot_output2),HumanMessage(content=few_shot_input3),
                                   AIMessage(content=few_shot_output3),  HumanMessage(content=text)]]),
        callback.done),
    )



    n=0
    async for token in callback.aiter():
        print(n,end=" ")
        n+=1
        print(token)
        final_token+=token
        yield f"data: {token}\n\n"
    print("출력결과 : ")
    print(final_token)
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
        장소 = {"home","library","Campus","classroom","park","office"}
        1. 사용자의 시나리오를 보고 알려준 장소 중 1가지로 분류해줘
        2. 보기에 해당되지 않는 경우, 실외라면 "park", 실내라면 "home"으로 분류해줘.
        3. 장소에 해당되지 않는 입력이면 "home"으로 분류해줘
        4. 입력이 없으면 "home"만 나타내줘
        5. 출력으로는 장소만 나타내줘 
        
        '''
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": ""},
        {"role": "assistant", "content": "home"},
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
    return {"place" : result}
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
    return {"mood" : result}
######################################################
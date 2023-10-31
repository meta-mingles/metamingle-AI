from diffusers import DiffusionPipeline
import torch
import openai
import dotenv
import os

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

key = os.environ["OPENAI_API_KEY"]
openai.api_key = key

from PIL import Image
import io

torch.cuda.set_device(1)


def loc_cls(text):
    system = '''
        장소 = ["Home","Library","University Campus","University Classroom","Park","Office","Coffee Shop","Restaurant"]
        사용자의 시나리오에 맞는 장소를 분류해줘. 위의 보기에 없는 경우, 실외라면 "Park", 실내라면 "Home"으로 분류해줘. 리스트의 한 요소를 스트링으로 출력해줘
        '''
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": text}
    ]

    chat_completion = openai.ChatCompletion.create(  ## gpt 오브젝트 생성후 메세지 전달
        # model="gpt-3.5-turbo",
        model="gpt-4",
        messages=messages,
        temperature=1,
        max_tokens=1000
    )

    result = chat_completion.choices[0].message.content
    print("분류결과 : " + result)
    return result


def make_image(location):
    pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0",
                                             torch_dtype=torch.float16, use_safetensors=True,
                                             variant="fp16")
    pipe.to("cuda")

    prompt = f"a photo of {location}, background, color, landscape, no people"
    negative_prompt = "tree,people,letter"

    image = pipe(prompt=prompt,
                 negative_prompt=negative_prompt,
                 guidance_scale=10.0).images[0]

    image_path = "images/test.jpg"
    image.save(image_path)

    print("이미지를 저장했습니다.")

    return image_path


if __name__ == "__main__":
    text = "제목: \"[발이 넓다]를 아시나요?\"\n오프닝: (멋진 표정으로 카메라를 바라봄) \n\"안녕, 친구들~! 오늘은 나랑 같이 신기한 말 하나 알아가자고!\"\n \n내용: (화면 가까이 앉음)\n\"어제, 학교에서 친구가 내게 '너 발이 넓다'라고 말했어. 나흘 보며 그게 뭔 소리야, 내 발이 작은데? 이런 생각이 딱 들었지. (깜짝 놀란 표정)\"\n\n(전신이 보이지 않게 다시 앉기)\n\"하지만 그게 자기 발 사이즈 얘기가 아니라, 아는 사람이 많다는 말이래. (썸네일용 포즈로 손가락으로 'V'자를 만듦) 신기하지 않아?\"\n\n결론:\n\"다음에 누가 발이 넓다고 하면, 착각하지 말고 자신있게 봐라고 말해줘! 오늘도 함께 관심사를 넓혀줘서 고마워. 그럼 다음 영상에서 만나. 안녕~!\" (화면을 쓸어내리며 인사)\n"
    location = loc_cls(text)
    image = make_image(location)
    print(image)
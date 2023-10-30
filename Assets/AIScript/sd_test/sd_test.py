from diffusers import DiffusionPipeline
import torch

from PIL import Image
import io

pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0",
                                         torch_dtype=torch.float16, use_safetensors=True,
                                         variant="fp16")
pipe.to("cuda")

prompt_list=[
    "a photo of park, background,color,landscape, no people",
    "a photo of From front Amusement Park Square, anim , background,no people,no letter",
    "a photo of From a university campus, no people",
    "a photo of university classroom",
    "a photo of my home",
    "a photo of Library",
]

negative_prompt="tree,people,letter"

image = pipe(prompt=prompt_list,
             negative_prompt=negative_prompt,
             guidance_scale =10.0).images[0]


image = pipe(prompt=prompt_list).images[0]
image.save("astronaut_rides_horse.png")

# print(type(images))

# pil_image = Image.fromarray(images)
# output_path = "output_image.jpg"
# pil_image.save(output_path)
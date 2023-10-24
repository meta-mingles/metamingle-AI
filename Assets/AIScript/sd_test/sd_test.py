from diffusers import DiffusionPipeline
import torch

from PIL import Image
import io

pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0",
                                          torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
pipe.to("cuda")

# if using torch < 2.0
# pipe.enable_xformers_memory_efficient_attention()

prompt = "An astronaut riding a green horse"

image = pipe(prompt=prompt).images[0]
image.save("astronaut_rides_horse.png")

# print(type(images))

# pil_image = Image.fromarray(images)
# output_path = "output_image.jpg"
# pil_image.save(output_path)
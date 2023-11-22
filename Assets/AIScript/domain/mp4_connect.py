from fastapi import FastAPI, File, UploadFile,Depends,Form
from fastapi.responses import StreamingResponse
import io
import shutil
import os
from zipfile import ZipFile

from fastapi import APIRouter
from fastapi import FastAPI, File, UploadFile
from typing import Union
from pydantic import BaseModel
from domain.add_script_mp4s import make_mp4s
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/mp4",
)

class def_filename(BaseModel):
    file_uuid: str

@router.post("/en_script_video/")
# async def process_video(file: UploadFile = File(...), file_class: def_filename = Depends()): ##file_class json으로 받기
#     file_n=file_class.file_uuid
####### 테스트용
async def process_video(file: UploadFile = File(...), file_uuid: str = Form(...)):
    file_n=file_uuid

#######

    save_folder = "pre_mp4"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    file_location = f"{save_folder}/{file_n}.mp4"

    # 파일 시스템에 파일 쓰기
    with open(file_location, "wb") as data:
        shutil.copyfileobj(file.file, data)
    
    language="en"
    real_filename=make_mp4s(file_location,file_n,language)

    sand_folder="post_mp4"
    send_file_location = f"{sand_folder}/{real_filename}"

    return FileResponse(path=send_file_location, media_type="video/mp4")

    ## 이전 바이트 통신
    # with open(send_file_location, "rb") as data:
    #     return StreamingResponse(io.BytesIO(data.read()), media_type=file.content_type)



@router.post("/kr_script_video/")
async def process_video(file_class: def_filename):

    file_n=f"{file_class.file_uuid}"
    
    save_folder = "pre_mp4"
    
    file_location = f"{save_folder}/{file_n}.mp4"
    
    language="kr"
    real_filename=make_mp4s(file_location,file_n,language)

    sand_folder="post_mp4"
    send_file_location = f"{sand_folder}/{real_filename}"
    print("경로확인")
    print(real_filename)
    print(send_file_location)
    
    with open(send_file_location, "rb") as video_file:
        video_stream = io.BytesIO(video_file.read())
        return StreamingResponse(video_stream, media_type="video/mp4")

    # def iterfile():  
    #     with open(send_file_location, mode="rb") as file_like:  
    #         yield from file_like  

    # return StreamingResponse(iterfile(), media_type="video/mp4")
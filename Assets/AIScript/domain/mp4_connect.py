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
from domain.modify_add_script_mp4s import modify_make_mp4s
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/mp4",
)

@router.post("/en_script_video")
async def process_video(file: UploadFile = File(...), file_uuid: str = Form(...)):
    
    file_n=file_uuid
    print("연결됨")

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

    with open(send_file_location, "rb") as data:
        return StreamingResponse(io.BytesIO(data.read()), media_type=file.content_type)

@router.post("/kr_script_video/")
async def process_video(file_uuid: str = Form(...)):

    file_n=file_uuid
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
        return StreamingResponse(io.BytesIO(video_file.read()), media_type="video/mp4")
    
@router.post("/modi_kr_script_video")
# async def process_video(file_class: def_filename):
async def process_video(file_uuid: str = Form(...)):

    file_n=file_uuid
    save_folder = "pre_mp4"
    
    file_location = f"{save_folder}/{file_n}.mp4"
    
    language="kr"
    real_filename=modify_make_mp4s(file_location,file_n,language)

    sand_folder="post_mp4"
    send_file_location = f"{sand_folder}/{real_filename}"
    print("경로확인")
    print(real_filename)
    print(send_file_location)
    
    with open(send_file_location, "rb") as video_file:
        return StreamingResponse(io.BytesIO(video_file.read()), media_type="video/mp4")
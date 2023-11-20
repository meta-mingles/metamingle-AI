from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import io
import shutil
import os

from fastapi import APIRouter
from fastapi import FastAPI, File, UploadFile
from typing import Union
from pydantic import BaseModel
from domain.add_script_mp4s import make_mp4s

router = APIRouter(
    prefix="/mp4",
)


@router.post("/process-video/")
async def process_video(file: UploadFile = File(...)):

    save_folder = "pre_mp4"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    file_location = f"{save_folder}/{file.filename}"

    # 파일 시스템에 파일 쓰기
    with open(file_location, "wb") as data:
        shutil.copyfileobj(file.file, data)

    make_mp4s(file_location,file.filename)
    return StreamingResponse(io.BytesIO(await file.read()), media_type=file.content_type)
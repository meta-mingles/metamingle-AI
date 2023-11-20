# fastAPI 실행 코드
# python -m uvicorn main:app --reload
# python -m uvicorn main:app --reload --host=0.0.0.0 --port=8011

from typing import Union

from fastapi import FastAPI
#dsds
from domain import Alpha_Script,mp4_connect

app = FastAPI()

app.include_router(Alpha_Script.router)
app.include_router(mp4_connect.router)
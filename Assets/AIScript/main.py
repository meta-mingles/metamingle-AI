# fastAPI 실행 코드
# python -m uvicorn main:app --reload
# python -m uvicorn main:app --reload --host=0.0.0.0 --port=8000

from typing import Union

from fastapi import FastAPI
#dsds
from domain import Make_script

app = FastAPI()

app.include_router(Make_script.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

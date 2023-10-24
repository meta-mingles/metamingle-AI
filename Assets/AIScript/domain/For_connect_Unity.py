from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Response
from starlette.responses import FileResponse
from pathlib import Path

router = APIRouter(
    prefix="/unity_connect",
)


@router.post("/send_image/")
async def send_image(request_str: str):
    if request_str == "말":
        image_path = Path("../images/말.jpg")  # 이미지 파일 경로
        if image_path.is_file():
            return FileResponse(image_path)
        else:
            raise HTTPException(status_code=500, detail="이미지를 찾을 수 없습니다.")
    else:
        raise HTTPException(status_code=400, detail="해당하는 이미지를 찾을 수 없습니다.")


from datetime import datetime

from fastapi import APIRouter, FastAPI, File, UploadFile, HTTPException, Form

from app.database.query import INSERT_FILE_META_DATA
from app.database.worker import execute_insert_update_query_single

router = APIRouter()


app = FastAPI()


@router.post("/uploadfile/", tags=["Audio"])
async def create_upload_file(user_id: str = Form(...), file: UploadFile = File(...)):
    # 일자, user_id

    try:
        # 파일 저장 (로컬)
        file_id = gen_file_id(user_id)
        file_path = gen_file_path(file_id)
        await save_file(file, file_path)
        metadata = create_metadata(file_id, user_id, file.filename, file_path)
        insert_file_metadata(metadata)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file")


async def save_file(file: UploadFile, file_path: str):
    with open(file_path, "wb") as buffer:
        # 파일을 1MB 크기의 청크로 나누어 처리
        while True:
            data = await file.read(1048576)  # 1MB
            if not data:
                break
            buffer.write(data)


def gen_file_id(user_id: int):
    return datetime.now().strftime("%y%m%d%H%M%S") + "_" + user_id

def gen_file_path(file_id: str):
    return f"./app/audio/{file_id}.m4a"


def create_metadata(file_id: str, user_id: str, file_name: str, file_path: str):
    return {
        "file_id": file_id,
        "user_id": user_id,
        "file_name": file_name,
        "file_path": file_path,
    }


def insert_file_metadata(metadata: dict):
    execute_insert_update_query_single(
        query = INSERT_FILE_META_DATA, 
        params = metadata
        )
    

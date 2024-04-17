from datetime import datetime
import json
from fastapi import APIRouter, FastAPI, File, UploadFile, HTTPException, Form
from starlette.concurrency import run_in_threadpool

from app.database.query import INSERT_FILE_META_DATA
from app.database.worker import execute_insert_update_query_single
from app.routers.function.clova_function import ClovaSpeechClient

router = APIRouter()
app = FastAPI()

@router.post("/uploadfile/", tags=["Audio"])
async def create_upload_file(user_id: str = Form(...), file: UploadFile = File(...)):
    try:
        file_id = gen_file_id(user_id)
        file_path = gen_file_path(file_id)
        await save_file(file, file_path)
        
        metadata = create_metadata(file_id, user_id, file.filename, file_path)
        insert_file_metadata(metadata)
        
        await file.seek(0)
        stt_result = await request_clova_stt(file)
        return stt_result
        
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

async def save_file(file: UploadFile, file_path: str):
    with open(file_path, "wb") as buffer:
        while True:
            data = await file.read(1048576)  # 1MB
            if not data:
                break
            buffer.write(data)

def gen_file_id(user_id: str):
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
        query=INSERT_FILE_META_DATA, 
        params=metadata
    )

async def request_clova_stt(file: UploadFile):
    try:
        # 파일 데이터를 안전하게 읽기
        file_data = await file.read()
        if b'\0' in file_data:
            raise ValueError("File data contains an embedded null byte")

        # Clova STT 요청을 실행
        return await run_in_threadpool(process_stt, file_data)
    except ValueError as e:
        print(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process STT: {str(e)}")


def process_stt(file_data):
    client = ClovaSpeechClient()
    # 올바른 인자 이름 'file'를 사용하여 메서드 호출
    response = client.req_upload(file=file_data)
    return response.json()


def validate_file_path(file_path):
    if '\0' in file_path:
        raise ValueError("File path contains an embedded null byte")
    return file_path

def read_file_safely(file_path):
    validated_path = validate_file_path(file_path)
    with open(validated_path, 'rb') as file:
        data = file.read()
        # NULL 바이트 검사
        if b'\0' in data:
            raise ValueError("File contains an embedded null byte")
        return data

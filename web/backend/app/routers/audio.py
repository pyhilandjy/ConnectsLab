from datetime import datetime
import json
from fastapi import APIRouter, FastAPI, File, UploadFile, HTTPException, Form, Depends, BackgroundTasks
from datetime import datetime
from starlette.concurrency import run_in_threadpool
import pandas as pd

from app.database.query import INSERT_FILE_META_DATA, INSERT_STT_RESULT_DATA
from app.database.worker import execute_insert_update_query_single
from app.routers.function.clova_function import ClovaSpeechClient

router = APIRouter()
app = FastAPI()

def get_clova_client():
    return ClovaSpeechClient()

# @router.post("/uploadfile/", tags=["Audio"])
# async def create_upload_file(
#     background_tasks: BackgroundTasks,
#     user_id: str = Form(...), 
#     file: UploadFile = File(...),
#     clova_client: ClovaSpeechClient = Depends(get_clova_client)
# ):
#     try:
#         file_id = gen_file_id(user_id)
#         file_path = gen_file_path(file_id)
#         await save_file(file, file_path)
        
#         metadata = create_metadata(file_id, user_id, file.filename, file_path)
#         insert_file_metadata(metadata)
        
#         # 인스턴스를 통한 req_upload 메소드 호출
#         segments = await stt_results(clova_client, file_path)

#         return segments

#     except Exception as e:
#         print(f"Error occurred: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.post("/uploadfile/", tags=["Audio"])
async def create_upload_file(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...), 
    file: UploadFile = File(...),
    clova_client: ClovaSpeechClient = Depends(get_clova_client)
):
    try:
        file_id = gen_file_id(user_id)
        file_path = gen_file_path(file_id)
        await save_file(file, file_path)
        
        metadata = create_metadata(file_id, user_id, file.filename, file_path)
        insert_file_metadata(metadata)
        
        # stt_results 함수를 백그라운드 작업으로 추가
        stt = stt_response(clova_client, file_path, file_id)


        return stt

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

def insert_stt_result_data(data_list):
    for data in data_list:
        try:
            execute_insert_update_query_single(
                query=INSERT_STT_RESULT_DATA, 
                params=data
            )
        except Exception as e:
            print(f"데이터 삽입 중 오류 발생: {e}")

async def stt_response(clova_client, file_path, file_id):
    response = await run_in_threadpool(clova_client.req_upload, file_path, completion='sync')
    clova_output = response.text
    data = json.loads(clova_output)
    segments = data['segments']

    data_list = []
    index = 1  
    for segment in segments:
        start_time = segment['start']
        end_time = segment['end']
        text = segment['text']
        confidence = segment['confidence']
        speaker_label = segment['speaker']['label']
        text_edited = segment['textEdited']

        segment_data = {
            'file_id': file_id,
            'index': index,
            'start_time': start_time,
            'end_time': end_time,
            'text': text,
            'confidence': confidence,
            'speaker_label': speaker_label,
            'text_edited': text_edited
        }
        data_list.append(segment_data)
        index += 1 

    # 데이터베이스에 추가
        insert_stt_result_data(data_list)
    return data_list

    


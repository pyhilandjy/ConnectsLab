from fastapi import (
    UploadFile,
)

from datetime import datetime
import json

from app.database.query import INSERT_FILE_META_DATA, INSERT_STT_RESULT_DATA
from app.database.worker import execute_insert_update_query_single
from app.routers.function.clova_function import ClovaApiClient


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
    execute_insert_update_query_single(query=INSERT_FILE_META_DATA, params=metadata)


def insert_stt_result_data(data_list):
    for data in data_list:
        try:
            execute_insert_update_query_single(
                query=INSERT_STT_RESULT_DATA, params=data
            )
        except Exception as e:
            print(f"데이터 삽입 중 오류 발생: {e}")


def get_stt_results(file_path):
    clova_api_client = ClovaApiClient()
    response = clova_api_client.request_stt(file_path=file_path)

    clova_output = response.text
    data = json.loads(clova_output)
    data["segments"]

    return data["segments"]


def insert_stt_segments(segments, file_id):
    data_list = []
    for index, segment in enumerate(segments, start=1):
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"]
        confidence = segment["confidence"]
        speaker_label = segment["speaker"]["label"]
        text_edited = segment["textEdited"]

        segment_data = {
            "file_id": file_id,
            "index": index,
            "start_time": start_time,
            "end_time": end_time,
            "text": text,
            "confidence": confidence,
            "speaker_label": speaker_label,
            "text_edited": text_edited,
        }
        data_list.append(segment_data)

        insert_stt_result_data([segment_data])

    return data_list

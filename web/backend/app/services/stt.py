from fastapi import UploadFile


from datetime import datetime
import json

import pandas as pd

from app.database.query import (
    INSERT_AUDIO_FILE_META_DATA,
    INSERT_STT_RESULT_DATA,
)
from app.database.worker import execute_insert_update_query_single
from app.routers.clovaapi.clova_function import ClovaApiClient


async def save_audio_file(file: UploadFile, file_path: str):
    """m4a파일 저장"""
    with open(file_path, "wb") as buffer:
        while True:
            data = await file.read(1048576)  # 1MB
            if not data:
                break
            buffer.write(data)


def gen_audio_file_id(user_id: str):
    """aoudio file id"""
    return datetime.now().strftime("%y%m%d%H%M%S") + "_" + user_id


def gen_audio_file_path(file_id: str):
    """파일경로 생성"""
    # 존재하지 않을 경우 mkdir 기능 추가해야함
    return f"./app/audio/{file_id}.m4a"


def create_audio_metadata(file_id: str, user_id: str, file_name: str, file_path: str):
    """오디오 파일 메타데이터 생성"""
    return {
        "file_id": file_id,
        "user_id": user_id,
        "file_name": file_name,
        "file_path": file_path,
    }


def insert_audio_file_metadata(metadata: dict):
    """오디오 파일 메타데이터 db적재"""
    execute_insert_update_query_single(
        query=INSERT_AUDIO_FILE_META_DATA, params=metadata
    )


def insert_stt_result_data(data_list):
    """stt 결과값 db 적재"""

    execute_insert_update_query_single(query=INSERT_STT_RESULT_DATA, params=data_list)


def get_stt_results(file_path):
    """클로바에서 나온 stt 세그먼츠 return"""
    clova_api_client = ClovaApiClient()
    response = clova_api_client.request_stt(file_path=file_path)

    clova_output = response.text
    data = json.loads(clova_output)
    data["segments"]

    return data["segments"]


def insert_stt_segments(segments, file_id):
    """stt결과값 필요 세그먼츠 추출 밑 적재"""
    data_list = []
    for index, segment in enumerate(segments, start=1):
        segment_data = {"file_id": file_id, "index": index}
        start_time = segment["start_time"]
        end_time = segment["end_time"]
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
        insert_stt_result_data(segment_data)
    return data_list


def splitter(text_list, punct):
    """
    :param text_list: 리스트로 감싸진 문장들
    :param punct: 처리할 특수문자
    """
    output_list = []

    # input으로 받은 문장 리스트에 대해 (리스트 원소가 하나라도 동일하게 작업 됨)
    for sentence in text_list:
        sentence = sentence.strip()

        # 특수문자가 문장에 있다면
        if punct in sentence:
            texts = []
            temp_sent = ""

            # 띄어쓰기로 단어별 문장 split
            for word in sentence.split():

                # 임시 문장에 단어와 띄어쓰기 추가
                temp_sent += word + " "

                # 주어진 특수문자가 단어에 있다면
                if punct in word:
                    # 문장 양 끝의 공백 제거 후 texts 리스트에 추가
                    texts.append(temp_sent.strip())
                    # 임시 문장 초기화
                    temp_sent = ""

            # 문장의 마지막이 주어진 특수문자가 아닐 때, 최종 저장된 임시문장을 texts 리스트에 추가
            # 이걸 안해주면 특수문자 없는 마지막 문장이 최종 결과물에 포함되지 않음
            if temp_sent != texts[-1]:
                if temp_sent.strip() != "":
                    texts.append(temp_sent.strip())

            # texts의 문장들을 최종 output 리스트에 추가
            for text in texts:
                output_list.append(text)

        # 문장에 특수문자가 없다면 그냥 문장 그대로 최종 output 리스트에 추가
        else:
            output_list.append(sentence)
    return output_list


def explode(segments: list, target_col: str):
    """
    :params segments : 줄바꿈을 해야할 DataFrame
    :params target_col : 대상이 될 Column

    :return : 줄바꿈이 완료된 DataFrame
    """

    # 작업할 특수문자들 / 특수 문자 추가 필요시 여기에 그냥 추가하면 됨
    puncts = ".?!"

    return_list = []
    # 매 row 별로 데이터 작업
    for index in range(len(segments)):
        target_text = [segments[index][target_col]]

        # 매 특수문자 별 splitter 실행
        for punct in puncts:
            target_text = splitter(target_text, punct)

        # splitter의 output의 text별로 col_datas의 컬럼별 리스트에 추가 (DF Row 추가하는 작업)
        for text in target_text:
            col_data = {}
            # 컬럼별로 작업
            for col in segments[index].keys():
                # target column에 나누어진 text 추가
                if col == target_col:
                    col_data[target_col] = text

                # 나머지 컬럼은 원래 컬럼 내용과 동일하게 추가
                else:
                    col_data[col] = segments[index][col]

            return_list.append(col_data)
    return return_list


def rename_keys(segments):
    segment = segments[0]
    segment_names = {}
    time = []
    for key, value in segment.items():
        if type(value) == int:
            time.append([key, value])
        elif type(value) == str:
            if "edited" in key.lower():
                segment_names[key] = "textEdited"
            else:
                segment_names[key] = "text"
        elif type(value) == float:
            segment_names[key] = "confidence"
        elif type(value) == dict:
            if "name" in value.keys():
                segment_names[key] = "speaker"
            else:
                segment_names[key] = "diarization"
        elif type(value) == list:
            segment_names[key] = "words"
        else:
            print("뭔가 잘못됐다")

    if time[0][1] > time[1][1]:
        segment_names[time[0][0]] = "end_time"
        segment_names[time[1][0]] = "start_time"
    else:
        segment_names[time[0][0]] = "start_time"
        segment_names[time[1][0]] = "end_time"

    output = []
    for segment in segments:
        output.append({segment_names.get(k, k): v for k, v in segment.items()})
    return output

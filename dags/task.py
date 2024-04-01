from datetime import datetime, timedelta
from konlpy.tag import *
from function.database import to_db
from function.clova_function import ClovaSpeechClient, read_text_file, analyze_text_with_mecab_to_xlsx, extract_last_part, get_user_name, get_user_id, get_m4a_files_in_folder, stop_airflow_containers
import requests
import json 
import pandas as pd
import pymysql
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import subprocess
import os

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

def STT():
    """전날 m4a파일 STT 후 db에 적재"""
    # 폴더 경로 지정
    folder_path = '/opt/airflow/dags/m4a/d10'

    # 폴더 내의 모든 m4a 파일 가져오기
    m4a_files = get_m4a_files_in_folder(folder_path, start_with_beforeday=True)

    # 각 파일에 대해 처리
    for audio_file in m4a_files:
        user_info = extract_last_part(audio_file) 
        base_filename = f"{user_info}_"

        res = ClovaSpeechClient().req_upload(file=audio_file, completion='sync')
        clova_output = res.text
        data = json.loads(clova_output)
        segments = data['segments']

        # datetime 필요 filename의 앞 6글자
        data_list = []
        for segment in segments:
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text']
            confidence = segment['confidence']
            speaker_label = segment['speaker']['label']
            text_edited = segment['textEdited']
            user_name = get_user_name(audio_file)
            user_id = get_user_id(user_name)
            date = base_filename[:6]
            

            data_list.append([user_id, user_name, start_time, end_time, text, confidence, speaker_label, text_edited, date])

        
        df = pd.DataFrame(data_list, columns=['user_id', 'user_name', 'start_time', 'end_time', 'text', 'confidence', 'speaker_label', 'text_edited', 'date'])
        
        df['index'] = df.groupby(['user_id', 'date']).cumcount() + 1
        
        df['unique_id'] = df['user_id'].astype(str) + '_' + df['date'].astype(str) + '_' + df['index'].astype(str)
        
    to_db(df)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG(
    "stt_task",
    default_args=default_args,
    description="daily STT yesterday m4a file",
    schedule_interval='@daily',
    start_date=datetime(2023, 11, 30),
    catchup=False,
)

# Python Operator 정의
get_instagram_task = PythonOperator(
    task_id="STT",
    python_callable=STT,
    provide_context=True,
    dag=dag,
)



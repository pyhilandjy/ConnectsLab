from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

# 추가된 import 구문
from konlpy.tag import *
from function.clova_function import ClovaSpeechClient, get_m4a_files_in_folder, extract_last_part, get_user_name, get_user_id
import json

def STT(file):
    """전날 m4a 파일 STT 후 db에 적재"""
    m4a_files = file
    
    for audio_file in m4a_files:
        user_info = extract_last_part(audio_file)
        base_filename = f"{user_info}_"
        
        res = ClovaSpeechClient().req_upload(file=audio_file, completion='sync')
        clova_output = res.text
        data = json.loads(clova_output)
        segments = data['segments']
        
        data_list = []
        for segment in segments:
            start_time, end_time = segment['start'], segment['end']
            text, confidence = segment['text'], segment['confidence']
            speaker_label, text_edited = segment['speaker']['label'], segment['textEdited']
            user_name = get_user_name(audio_file)
            user_id =  get_user_id(user_name)
            date = base_filename[:6]
            
            data_list.append([user_id, user_name, start_time, end_time, text, confidence, speaker_label, text_edited, date])
        
        df = pd.DataFrame(data_list, columns=['user_id', 'user_name', 'start_time', 'end_time', 'text', 'confidence', 'speaker_label', 'text_edited', 'date'])
        
        # 누적 카운트를 위한 인덱스 추가
        df['index'] = df.groupby(['user_id', 'date']).cumcount() + 1
        # 유일한 식별자 컬럼 생성
        df['unique_id'] = df['user_id'].astype(str) + '_' + df['date'].astype(str) + '_' + df['index'].astype(str)
        
        to_db(df)

def to_db(df):
    """DataFrame을 MySQL 데이터베이스에 적재"""
    engine = create_engine('mysql+pymysql://jun:1234qwer@host.docker.internal/STT')
    df.to_sql(name='stt', con=engine, if_exists='append', index=False)


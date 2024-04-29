import os
import requests #naver CLOVA Speech API
import json     #naver CLOVA Speech API
import pymysql
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from function.database import to_db
import subprocess
import pandas as pd
from function.database import to_db


class ClovaSpeechClient:
    # Clova Speech invoke URL
    invoke_url = 'https://clovaspeech-gw.ncloud.com/external/v1/6542/2a76879d93ca2fd6fc6fcf7cdc1cdf1888f7487dbff7c21c5a0ab0d655659361'
    # Clova Speech secret key
    secret = 'e528cad5fdc14d84808b304e6eb77b35'

    def req_upload(self, file, completion='sync', callback=None, userdata=None, forbiddens=None, boostings=None,
                   wordAlignment=True, fullText=True, diarization=None):
        request_body = {
            'language': 'ko-KR',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': diarization,
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }
        print(json.dumps(request_body, ensure_ascii=False).encode('UTF-8'))
        files = {
            'media': open(file, 'rb'),
            'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
        }
        response = requests.post(headers=headers, url=self.invoke_url + '/recognizer/upload', files=files)
        return response


# 텍스트 파일을 읽어서 반환하는 함수
def read_text_file(file_path):
    """file_path를 열어서 text로 반환"""
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

# MeCab을 사용하여 텍스트를 형태소로 분석하고 XLSX 파일로 저장하는 함수
def analyze_text_with_mecab_to_xlsx(text, output_xlsx):
    """MeCab을 사용하여 텍스트를 형태소로 분석하고 XLSX 파일로 저장하는 함수"""
    mecab = MeCab.Tagger()
    pos_lists = {'고유명사': [], '일반명사': [], '대명사': [], '동사': [], '형용사': [], '부사': [], '접속사': [], '조사': [], '숫자': []}
    pos_unique_lists = {'고유명사': set(), '일반명사': set(), '대명사': set(), '동사': set(), '형용사': set(), '부사': set(), '접속사': set(), '조사': set(), '숫자': set()}

    # 형태소 분석
    parsed = mecab.parse(text)
    for line in parsed.split('\n'):
        if '\t' not in line:
            continue
        word, tag_info = line.split('\t')
        tag = tag_info.split(',')[0]

        # 품사별 리스트에 단어 추가
        # 고유명사
        if tag == 'NNP':
            pos_lists['고유명사'].append(word)
            pos_unique_lists['고유명사'].add(word)
        # 일반명사
        elif tag == 'NNG':
            pos_lists['일반명사'].append(word)
            pos_unique_lists['일반명사'].add(word)
        # 대명사
        elif tag == 'NP':
            pos_lists['대명사'].append(word)
            pos_unique_lists['대명사'].add(word)
        # 동사
        elif tag == 'VV':
            pos_lists['동사'].append(word)
            pos_unique_lists['동사'].add(word)
        # 형용사
        elif tag == 'VA':
            pos_lists['형용사'].append(word)
            pos_unique_lists['형용사'].add(word)
        # 부사
        elif tag == 'MAG':
            pos_lists['부사'].append(word)
            pos_unique_lists['부사'].add(word)
        # 접속사
        elif tag == 'JC':
            pos_lists['접속사'].append(word)
            pos_unique_lists['접속사'].add(word)
        # 조사
        elif tag == 'JX':
            pos_lists['조사'].append(word)
            pos_unique_lists['조사'].add(word)
        # 숫자
        elif tag == 'SN':
            pos_lists['숫자'].append(word)
            pos_unique_lists['숫자'].add(word)

    # 결과 데이터를 DataFrame으로 변환
    data = {
        '품사': [],
        '단어 수': [],
        '중복 없는 단어 수': [],
        '단어 리스트': [],
        '중복 없는 단어 리스트': []
    }
    for pos in pos_lists:
        data['품사'].append(pos)
        data['단어 수'].append(len(pos_lists[pos]))
        data['중복 없는 단어 수'].append(len(pos_unique_lists[pos]))
        data['단어 리스트'].append(', '.join(pos_lists[pos]))
        data['중복 없는 단어 리스트'].append(', '.join(pos_unique_lists[pos]))

    df = pd.DataFrame(data)



# Function to extract the specified part
def extract_last_part(path):
    """ m4a의 파일 이름 last_part'"""
    # Split the path by '/'
    parts = path.split('/')
    # Take the last part and split by '.txt'
    last_part = parts[-1].split('.m4a')[0]
    return last_part

def get_user_name(file_path):
    # 파일명에서 마지막 부분을 추출하여 user_id와 user_name을 얻어옴
    file_name = os.path.basename(file_path)
    parts = file_name.split('_')
    user_info = parts[1]
    return user_info

def get_user_id(user_name):
    # MySQL에서 user_id에 해당하는 사용자 정보 조회
    connection = pymysql.connect(
        user='jun',
        password='1234qwer',
        host='host.docker.internal',
        database='STT',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    cursor = connection.cursor()
    query = f"SELECT user_id FROM user WHERE user_name = '{user_name}'"
    cursor.execute(query)
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()

    return str(result['user_id'])

def get_m4a_files_in_folder(folder_path, start_with_beforeday=False):
    """ 전날의 .m4a파일을 불러오는 함수"""
    yesterday = datetime.now() - timedelta(days=1)
    yesterday = yesterday.strftime("%y%m%d")

    files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.m4a')]
    
    if start_with_beforeday:
        filtered_files = [file for file in files if os.path.basename(file).startswith(yesterday)]
        return filtered_files
    
    return files

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
    to_db(table = 'STT', df = df)

def stop_airflow_containers():
    subprocess.run(["docker", "compose", "down"])
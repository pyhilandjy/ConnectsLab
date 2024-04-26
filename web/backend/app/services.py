import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from fastapi import UploadFile
from pydantic import BaseModel

import mecab_ko as MeCab
from collections import Counter
from io import BytesIO
import os


from datetime import datetime, date
import json

from app.database.query import (
    INSERT_AUDIO_FILE_META_DATA,
    INSERT_STT_RESULT_DATA,
    INSERT_IMAGE_FILE_META_DATA,
    SELECT_STT_RESULTS_WORDCLOUD,
)
from app.database.worker import execute_insert_update_query_single, execute_select_query
from app.routers.function.clova_function import ClovaApiClient

SPEAKER_COL_NAME = "speaker_label"
CONTENTS_COL_NAME = "text_edited"
FONT_PATH = "NanumFontSetup_TTF_GOTHIC/NanumGothic.ttf"
POS_TAG_TO_KOREAN = {
    "NNP": "고유명사",
    "NNG": "일반명사",
    "NP": "대명사",
    "VV": "동사",
    "VA": "형용사",
    "MAG": "부사",
    "JC": "접속사",
    "JX": "조사",
    "SN": "숫자",
}


async def save_audio_file(file: UploadFile, file_path: str):
    with open(file_path, "wb") as buffer:
        while True:
            data = await file.read(1048576)  # 1MB
            if not data:
                break
            buffer.write(data)


def gen_audio_file_id(user_id: str):
    return datetime.now().strftime("%y%m%d%H%M%S") + "_" + user_id


def gen_audio_file_path(file_id: str):
    """파일경로 생성"""
    # 존재하지 않을 경우 mkdir 기능 추가해야함
    return f"./app/audio/{file_id}.m4a"


def create_audio_metadata(file_id: str, user_id: str, file_name: str, file_path: str):
    return {
        "file_id": file_id,
        "user_id": user_id,
        "file_name": file_name,
        "file_path": file_path,
    }


def insert_audio_file_metadata(metadata: dict):
    execute_insert_update_query_single(
        query=INSERT_AUDIO_FILE_META_DATA, params=metadata
    )


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


#################stt#################


def parse_text(text):
    """텍스트에 형태소분석 결과를 반환"""
    mecab = MeCab.Tagger()
    return mecab.parse(text)


def classify_words_by_pos(parsed_text):
    """파싱된 텍스트에서 품사별로 단어를 분류"""
    pos_lists = {korean: [] for korean in POS_TAG_TO_KOREAN.values()}
    pos_unique_lists = {korean: set() for korean in POS_TAG_TO_KOREAN.values()}

    for line in parsed_text.split("\n"):
        if "\t" not in line:
            continue
        word, tag_info = line.split("\t")
        tag = tag_info.split(",")[0]
        if tag in POS_TAG_TO_KOREAN:
            korean_pos = POS_TAG_TO_KOREAN[tag]
            pos_lists[korean_pos].append(word)
            pos_unique_lists[korean_pos].add(word)

    return pos_lists, pos_unique_lists


def build_pos_summary(pos_lists, pos_unique_lists):
    """품사별 단어 리스트와 고유 단어 세트에서 요약 정보를 구성하여 반환"""
    return {
        pos: {
            "단어 수": len(words),
            "중복 없는 단어 수": len(pos_unique_lists[pos]),
            "단어 리스트": ", ".join(words),
            "중복 없는 단어 리스트": ", ".join(pos_unique_lists[pos]),
        }
        for pos, words in pos_lists.items()
    }


def analyze_text_with_mecab(text):
    """품사별로 단어를 분류"""
    parsed_text = parse_text(text)
    pos_lists, pos_unique_lists = classify_words_by_pos(parsed_text)
    return build_pos_summary(pos_lists, pos_unique_lists)


def extract_speaker_data(data):
    """발화자별로 텍스트를 추출하여 하나의 문자열로 결합"""
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)
    speaker_data = (
        data.groupby("speaker_label")["text_edited"]
        .apply(lambda texts: " ".join(texts.astype(str)))
        .to_dict()
    )
    return speaker_data


def analyze_speech_data(data):
    """형태소분석"""
    speaker_data = extract_speaker_data(data)
    return {
        speaker: analyze_text_with_mecab(text) for speaker, text in speaker_data.items()
    }


#################형태소분석#################


# Create a circle mask
def create_circle_mask():
    """mask 생성"""
    x, y = np.ogrid[:600, :600]  # adjust to desired dimensions
    center_x, center_y = 300, 300  # adjust to be the center of the circle
    radius = 300  # adjust to be the radius of the circle

    circle = (x - center_x) ** 2 + (y - center_y) ** 2 <= radius**2
    mask = 255 * np.ones((600, 600), dtype=np.uint8)
    mask[circle] = 0
    return mask


def extract_nouns_with_mecab(text):
    """형태소분석 명사 추출"""
    mecab = MeCab.Tagger()
    nouns = []
    for line in mecab.parse(text).split("\n"):
        if "\t" in line:
            word, tag_info = line.split("\t")
            tag = tag_info.split(",")[0]
            if tag in ["NNG", "NNP"]:  # 일반명사와 고유명사
                nouns.append(word)
    return nouns


def count_words(nouns):
    """한 글자 명사 제거"""
    words = [word for word in nouns if len(word) > 1]
    return Counter(words)


def generate_wordcloud(word_counts, font_path, mask):
    """워드클라우드 기본 생성"""
    wc = WordCloud(
        font_path=font_path,
        background_color="white",
        width=800,
        height=800,
        max_words=200,
        max_font_size=100,
        colormap="viridis",  # 색상 맵 변경
        mask=mask,
    )
    wc.generate_from_frequencies(word_counts)
    return wc


def save_wordcloud(wordcloud, image_path):
    """워드클라우드를 파일로 저장"""
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(image_path, format="PNG")  # 이미지 파일로 저장
    plt.close()


def create_wordcloud(stt_wordcloud, font_path, user_id, start_date, end_date, type):
    """워드클라우드 생성 및 파일로 저장"""
    if not isinstance(stt_wordcloud, pd.DataFrame):
        stt_wordcloud = pd.DataFrame(stt_wordcloud)

    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    for speaker in stt_wordcloud["speaker_label"].unique():
        speaker_data = stt_wordcloud[stt_wordcloud["speaker_label"] == speaker]
        text = " ".join(speaker_data["text_edited"].astype(str))
        nouns = extract_nouns_with_mecab(text)
        word_counts = count_words(nouns)
        mask = create_circle_mask()
        wordcloud = generate_wordcloud(word_counts, font_path, mask)

        image_id = gen_image_file_id(user_id, speaker, start_date, end_date, type)

        # 파일 경로 생성
        image_path = gen_wordcloud_file_path(
            user_id,
            speaker,
            start_date,
            end_date,
            type,
        )

        metadata = create_image_metadata(
            image_id=image_id,
            user_id=user_id,
            speaker=speaker,
            start_date=start_date,
            end_date=end_date,
            type=type,
            image_path=image_path,
        )
        insert_image_file_metadata(metadata)
        # 워드클라우드 저장
        save_wordcloud(wordcloud, image_path)
    return image_path


#################워드클라우드#################


# image file data
def gen_image_file_id(
    user_id: str, speaker: str, start_date: date, end_date: date, type: str
) -> str:
    """이미지 파일 아이디 생성"""
    return f"{user_id}_{speaker}_{start_date}_{end_date}_{type}"


def gen_wordcloud_file_path(
    user_id: str, speaker: str, start_date: date, end_date: date, type: str
):
    """이미지 파일경로 생성"""
    directory = f"../backend/app/image"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return f"{directory}/{user_id}_{speaker}_{start_date}_{end_date}_{type}.png"


def create_image_metadata(
    image_id: str,
    speaker: str,
    user_id: str,
    start_date: date,
    end_date: date,
    type: str,
    image_path: str,
):
    return {
        "image_id": image_id,
        "speaker": speaker,
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
        "type": type,
        "image_path": image_path,
    }


def insert_image_file_metadata(metadata: dict):
    execute_insert_update_query_single(
        query=INSERT_IMAGE_FILE_META_DATA, params=metadata
    )

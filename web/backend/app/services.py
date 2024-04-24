from pytz import timezone
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from fastapi import UploadFile

import mecab_ko as MeCab
from collections import Counter
from io import BytesIO


from datetime import datetime
import json

from app.database.query import INSERT_FILE_META_DATA, INSERT_STT_RESULT_DATA
from app.database.worker import execute_insert_update_query_single
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


def display_wordcloud(wordcloud, title):
    """워드클라우드 표시 세팅"""
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title(title)
    buffer = BytesIO()
    plt.savefig(buffer, format="PNG")
    # plt.show()
    # plt.close()
    # buffer.seek(0)
    return plt.show()


def create_wordcloud(stt_wordcloud, font_path=FONT_PATH):
    """워드클라우드 생성"""
    if not isinstance(stt_wordcloud, pd.DataFrame):
        stt_wordcloud = pd.DataFrame(stt_wordcloud)
    for speaker in stt_wordcloud["speaker_label"].unique():
        speaker_data = stt_wordcloud[stt_wordcloud["speaker_label"] == speaker]
        text = " ".join(speaker_data["text_edited"].astype(str))
        nouns = extract_nouns_with_mecab(text)
        word_counts = count_words(nouns)
        mask = create_circle_mask()
        wordcloud = generate_wordcloud(word_counts, font_path, mask)
        display_wordcloud(wordcloud, f"WordCloud for Speaker {speaker}")


#################워드클라우드#################

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from wordcloud import WordCloud
# import seaborn as sns
# from matplotlib import font_manager, rc

# import mecab_ko as MeCab
# from collections import Counter
# import os


# from datetime import date

# from cl.backend.database.query import (
#     INSERT_IMAGE_FILES_META_DATA,
# )
# from cl.backend.database.worker import execute_insert_update_query_single

# FONT_PATH = "./assets/NanumFontSetup_TTF_GOTHIC/NanumGothic.ttf"
# # font_prop = font_manager.FontProperties(fname=FONT_PATH)
# # rc("font", family=font_prop.get_name())

# POS_TAG_TO_KOREAN = {
#     "NNP": "고유명사",
#     "NNG": "일반명사",
#     "NP": "대명사",
#     "VV": "동사",
#     "VA": "형용사",
#     "MAG": "부사",
#     "JC": "접속사",
#     "JX": "조사",
#     "SN": "숫자",
# }


# def parse_text(text):
#     """텍스트에 형태소분석 결과를 반환"""
#     mecab = MeCab.Tagger()
#     return mecab.parse(text)


# def classify_words_by_pos(parsed_text):
#     """파싱된 텍스트에서 품사별로 단어를 분류"""
#     pos_lists = {korean: [] for korean in POS_TAG_TO_KOREAN.values()}
#     pos_unique_lists = {korean: set() for korean in POS_TAG_TO_KOREAN.values()}

#     for line in parsed_text.split("\n"):
#         if "\t" not in line:
#             continue
#         word, tag_info = line.split("\t")
#         tag = tag_info.split(",")[0]
#         if tag in POS_TAG_TO_KOREAN:
#             korean_pos = POS_TAG_TO_KOREAN[tag]
#             pos_lists[korean_pos].append(word)
#             pos_unique_lists[korean_pos].add(word)

#     return pos_lists, pos_unique_lists


# def build_pos_summary(pos_lists, pos_unique_lists):
#     """품사별 단어 리스트와 고유 단어 세트에서 요약 정보를 구성하여 반환"""
#     return {
#         pos: {
#             "단어 수": len(words),
#             "중복 없는 단어 수": len(pos_unique_lists[pos]),
#             "단어 리스트": ", ".join(words),
#             "중복 없는 단어 리스트": ", ".join(pos_unique_lists[pos]),
#         }
#         for pos, words in pos_lists.items()
#     }


# def analyze_text_with_mecab(text):
#     """품사별로 단어를 분류"""
#     parsed_text = parse_text(text)
#     pos_lists, pos_unique_lists = classify_words_by_pos(parsed_text)
#     return build_pos_summary(pos_lists, pos_unique_lists)


# def extract_speaker_data(data):
#     """발화자별로 텍스트를 추출하여 하나의 문자열로 결합"""
#     if not isinstance(data, pd.DataFrame):
#         data = pd.DataFrame(data)
#     speaker_data = (
#         data.groupby("speaker_label")["text_edited"]
#         .apply(lambda texts: " ".join(texts.astype(str)))
#         .to_dict()
#     )
#     return speaker_data


# def analyze_speech_data(data):
#     """형태소분석"""
#     speaker_data = extract_speaker_data(data)
#     return {
#         speaker: analyze_text_with_mecab(text) for speaker, text in speaker_data.items()
#     }


# #################형태소분석#################


# # Create a circle mask
# def create_circle_mask():
#     """mask 생성"""
#     x, y = np.ogrid[:600, :600]  # adjust to desired dimensions
#     center_x, center_y = 300, 300  # adjust to be the center of the circle
#     radius = 300  # adjust to be the radius of the circle

#     circle = (x - center_x) ** 2 + (y - center_y) ** 2 <= radius**2
#     mask = 255 * np.ones((600, 600), dtype=np.uint8)
#     mask[circle] = 0
#     return mask


# def extract_nouns_with_mecab(text):
#     """형태소분석 명사 추출"""
#     mecab = MeCab.Tagger()
#     nouns = []
#     for line in mecab.parse(text).split("\n"):
#         if "\t" in line:
#             word, tag_info = line.split("\t")
#             tag = tag_info.split(",")[0]
#             if tag in ["NNG", "NNP"]:  # 일반명사와 고유명사
#                 nouns.append(word)
#     return nouns


# def count_words(nouns):
#     """한 글자 명사 제거"""
#     words = [word for word in nouns if len(word) > 1]
#     return Counter(words)


# def generate_wordcloud(word_counts, font_path, mask):
#     """워드클라우드 기본 생성"""
#     wc = WordCloud(
#         font_path=font_path,
#         background_color="white",
#         width=800,
#         height=800,
#         max_words=200,
#         max_font_size=100,
#         colormap="viridis",  # 색상 맵 변경
#         mask=mask,
#     )
#     wc.generate_from_frequencies(word_counts)
#     return wc


# def save_wordcloud(wordcloud, image_path):
#     """워드클라우드를 파일로 저장"""
#     plt.figure(figsize=(10, 10))
#     plt.imshow(wordcloud, interpolation="bilinear")
#     plt.axis("off")
#     plt.savefig(image_path, format="PNG")  # 이미지 파일로 저장
#     plt.close()


# def create_wordcloud(stt_wordcloud, font_path, user_id, start_date, end_date, type):
#     """워드클라우드 생성 및 파일로 저장"""
#     if not isinstance(stt_wordcloud, pd.DataFrame):
#         stt_wordcloud = pd.DataFrame(stt_wordcloud)

#     f_start_date = start_date.strftime("%Y-%m-%d")
#     f_end_date = end_date.strftime("%Y-%m-%d")

#     for speaker in stt_wordcloud["speaker_label"].unique():
#         speaker_data = stt_wordcloud[stt_wordcloud["speaker_label"] == speaker]
#         text = " ".join(speaker_data["text_edited"].astype(str))
#         nouns = extract_nouns_with_mecab(text)
#         word_counts = count_words(nouns)
#         mask = create_circle_mask()
#         wordcloud = generate_wordcloud(word_counts, font_path, mask)

#         image_id = gen_image_file_id(user_id, speaker, f_start_date, f_end_date, type)

#         # 파일 경로 생성
#         image_path = gen_image_file_path(
#             user_id,
#             speaker,
#             f_start_date,
#             f_end_date,
#             type,
#         )

#         metadata = create_image_metadata(
#             image_id=image_id,
#             user_id=user_id,
#             speaker=speaker,
#             start_date=start_date,
#             end_date=end_date,
#             type=type,
#             image_path=image_path,
#         )
#         insert_image_file_metadata(metadata)
#         # 워드클라우드 저장
#         save_wordcloud(wordcloud, image_path)
#     return image_path


# # image file data
# def gen_image_file_id(
#     user_id: str, speaker: str, start_date: date, end_date: date, type: str
# ) -> str:
#     """이미지 파일 아이디 생성"""
#     return f"{user_id}_{speaker}_{start_date}_{end_date}_{type}.png"


# def gen_image_file_path(
#     user_id: str, speaker: str, start_date: date, end_date: date, type: str
# ):
#     """이미지 파일경로 생성"""
#     directory = f"../backend/app/image"
#     if not os.path.exists(directory):
#         os.makedirs(directory)
#     return f"{directory}/{user_id}_{speaker}_{start_date}_{end_date}_{type}.png"


# def create_image_metadata(
#     image_id: str,
#     speaker: str,
#     user_id: str,
#     start_date: date,
#     end_date: date,
#     type: str,
#     image_path: str,
# ):
#     return {
#         "image_id": image_id,
#         "speaker": speaker,
#         "user_id": user_id,
#         "start_date": start_date,
#         "end_date": end_date,
#         "type": type,
#         "image_path": image_path,
#     }


# def insert_image_file_metadata(metadata: dict):
#     execute_insert_update_query_single(
#         query=INSERT_IMAGE_FILES_META_DATA, params=metadata
#     )


# #################워드클라우드#################


# def violin_chart(stt_violin_chart, user_id, start_date, end_date, type, font_path):
#     if not isinstance(stt_violin_chart, pd.DataFrame):
#         stt_violin_chart = pd.DataFrame(stt_violin_chart)
#     stt_violin_chart["char"] = stt_violin_chart["text_edited"].apply(len)
#     f_start_date = start_date.strftime("%Y-%m-%d")
#     f_end_date = end_date.strftime("%Y-%m-%d")
#     speaker = stt_violin_chart["speaker_label"].unique()
#     speaker = ",".join(speaker)

#     font_prop = font_manager.FontProperties(fname=font_path)
#     plt.rcParams["font.family"] = font_prop.get_name()
#     plt.rcParams["axes.unicode_minus"] = False
#     image_id = gen_image_file_id(user_id, speaker, f_start_date, f_end_date, type)

#     image_path = gen_image_file_path(
#         user_id,
#         speaker,
#         f_start_date,
#         f_end_date,
#         type,
#     )

#     metadata = create_image_metadata(
#         image_id=image_id,
#         user_id=user_id,
#         speaker=speaker,
#         start_date=start_date,
#         end_date=end_date,
#         type=type,
#         image_path=image_path,
#     )
#     insert_image_file_metadata(metadata)
#     sns.set_palette(sns.color_palette("Set2", 2))
#     save_violin_plot(stt_violin_chart, image_path, font_prop)
#     return image_path


# def save_violin_plot(stt_violin_chart, image_path, font_prop):
#     plt.figure(figsize=(6, 6))
#     plt.title("발화자별 문장 길이 분포", fontproperties=font_prop)
#     plt.xlabel("speaker_label", fontproperties=font_prop)
#     plt.ylabel("문장 길이", fontproperties=font_prop)

#     sns.violinplot(
#         data=stt_violin_chart,
#         x="speaker_label",
#         y="char",
#         hue="speaker_label",
#         split=True,
#         inner="quart",
#         palette=sns.color_palette("Set2"),
#     )

#     plt.tight_layout()
#     plt.savefig(image_path, format="PNG")  # 이미지 파일로 저장
#     plt.close()

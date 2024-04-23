from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from fastapi.responses import FileResponse
import pandas as pd

from app.database.query import SELECT_STT_RESULTS, SELECT_STT_RESULTS_WORDCLOUD
from app.database.worker import execute_select_query
from app.services import analyze_speech_data, create_wordcloud

router = APIRouter()


class FileModel(BaseModel):
    file_id: str


@router.post("/stt-results-by-file_id/", tags=["stt_results"])
async def get_stt_results_by_file_id(stt_model: FileModel):
    """stt result를 가져오는 엔드포인트"""
    user_info = execute_select_query(
        query=SELECT_STT_RESULTS, params={"file_id": stt_model.file_id}
    )

    if not user_info:
        raise HTTPException(status_code=404, detail="Users not found")

    return user_info


class WordcloudModel(BaseModel):
    user_id: str
    start_date: date
    end_date: date


@router.post("/stt-results-wordcloud/", tags=["stt_results"])
async def get_stt_results_for_wordcloud(wordcloud_model: WordcloudModel):
    """워드클라우드를 위한 stt result를 가져오는 엔드포인트"""
    stt_wordcloud = execute_select_query(
        query=SELECT_STT_RESULTS_WORDCLOUD,
        params={
            "user_id": wordcloud_model.user_id,
            "start_date": wordcloud_model.start_date,
            "end_date": wordcloud_model.end_date,
        },
    )

    if not stt_wordcloud:
        raise HTTPException(status_code=404, detail="Users not found")

    else:
        # morphs_result = analyze_speech_data(stt_wordcloud)
        word_cloud = create_wordcloud(stt_wordcloud)
    return word_cloud


def gen_wordcloud(data):
    df = pd.DataFrame(data)
    wordcloud_generator = analyze_speech_data(dataframe=df, name="output_name")

    pass


# @router.post("/generate_wordcloud/")
# async def generate_wordcloud(data: List[Dict[str, str]]):
#     try:
#         # 데이터 프레임 생성
#         df = pd.DataFrame(data)

#         # 워드클라우드 객체 생성
#         wordcloud_generator = KhaiiiWordCloud(df)

#         # 워드클라우드 생성 및 저장
#         image_path = wordcloud_generator.create_wordcloud(name="output_name")

#         # 이미지 파일로 반환
#         return FileResponse(image_path, media_type="image/png", filename=image_path)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

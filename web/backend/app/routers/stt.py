from fastapi import APIRouter, HTTPException, Form, File
from pydantic import BaseModel
from datetime import date

from app.database.query import SELECT_STT_RESULTS, SELECT_STT_RESULTS_WORDCLOUD
from app.database.worker import execute_select_query
from app.services import create_wordcloud, FONT_PATH

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
async def generate_wordcloud(wordcloud_model: WordcloudModel):
    """워드클라우드를 위한 STT 결과를 가져오는 엔드포인트"""
    stt_wordcloud = execute_select_query(
        query=SELECT_STT_RESULTS_WORDCLOUD,
        params={
            "user_id": wordcloud_model.user_id,
            "start_date": wordcloud_model.start_date,
            "end_date": wordcloud_model.end_date,
        },
    )

    if not stt_wordcloud:
        raise HTTPException(
            status_code=404,
            detail="No STT results found for the specified user and date range.",
        )

    user_id = wordcloud_model.user_id
    start_date = wordcloud_model.start_date
    end_date = wordcloud_model.end_date
    font_path = FONT_PATH

    # 워드클라우드 생성 및 이미지 저장
    type = "wordcloud"
    image_path = create_wordcloud(
        stt_wordcloud, font_path, user_id, start_date, end_date, type
    )
    return image_path

from fastapi import APIRouter, HTTPException, Form, File
from pydantic import BaseModel
from datetime import date

from app.database.query import (
    SELECT_STT_RESULTS,
    SELECT_STT_RESULTS_WORDCLOUD,
    SELECT_IMAGE_FILES,
    SELECT_IMAGE_TYPE,
)
from app.database.worker import execute_select_query
from app.services import create_wordcloud, FONT_PATH

router = APIRouter()


class FileModel(BaseModel):
    file_id: str


class WordcloudModel(BaseModel):
    user_id: str
    start_date: date
    end_date: date


class ImagefileModel(BaseModel):
    user_id: str
    start_date: date
    end_date: date
    type: str


class ImagetypeModel(BaseModel):
    user_id: str
    start_date: date
    end_date: date


@router.post("/stt-results-by-file_id/", tags=["stt_results"])
async def get_stt_results_by_file_id(stt_model: FileModel):
    """stt result를 가져오는 엔드포인트"""
    user_info = execute_select_query(
        query=SELECT_STT_RESULTS, params={"file_id": stt_model.file_id}
    )

    if not user_info:
        raise HTTPException(status_code=404, detail="Users not found")

    return user_info


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


@router.post("/stt-results/image_file/", tags=["stt_results"])
async def get_image_file(imagefilemodel: ImagefileModel):
    """
    image_files 데이터를 가져오는 엔드포인트
    """

    image_files = execute_select_query(
        query=SELECT_IMAGE_FILES,
        params={
            "user_id": imagefilemodel.user_id,
            "start_date": imagefilemodel.start_date,
            "end_date": imagefilemodel.end_date,
            "type": imagefilemodel.type,
        },
    )

    if not image_files:
        raise HTTPException(status_code=404, detail="files not found")

    return image_files


@router.post("/stt-results/image_type/", tags=["stt_results"])
async def get_image_type(imagetypemodel: ImagetypeModel):
    """
    image_type을 가져오는 엔드포인트
    """

    image_type = execute_select_query(
        query=SELECT_IMAGE_TYPE,
        params={
            "user_id": imagetypemodel.user_id,
            "start_date": imagetypemodel.start_date,
            "end_date": imagetypemodel.end_date,
        },
    )

    if not image_type:
        raise HTTPException(status_code=404, detail="type not found")

    return image_type

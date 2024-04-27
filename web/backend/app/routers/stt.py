from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import date

import zipfile
import os

from app.database.query import (
    SELECT_STT_RESULTS,
    SELECT_STT_RESULTS_WORDCLOUD,
    SELECT_IMAGE_FILES,
    SELECT_IMAGE_TYPE,
)
from app.database.worker import execute_select_query
from app.services.gen_wordcloud import create_wordcloud, FONT_PATH

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
    """file_id별로 stt result를 가져오는 엔드포인트"""
    user_info = execute_select_query(
        query=SELECT_STT_RESULTS, params={"file_id": stt_model.file_id}
    )

    if not user_info:
        raise HTTPException(status_code=404, detail="Users not found")

    return user_info


@router.post("/create-wordcloud/", tags=["stt_results"])
async def generate_wordcloud(wordcloud_model: WordcloudModel):
    """워드클라우드를 생성하는 엔드포인트(현재 2개의 파일은 보여지는것 구현x)"""
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
    return FileResponse(image_path)


@router.post("/image_files/images/", tags=["stt_results"])
async def get_images(imagefilemodel: ImagefileModel):
    """
    images를 가져오는 엔드포인트
    """

    image_files_path = execute_select_query(
        query=SELECT_IMAGE_FILES,
        params={
            "user_id": imagefilemodel.user_id,
            "start_date": imagefilemodel.start_date,
            "end_date": imagefilemodel.end_date,
            "type": imagefilemodel.type,
        },
    )

    if not image_files_path:
        raise HTTPException(status_code=404, detail="files not found")

    # zip파일로 묶어서 전송
    zip_path = "../backend/app/image/image.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        for image_dict in image_files_path:
            img_path = image_dict["image_path"]
            if os.path.exists(img_path):
                z.write(img_path, os.path.basename(img_path))
            else:
                raise HTTPException(
                    status_code=404, detail=f"File not found: {img_path}"
                )

    # Return the zip file as a response
    return FileResponse(zip_path, media_type="application/zip", filename="images.zip")


@router.post("/image_files/image_type/", tags=["stt_results"])
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

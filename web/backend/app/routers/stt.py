from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import date

import zipfile
import os

from app.database.query import (
    SELECT_STT_RESULTS,
    SELECT_STT_RESULTS_FOR_IMAGE,
    SELECT_IMAGE_FILES,
    SELECT_IMAGE_TYPE,
    UPDATE_STT_TEXT,
    UPDATE_STT_SPEAKER,
    UPDATE_STT_EDIT_TEXT,
    INCREASE_INDEX,
    ADD_SELECTED_INDEX_DATA,
    CALLBACK_INDEX,
)
from app.database.worker import execute_select_query, execute_insert_update_query_single
from app.services.gen_wordcloud import create_wordcloud, FONT_PATH, violin_chart

router = APIRouter()


class FileModel(BaseModel):
    file_id: str


@router.post("/stt-results-by-file_id/", tags=["stt_results"])
async def get_stt_results_by_file_id(stt_model: FileModel):
    """file_id별로 stt result를 가져오는 엔드포인트"""
    files_info = execute_select_query(
        query=SELECT_STT_RESULTS, params={"file_id": stt_model.file_id}
    )

    if not files_info:
        raise HTTPException(status_code=404, detail="Users not files_info")

    return files_info


class ImageModel(BaseModel):
    user_id: str
    start_date: date
    end_date: date


@router.post("/create-wordcloud/", tags=["stt_results"])
async def generate_wordcloud(image_model: ImageModel):
    """워드클라우드를 생성하여 이미지 반환하는 엔드포인트(현재 2개의 파일은 보여지는것 구현x)"""
    stt_wordcloud = execute_select_query(
        query=SELECT_STT_RESULTS_FOR_IMAGE,
        params={
            "user_id": image_model.user_id,
            "start_date": image_model.start_date,
            "end_date": image_model.end_date,
        },
    )

    if not stt_wordcloud:
        raise HTTPException(
            status_code=404,
            detail="No STT results found for the specified user and date range.",
        )

    user_id = image_model.user_id
    start_date = image_model.start_date
    end_date = image_model.end_date
    font_path = FONT_PATH

    # 워드클라우드 생성 및 이미지 저장
    type = "wordcloud"
    image_path = create_wordcloud(
        stt_wordcloud, font_path, user_id, start_date, end_date, type
    )
    return FileResponse(image_path)


class ImagefileModel(BaseModel):
    user_id: str
    start_date: date
    end_date: date
    type: str


@router.post("/image_files/images/", tags=["stt_results"])
async def get_images(imagefilemodel: ImagefileModel):
    """
    images를 zip파일로 반환하는 엔드포인트
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


class ImagetypeModel(BaseModel):
    user_id: str
    start_date: date
    end_date: date


@router.post("/image_files/image_type/", tags=["stt_results"])
async def get_image_type(imagetypemodel: ImagetypeModel):
    """
    user_id, start_date, end_date 별로 image_type을 가져오는 엔드포인트
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


@router.post("/create-violinplot/", tags=["stt_results"])
async def generate_violin_chart(image_model: ImageModel):
    """워드클라우드를 생성하여 이미지 반환하는 엔드포인트(현재 2개의 파일은 보여지는것 구현x)"""
    stt_violin_chart = execute_select_query(
        query=SELECT_STT_RESULTS_FOR_IMAGE,
        params={
            "user_id": image_model.user_id,
            "start_date": image_model.start_date,
            "end_date": image_model.end_date,
        },
    )
    user_id = image_model.user_id
    start_date = image_model.start_date
    end_date = image_model.end_date
    type = "violin"
    font_path = FONT_PATH

    if not stt_violin_chart:
        raise HTTPException(
            status_code=404,
            detail="No STT results found for the specified user and date range.",
        )
    image_path = violin_chart(
        stt_violin_chart, user_id, start_date, end_date, type, font_path
    )

    return FileResponse(image_path)


class UpdateText(BaseModel):
    file_id: str
    old_text: str
    new_text: str


@router.post("/stt_results/update_text/", tags=["stt_results"])
async def update_stt_text(update_text_model: UpdateText):
    update_text = execute_insert_update_query_single(
        query=UPDATE_STT_TEXT,
        params={
            "file_id": update_text_model.file_id,
            "old_text": update_text_model.old_text,
            "new_text": update_text_model.new_text,
        },
    )

    if update_text == 0:
        raise HTTPException(
            status_code=404, detail="STT result not found or no changes made"
        )

    return {
        "message": "STT result updated successfully",
    }


class UpdateSpeaker(BaseModel):
    file_id: str
    old_speaker: str
    new_speaker: str


@router.post("/stt_results/update_speaker/", tags=["stt_results"])
async def update_stt_text(update_speaker_model: UpdateSpeaker):
    update_speaker = execute_insert_update_query_single(
        query=UPDATE_STT_SPEAKER,
        params={
            "file_id": update_speaker_model.file_id,
            "old_speaker": update_speaker_model.old_speaker,
            "new_speaker": update_speaker_model.new_speaker,
        },
    )

    if update_speaker == 0:
        raise HTTPException(
            status_code=404, detail="STT result not found or no changes made"
        )

    return {
        "message": "STT result updated successfully",
    }


class UpdateTextEdit(BaseModel):
    file_id: str
    index: int
    new_text: str


@router.post("/stt_results/update_text_edit/", tags=["stt_results"])
async def update_stt_text(update_text_edit: UpdateTextEdit):
    text_edit = execute_insert_update_query_single(
        query=UPDATE_STT_EDIT_TEXT,
        params={
            "file_id": update_text_edit.file_id,
            "index": update_text_edit.index,
            "new_text": update_text_edit.new_text,
        },
    )

    if text_edit == 0:
        raise HTTPException(
            status_code=404, detail="STT result not found or no changes made"
        )

    return {
        "message": "STT result updated successfully",
    }


class IncreaseIndex(BaseModel):
    file_id: str
    selected_index: int


@router.post("/stt_results/selected_index_increase/", tags=["stt_results"])
async def update_stt_text(increase_index: IncreaseIndex):
    index_increase = execute_insert_update_query_single(
        query=INCREASE_INDEX,
        params={
            "file_id": increase_index.file_id,
            "selected_index": increase_index.selected_index,
        },
    )

    callback_index = execute_insert_update_query_single(
        query=CALLBACK_INDEX,
        params={
            "file_id": increase_index.file_id,
            "selected_index": increase_index.selected_index,
        },
    )

    if callback_index == 0 or index_increase == 0:
        raise HTTPException(
            status_code=404, detail="STT result not found or no add row"
        )

    return {
        "message": "add row updated successfully",
    }


class AddIndexData(BaseModel):
    file_id: str
    selected_index: int
    new_index: int


@router.post("/stt_results/add_index_data/", tags=["stt_results"])
async def update_stt_text(add_index_data: AddIndexData):
    affected_rows = execute_insert_update_query_single(
        query=ADD_SELECTED_INDEX_DATA,
        params={
            "file_id": add_index_data.file_id,
            "selected_index": add_index_data.selected_index,
            "new_index": add_index_data.new_index,
        },
    )

    if affected_rows == 0:
        raise HTTPException(
            status_code=404, detail="STT result not found or no add row"
        )

    return {
        "message": "add row updated successfully",
    }

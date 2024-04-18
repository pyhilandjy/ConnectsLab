from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from app.database.query import SELECT_STT_RESULTS
from app.database.worker import execute_select_query

router = APIRouter()

@router.get("/", tags=["stt_results"])
async def get_users():
    """stt result를 가져오는 엔드포인트"""
    user_info = execute_select_query(
        query=SELECT_STT_RESULTS,
    )

    if not user_info:
        raise HTTPException(status_code=404, detail="Users not found")

    return user_info
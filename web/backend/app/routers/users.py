from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from app.database.query import SELECT_USERS, LOGIN
from app.database.worker import execute_select_query

router = APIRouter()


@router.post("/", tags=["Users"])
async def get_users():
    """유저의 목록을 가져오는 엔드포인트"""
    user_info = execute_select_query(
        query=SELECT_USERS,
    )

    if not user_info:
        raise HTTPException(status_code=404, detail="Users not found")

    return user_info


class LoginInfo(BaseModel):
    id: str


@router.post("/login/", tags=["Users"])
async def login(login_model: LoginInfo):
    """login 하기위한 정보를 가져오는 앤드포인트"""
    login_info = execute_select_query(query=LOGIN, params={"id": login_model.id})
    if not login_info:
        raise HTTPException(status_code=404, detail="Users not found")

    return login_info

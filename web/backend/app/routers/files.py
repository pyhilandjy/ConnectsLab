from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from app.database.query import SELECT_FILES
from app.database.worker import execute_select_query

router = APIRouter()


class FileModel(BaseModel):
    user_id: str


@router.post("/", tags=["Files"])
async def get_files(file_model: FileModel):
    """123"""

    files = execute_select_query(
        query=SELECT_FILES, params={"user_id": file_model.user_id}
    )

    if not files:
        raise HTTPException(status_code=404, detail="files not found")

    return files

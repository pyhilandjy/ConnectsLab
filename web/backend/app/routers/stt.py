from datetime import datetime

from fastapi import APIRouter, FastAPI, File, HTTPException, Form



router = APIRouter()

@router.get("/", tags=["STT"])
async def stt():
    pass

app = FastAPI()
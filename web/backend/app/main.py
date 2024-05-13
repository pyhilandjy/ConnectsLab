from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.routers import audio, users, stt, files
from app.services.api import get_api_key


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(audio.router, prefix="/audio", dependencies=[Depends(get_api_key)])
app.include_router(users.router, prefix="/users", dependencies=[Depends(get_api_key)])
app.include_router(files.router, prefix="/files", dependencies=[Depends(get_api_key)])
app.include_router(stt.router, prefix="/stt", dependencies=[Depends(get_api_key)])


@app.get("/")
async def home():
    return {"status": "ok"}

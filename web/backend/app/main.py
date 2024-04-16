from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import audio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio.router, prefix="/audio")

@app.get("/")
async def home():
    return {"status": "ok"}

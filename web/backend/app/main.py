from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import audio, users


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(audio.router, prefix="/audio")
app.include_router(users.router, prefix="/users")


@app.get("/")
async def home():
    return {"status": "ok"}

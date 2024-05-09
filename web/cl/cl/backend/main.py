from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import audio, users, stt, files


app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# app.include_router(audio.router, prefix="/audio")
# app.include_router(users.router, prefix="/users")
# app.include_router(files.router, prefix="/files")
# app.include_router(stt.router, prefix="/stt")


# @app.get("/")
# async def home():
#     return {"status": "ok"}

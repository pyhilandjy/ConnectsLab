from fastapi import (
    APIRouter,
    FastAPI,
    File,
    UploadFile,
    HTTPException,
    Form,
    BackgroundTasks,
)

from app.services import (
    save_file,
    gen_file_id,
    gen_file_path,
    create_metadata,
    insert_file_metadata,
    get_stt_results,
    insert_stt_segments,
)


router = APIRouter()
app = FastAPI()


# ClovaSpeechClient()


@router.post("/uploadfile/", tags=["Audio"])
async def create_upload_file(user_id: str = Form(...), file: UploadFile = File(...)):
    try:
        file_id = gen_file_id(user_id)
        file_path = gen_file_path(file_id)
        await save_file(file, file_path)

        metadata = create_metadata(file_id, user_id, file.filename, file_path)
        insert_file_metadata(metadata)

        segments = get_stt_results(file_path)

        return insert_stt_segments(segments, file_id)

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


# @router.post("/uploadfile/", tags=["Audio"])
# async def create_upload_file(
#     background_tasks: BackgroundTasks,
#     user_id: str = Form(...),
#     file: UploadFile = File(...),
#     clova_client: ClovaSpeechClient = Depends(get_clova_client)
# ):
#     try:
#         file_id = gen_file_id(user_id)
#         file_path = gen_file_path(file_id)
#         await save_file(file, file_path)

#         metadata = create_metadata(file_id, user_id, file.filename, file_path)
#         insert_file_metadata(metadata)

#         # stt_results 함수를 백그라운드 작업으로 추가
#         stt = stt_response(clova_client, file_path, file_id)


#         return stt

#     except Exception as e:
#         print(f"Error occurred: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

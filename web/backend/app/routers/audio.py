from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    Form,
    BackgroundTasks,
)

from app.services.stt import (
    save_audio_file,
    gen_audio_file_id,
    gen_audio_file_path,
    create_audio_metadata,
    insert_audio_file_metadata,
    get_stt_results,
    insert_stt_segments,
    explode,
    rename_keys,
)


router = APIRouter()


@router.post("/uploadfile/", tags=["Audio"])
async def create_upload_file(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    file: UploadFile = File(...),
):
    try:
        file_id = gen_audio_file_id(user_id)
        file_path = gen_audio_file_path(file_id)
        await save_audio_file(file, file_path)

        metadata = create_audio_metadata(file_id, user_id, file.filename, file_path)
        insert_audio_file_metadata(metadata)

        # 백그라운드 태스크로 STT 처리 및 결과 삽입
        background_tasks.add_task(process_stt_and_insert, file_path, file_id)

        return {"message": "File uploaded and processing started in the background."}
    except Exception as e:
        return {"error": str(e)}


async def process_stt_and_insert(file_path, file_id):
    segments = get_stt_results(file_path)
    rename_segments = rename_keys(segments)
    explode_segments = explode(rename_segments, "textEdited")
    return insert_stt_segments(explode_segments, file_id)

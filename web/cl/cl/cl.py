import reflex as rx
import requests
from cl.router.app import api_test
from fastapi.middleware.cors import CORSMiddleware

from cl.backend.routers import audio, users, stt, files


# 상태 관리 클래스
class FormState(rx.State):
    form_data = {}

    async def handle_submit(cls, form_data):
        cls.form_data = form_data
        file_id = form_data.get("file_id", "")

        if file_id:
            try:
                # FastAPI 엔드포인트에 POST 요청을 보냅니다.
                response = requests.post(
                    "http://localhost:8000/stt/results-by-file_id/",
                    json={"file_id": file_id},
                )

                if response.ok:
                    cls.stt_results = response.json()
                else:
                    cls.stt_results = []  # 오류가 있거나 데이터가 없을 때 빈 목록
            except Exception as e:
                print(f"Error fetching STT results: {e}")
                cls.stt_results = []


# 폼 UI 컴포넌트 구성
def index():
    return rx.vstack(
        rx.form(
            rx.vstack(
                rx.input(
                    placeholder="File ID",
                    name="file_id",
                ),
                rx.button("Submit", type="submit"),
            ),
            on_submit=FormState.handle_submit,
            reset_on_submit=True,
        ),
        rx.divider(),
        rx.heading("Results"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.cell("id"),
                    rx.table.cell("file_id"),
                    rx.table.cell("index"),
                    rx.table.cell("start_time"),
                    rx.table.cell("end_time"),
                    rx.table.cell("text"),
                    rx.table.cell("confidence"),
                    rx.table.cell("speaker_label"),
                    rx.table.cell("text_edited"),
                    rx.table.cell("created_at"),
                    rx.table.cell("stt_status"),
                    rx.table.cell("act_id"),
                )
            ),
            rx.table.body(
                rx.foreach(
                    FormState.handle_submit,
                    lambda result: rx.table.row(
                        rx.table.cell(result.get("id")),
                        rx.table.cell(result.get("file_id")),
                        rx.table.cell(result.get("index")),
                        rx.table.cell(result.get("start_time")),
                        rx.table.cell(result.get("end_time")),
                        rx.table.cell(result.get("text")),
                        rx.table.cell(result.get("confidence")),
                        rx.table.cell(result.get("speaker_label")),
                        rx.table.cell(result.get("text_edited")),
                        rx.table.cell(result.get("created_at")),
                        rx.table.cell(result.get("stt_status")),
                        rx.table.cell(result.get("act_id")),
                    ),
                )
            ),
        ),
    )


# 앱 설정
app = rx.App()
app.api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.api.include_router(audio.router, prefix="/audio")
app.api.include_router(users.router, prefix="/users")
app.api.include_router(files.router, prefix="/files")
app.api.include_router(stt.router, prefix="/stt")
app.api.add_api_route("/items/{item_id}", api_test)
app.add_page(index)

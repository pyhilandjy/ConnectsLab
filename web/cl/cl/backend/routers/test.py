from pydantic import BaseModel
from datetime import date

from sqlalchemy import text


from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgresql_url: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


class DBConnection:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    @contextmanager
    def get_db(self):
        db_session = self.SessionLocal()
        try:
            yield db_session
        finally:
            db_session.close()


postgresql_connection = DBConnection(settings.postgresql_url)


SELECT_STT_RESULTS_FOR_IMAGE = text(
    """
    SELECT sr.*
    FROM stt_results sr
    JOIN files f ON sr.file_id = f.id
    WHERE f.user_id = :user_id
        AND sr.created_at BETWEEN :start_date AND :end_date
    ORDER BY sr.created_at ASC, sr.index ASC
    """
)


def execute_select_query(query: str, params: dict = None) -> list:
    """
    SELECT 쿼리를 실행합니다.
    :param connection: DB 연결 객체.
    :type connection: DBConnection

    :param query: 실행할 쿼리.
    :type query: str

    :param params: 쿼리 파라미터.
    :type params: dict

    :return: 쿼리 결과.
    :rtype: list
    """
    with postgresql_connection.get_db() as db:
        result = db.execute(query, params)
        return [record for record in result.mappings()]


class ImageModel(BaseModel):
    user_id: str
    start_date: date
    end_date: date


def generate_violin_chart(image_model: ImageModel):
    """워드클라우드를 생성하여 이미지 반환하는 엔드포인트(현재 2개의 파일은 보여지는것 구현x)"""
    stt_violin_chart = execute_select_query(
        query=SELECT_STT_RESULTS_FOR_IMAGE,
        params={
            "user_id": image_model.user_id,
            "start_date": image_model.start_date,
            "end_date": image_model.end_date,
        },
    )
    return stt_violin_chart


stt_violin_chart = generate_violin_chart()
stt_violin_chart

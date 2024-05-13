from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgresql_url: str
    clova_invoke_url: str
    clova_secret: str
    api_name: str
    api_key: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "AI Video Studio"
    debug: bool = False
    database_url: str = "sqlite:///./test.db"
    api_key: str = ""

    class Config:
        env_file = ".env"

settings = Settings()

from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings

PROJECT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    # DEBUG
    DEBUG: bool

    # SECURITY
    SECRET_KEY: str

    # PROJECT DETAILS
    PROJECT_NAME: str
    CORS_ALLOWED_ORIGINS: Union[List, str]

    # POSTGRESQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URL: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URL", mode="before")
    def assemble_postgres_connection(
        cls, v: Optional[str], info: Dict[str, str]
    ) -> str:
        values = info.data

        # Assemble postgres url
        if isinstance(v, str):
            return v
        if values.get("DEBUG"):
            postgres_server = "localhost"
        else:
            postgres_server = values.get("POSTGRES_SERVER")

        return str(
            AnyUrl.build(
                scheme="postgresql+psycopg",
                username=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                host=postgres_server or "localhost",
                port=values.get("POSTGRES_PORT"),
                path=values.get("POSTGRES_DB"),
            )
        )

    @field_validator("CORS_ALLOWED_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v):
        return v.split()

    class Config:
        env_file = f"{PROJECT_DIR}/.env"
        case_sensitive = True


settings: Settings = Settings()

from pydantic_settings import BaseSettings


class DevelopConfig(BaseSettings):
    DATABASE_URL: str
    ALEMBIC_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"
        from_attribute = True


settings = DevelopConfig()

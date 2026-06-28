from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GITHUB_TOKEN: str = ""
    GITHUB_USERNAME: str = "GuilhermeNascimento-bit"
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 300  # 5 minutes

    class Config:
        env_file = ".env"


settings = Settings()

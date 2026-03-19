"""
앱 설정 관리 모듈
환경변수를 읽어 설정 객체로 제공
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Gemini AI API 키
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")

    # 데이터베이스 연결 URL (기본값: SQLite)
    database_url: str = Field(
        default="sqlite+aiosqlite:///./jobradar.db",
        env="DATABASE_URL"
    )

    # JWT 시크릿 키
    secret_key: str = Field(..., env="SECRET_KEY")

    # JWT 알고리즘
    algorithm: str = "HS256"

    # 액세스 토큰 만료 시간 (분)
    access_token_expire_minutes: int = 60 * 24  # 24시간

    # 디버그 모드
    debug: bool = Field(default=False, env="DEBUG")

    # 채용공고 수집 주기 (분)
    collect_interval_minutes: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 전역 설정 인스턴스
settings = Settings()

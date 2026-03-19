"""
채용공고 관련 Pydantic 스키마
API 요청/응답 직렬화 및 유효성 검사
"""
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


class JobResponse(BaseModel):
    """채용공고 응답 스키마"""
    id: int
    title: str
    company: str
    location: str | None
    salary: str | None
    description: str | None
    url: str
    platform: str
    deadline: datetime | None
    collected_at: datetime

    model_config = {"from_attributes": True}


class JobMatchResponse(BaseModel):
    """채용공고 매칭 결과 응답 스키마"""
    id: int
    job_id: int
    user_id: int
    match_score: float
    match_reason: str | None
    is_bookmarked: bool
    created_at: datetime

    # 연관된 채용공고 정보 포함
    job: JobResponse | None = None

    model_config = {"from_attributes": True}


class ResumeUpload(BaseModel):
    """이력서 텍스트 업로드 스키마"""
    resume_text: str = Field(
        ...,
        min_length=50,
        max_length=10000,
        description="이력서 전문 텍스트 (최소 50자)"
    )
    skills: str | None = Field(
        default=None,
        description="보유 기술 (쉼표 구분, 예: Python,FastAPI,React)"
    )
    desired_salary: int | None = Field(
        default=None,
        ge=0,
        description="희망 연봉 (만원 단위)"
    )
    desired_location: str | None = Field(
        default=None,
        max_length=100,
        description="희망 근무지"
    )


class JobSearchParams(BaseModel):
    """채용공고 검색 파라미터"""
    keyword: str | None = None
    location: str | None = None
    platform: str | None = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)

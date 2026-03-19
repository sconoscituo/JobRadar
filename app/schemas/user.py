"""
사용자 관련 Pydantic 스키마
회원가입/로그인/이력서 업데이트 요청 및 응답
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """회원가입 요청 스키마"""
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="비밀번호 (최소 8자)"
    )


class UserResponse(BaseModel):
    """사용자 정보 응답 스키마"""
    id: int
    email: str
    skills: str | None
    desired_salary: int | None
    desired_location: str | None
    is_premium: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT 토큰 응답 스키마"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT 페이로드 데이터"""
    email: str | None = None


class ResumeUpdate(BaseModel):
    """이력서 업데이트 요청 스키마"""
    resume_text: str | None = Field(
        default=None,
        min_length=50,
        max_length=10000,
        description="이력서 전문 텍스트"
    )
    skills: str | None = Field(
        default=None,
        description="보유 기술 (쉼표 구분)"
    )
    desired_salary: int | None = Field(
        default=None,
        ge=0,
        description="희망 연봉 (만원)"
    )
    desired_location: str | None = Field(
        default=None,
        max_length=100,
        description="희망 근무지"
    )


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    email: EmailStr
    password: str

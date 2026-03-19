"""
사용자 모델
이메일 기반 인증 + 이력서 정보 저장
"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 인증 정보
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # 이력서 정보 (텍스트 전체)
    resume_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 보유 기술 (쉼표 구분 문자열, 예: "Python,FastAPI,React")
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 희망 연봉 (만원 단위)
    desired_salary: Mapped[int | None] = mapped_column(nullable=True)

    # 희망 근무지 (예: "서울", "재택")
    desired_location: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # 프리미엄 구독 여부
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)

    # 계정 활성화 여부
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # 가입 일시
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"

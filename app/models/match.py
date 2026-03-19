"""
채용공고-사용자 매칭 결과 모델
Gemini API가 산출한 적합도 점수 및 분석 이유 저장
"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class JobMatch(Base):
    __tablename__ = "job_matches"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 채용공고 외래키
    job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 사용자 외래키
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 매칭 점수 (0.0 ~ 100.0)
    match_score: Mapped[float] = mapped_column(Float, nullable=False)

    # 매칭 분석 이유 (Gemini가 생성한 텍스트)
    match_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 북마크 여부
    is_bookmarked: Mapped[bool] = mapped_column(Boolean, default=False)

    # 매칭 생성 일시
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # 관계 정의
    job = relationship("Job", lazy="select")
    user = relationship("User", lazy="select")

    def __repr__(self) -> str:
        return f"<JobMatch id={self.id} job_id={self.job_id} user_id={self.user_id} score={self.match_score}>"

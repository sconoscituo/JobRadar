"""
채용공고 모델
잡코리아/사람인/원티드 RSS에서 수집한 채용 정보
"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    # 기본 키
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 공고 제목
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)

    # 회사명
    company: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # 근무지
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # 연봉 정보 (텍스트, 예: "3,000~4,000만원")
    salary: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # 공고 상세 내용 (주요 업무, 자격요건 등)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 원본 공고 URL
    url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)

    # 수집 플랫폼 (jobkorea / saramin / wanted)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # 지원 마감일
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # 수집 일시
    collected_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title} company={self.company}>"

"""
데이터베이스 연결 및 세션 관리 모듈
SQLAlchemy 비동기 엔진 사용
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# 비동기 SQLAlchemy 엔진 생성
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # 디버그 모드에서 SQL 쿼리 출력
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

# 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ORM 베이스 클래스
class Base(DeclarativeBase):
    pass


async def init_db():
    """앱 시작 시 테이블 생성"""
    # 모델 임포트 (테이블 등록을 위해 필요)
    from app.models import user, job, match  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """FastAPI 의존성 주입용 DB 세션 제공"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

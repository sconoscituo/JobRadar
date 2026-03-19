"""
JobRadar FastAPI 앱 엔트리포인트
채용공고 자동 수집 스케줄러 + API 라우터 등록
"""
import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import jobs, match, users
from app.services.job_collector import collect_all_jobs

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# APScheduler 인스턴스 (전역)
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 라이프사이클 핸들러"""
    # ---- 시작 ----
    logger.info("JobRadar 서버 시작 중...")

    # DB 테이블 초기화
    await init_db()
    logger.info("데이터베이스 초기화 완료")

    # 스케줄러: 1시간마다 채용공고 수집
    scheduler.add_job(
        collect_all_jobs,
        trigger="interval",
        minutes=settings.collect_interval_minutes,
        id="collect_jobs",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"스케줄러 시작: {settings.collect_interval_minutes}분마다 채용공고 수집")

    # 앱 시작 시 즉시 1회 수집
    try:
        stats = await collect_all_jobs()
        logger.info(f"초기 채용공고 수집 완료: {stats}")
    except Exception as e:
        logger.warning(f"초기 수집 실패 (서버는 계속 실행): {e}")

    yield

    # ---- 종료 ----
    scheduler.shutdown()
    logger.info("JobRadar 서버 종료")


# FastAPI 앱 생성
app = FastAPI(
    title="JobRadar API",
    description="채용공고 자동 수집 + AI 이력서 매칭 서비스",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 설정 (프론트엔드 연동용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(match.router)


@app.get("/health", tags=["system"])
async def health_check():
    """헬스체크 엔드포인트 (Docker healthcheck용)"""
    return {"status": "ok", "service": "JobRadar"}


@app.get("/", tags=["system"])
async def root():
    """루트 엔드포인트"""
    return {
        "message": "JobRadar API",
        "docs": "/docs",
        "version": "1.0.0",
    }

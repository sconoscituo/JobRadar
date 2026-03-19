"""
매칭 라우터
이력서 기반 채용공고 적합도 분석 요청 및 결과 조회
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.job import Job
from app.models.match import JobMatch
from app.models.user import User
from app.schemas.job import JobMatchResponse
from app.services.matcher import analyze_match
from app.utils.auth import get_current_user

router = APIRouter(prefix="/match", tags=["match"])


@router.post("/{job_id}", response_model=JobMatchResponse)
async def request_match(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    특정 채용공고와 내 이력서 매칭 분석 요청
    - 무료: 매칭 점수만 반환
    - 프리미엄: 상세 분석 이유 포함
    """
    # 이력서 등록 여부 확인
    if not current_user.resume_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="이력서를 먼저 등록해주세요. PUT /users/me/resume"
        )

    # 채용공고 존재 확인
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="채용공고를 찾을 수 없습니다."
        )

    # 기존 매칭 결과 조회 (재분석 방지)
    existing_result = await db.execute(
        select(JobMatch).where(
            JobMatch.job_id == job_id,
            JobMatch.user_id == current_user.id,
            JobMatch.match_score > 0,
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        return existing

    # Gemini API로 매칭 분석 수행
    score, reason = await analyze_match(
        resume_text=current_user.resume_text,
        job_title=job.title,
        job_description=job.description or "",
        is_premium=current_user.is_premium,
    )

    # 결과 저장
    match = JobMatch(
        job_id=job_id,
        user_id=current_user.id,
        match_score=score,
        match_reason=reason,
    )
    db.add(match)
    await db.flush()
    await db.refresh(match)
    return match


@router.get("/results/me", response_model=list[JobMatchResponse])
async def my_match_results(
    min_score: float = Query(default=0.0, ge=0.0, le=100.0, description="최소 매칭 점수 필터"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """내 매칭 분석 결과 목록 조회 (점수 내림차순)"""
    offset = (page - 1) * size
    result = await db.execute(
        select(JobMatch)
        .where(
            JobMatch.user_id == current_user.id,
            JobMatch.match_score >= min_score,
        )
        .order_by(JobMatch.match_score.desc())
        .offset(offset)
        .limit(size)
    )
    matches = result.scalars().all()
    return matches


@router.post("/analyze-all", status_code=status.HTTP_202_ACCEPTED)
async def analyze_all_jobs(
    top_n: int = Query(default=10, ge=1, le=50, description="분석할 최신 공고 수"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    최신 채용공고 N개를 일괄 매칭 분석 (백그라운드)
    프리미엄 전용 기능
    """
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="일괄 분석은 프리미엄 구독 전용 기능입니다."
        )

    if not current_user.resume_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="이력서를 먼저 등록해주세요."
        )

    # 최신 채용공고 조회
    jobs_result = await db.execute(
        select(Job).order_by(Job.collected_at.desc()).limit(top_n)
    )
    jobs = jobs_result.scalars().all()

    analyzed_count = 0
    for job in jobs:
        # 이미 분석된 공고 건너뜀
        existing = await db.execute(
            select(JobMatch).where(
                JobMatch.job_id == job.id,
                JobMatch.user_id == current_user.id,
                JobMatch.match_score > 0,
            )
        )
        if existing.scalar_one_or_none():
            continue

        score, reason = await analyze_match(
            resume_text=current_user.resume_text,
            job_title=job.title,
            job_description=job.description or "",
            is_premium=True,
        )

        match = JobMatch(
            job_id=job.id,
            user_id=current_user.id,
            match_score=score,
            match_reason=reason,
        )
        db.add(match)
        analyzed_count += 1

    await db.flush()
    return {"analyzed": analyzed_count, "message": f"{analyzed_count}개 공고 분석 완료"}

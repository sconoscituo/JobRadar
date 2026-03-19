"""
채용공고 라우터
목록 조회, 키워드 검색, 상세 조회, 북마크 토글
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.database import get_db
from app.models.job import Job
from app.models.match import JobMatch
from app.models.user import User
from app.schemas.job import JobResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=list[JobResponse])
async def list_jobs(
    keyword: str | None = Query(default=None, description="검색 키워드 (제목/회사명)"),
    location: str | None = Query(default=None, description="근무지 필터"),
    platform: str | None = Query(default=None, description="플랫폼 필터 (jobkorea/saramin/wanted)"),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    size: int = Query(default=20, ge=1, le=100, description="페이지 크기"),
    db: AsyncSession = Depends(get_db),
):
    """채용공고 목록 조회 (검색/필터 지원)"""
    query = select(Job).order_by(Job.collected_at.desc())

    # 키워드 검색 (제목 또는 회사명)
    if keyword:
        query = query.where(
            or_(
                Job.title.ilike(f"%{keyword}%"),
                Job.company.ilike(f"%{keyword}%"),
            )
        )

    # 근무지 필터
    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))

    # 플랫폼 필터
    if platform:
        query = query.where(Job.platform == platform)

    # 페이지네이션
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    result = await db.execute(query)
    jobs = result.scalars().all()
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """채용공고 상세 조회"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="채용공고를 찾을 수 없습니다."
        )
    return job


@router.post("/{job_id}/bookmark", status_code=status.HTTP_200_OK)
async def toggle_bookmark(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """채용공고 북마크 토글 (추가/해제)"""
    # 채용공고 존재 확인
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="채용공고를 찾을 수 없습니다."
        )

    # 기존 매칭 레코드 조회
    match_result = await db.execute(
        select(JobMatch).where(
            JobMatch.job_id == job_id,
            JobMatch.user_id == current_user.id,
        )
    )
    match = match_result.scalar_one_or_none()

    if match:
        # 북마크 상태 토글
        match.is_bookmarked = not match.is_bookmarked
        db.add(match)
        bookmarked = match.is_bookmarked
    else:
        # 매칭 레코드가 없으면 북마크로 새로 생성 (점수 0)
        new_match = JobMatch(
            job_id=job_id,
            user_id=current_user.id,
            match_score=0.0,
            is_bookmarked=True,
        )
        db.add(new_match)
        bookmarked = True

    await db.flush()
    return {"bookmarked": bookmarked, "job_id": job_id}


@router.get("/bookmarks/me", response_model=list[JobResponse])
async def my_bookmarks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """내 북마크 채용공고 목록 조회"""
    result = await db.execute(
        select(Job)
        .join(JobMatch, Job.id == JobMatch.job_id)
        .where(
            JobMatch.user_id == current_user.id,
            JobMatch.is_bookmarked == True,  # noqa: E712
        )
        .order_by(JobMatch.created_at.desc())
    )
    jobs = result.scalars().all()
    return jobs

"""
채용공고 수집 서비스
잡코리아, 사람인, 원티드 RSS/HTTP 파싱으로 채용공고 자동 수집
"""
import asyncio
import logging
from datetime import datetime

import feedparser
import httpx
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.job import Job

logger = logging.getLogger(__name__)

# RSS 피드 URL 목록 (플랫폼별)
RSS_FEEDS = {
    "saramin": [
        "https://www.saramin.co.kr/zf_user/rss/default",
        "https://www.saramin.co.kr/zf_user/rss/it",
    ],
    "wanted": [
        "https://www.wanted.co.kr/rss",
    ],
    "jobkorea": [
        "https://www.jobkorea.co.kr/rss/it.xml",
    ],
}

# HTTP 요청 헤더 (봇 차단 우회)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


async def fetch_rss_feed(url: str, platform: str) -> list[dict]:
    """
    단일 RSS 피드 URL에서 채용공고 파싱
    반환값: 채용공고 딕셔너리 리스트
    """
    jobs = []
    try:
        async with httpx.AsyncClient(timeout=15.0, headers=HEADERS, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

        # feedparser로 RSS 파싱
        feed = feedparser.parse(response.text)

        for entry in feed.entries:
            # 설명에서 HTML 태그 제거
            raw_desc = getattr(entry, "summary", "") or getattr(entry, "description", "")
            description = BeautifulSoup(raw_desc, "html.parser").get_text(separator=" ").strip()

            # 마감일 파싱 시도
            deadline = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    deadline = datetime(*entry.published_parsed[:6])
                except Exception:
                    pass

            job_data = {
                "title": getattr(entry, "title", "제목 없음").strip(),
                "company": _extract_company(entry, platform),
                "location": _extract_location(entry, platform),
                "salary": None,
                "description": description[:2000] if description else None,  # 2000자 제한
                "url": getattr(entry, "link", ""),
                "platform": platform,
                "deadline": deadline,
            }

            # URL이 없으면 건너뜀
            if not job_data["url"]:
                continue

            jobs.append(job_data)

    except httpx.HTTPError as e:
        logger.warning(f"[{platform}] RSS 피드 요청 실패: {url} - {e}")
    except Exception as e:
        logger.error(f"[{platform}] RSS 파싱 오류: {url} - {e}")

    return jobs


def _extract_company(entry, platform: str) -> str:
    """플랫폼별 회사명 추출"""
    # 사람인: author 필드에 회사명
    if hasattr(entry, "author") and entry.author:
        return entry.author.strip()
    # 태그에서 추출 시도
    if hasattr(entry, "tags"):
        for tag in entry.tags:
            if "company" in tag.get("term", "").lower():
                return tag.get("label", "").strip()
    return "회사명 미상"


def _extract_location(entry, platform: str) -> str | None:
    """플랫폼별 근무지 추출"""
    # 태그에서 location 추출 시도
    if hasattr(entry, "tags"):
        for tag in entry.tags:
            term = tag.get("term", "").lower()
            if "location" in term or "지역" in term:
                return tag.get("label", "").strip()
    return None


async def save_jobs(jobs: list[dict], db: AsyncSession) -> int:
    """
    수집된 채용공고를 DB에 저장 (중복 URL 건너뜀)
    반환값: 새로 저장된 공고 수
    """
    saved_count = 0
    for job_data in jobs:
        # URL 중복 검사
        result = await db.execute(select(Job).where(Job.url == job_data["url"]))
        if result.scalar_one_or_none():
            continue  # 이미 존재하면 건너뜀

        job = Job(**job_data)
        db.add(job)
        saved_count += 1

    if saved_count > 0:
        await db.flush()

    return saved_count


async def collect_all_jobs() -> dict:
    """
    모든 플랫폼에서 채용공고 수집 (스케줄러에서 호출)
    반환값: 플랫폼별 수집/저장 통계
    """
    stats = {}
    all_jobs = []

    # 병렬로 모든 RSS 피드 수집
    tasks = []
    for platform, urls in RSS_FEEDS.items():
        for url in urls:
            tasks.append((platform, fetch_rss_feed(url, platform)))

    # asyncio.gather로 병렬 실행
    results = await asyncio.gather(
        *[coro for _, coro in tasks],
        return_exceptions=True,
    )

    for (platform, _), result in zip(tasks, results):
        if isinstance(result, Exception):
            logger.error(f"[{platform}] 수집 중 예외 발생: {result}")
            continue
        stats.setdefault(platform, {"fetched": 0, "saved": 0})
        stats[platform]["fetched"] += len(result)
        all_jobs.extend(result)

    # DB 저장
    async with AsyncSessionLocal() as db:
        for platform in RSS_FEEDS:
            platform_jobs = [j for j in all_jobs if j["platform"] == platform]
            saved = await save_jobs(platform_jobs, db)
            stats.setdefault(platform, {"fetched": 0, "saved": 0})
            stats[platform]["saved"] = saved
        await db.commit()

    total_saved = sum(s.get("saved", 0) for s in stats.values())
    logger.info(f"채용공고 수집 완료: 총 {total_saved}개 저장 | 상세: {stats}")
    return stats

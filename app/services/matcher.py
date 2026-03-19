"""
Gemini API 기반 이력서-채용공고 매칭 서비스
적합도 점수(0~100) 및 분석 이유 생성
"""
import json
import logging
import re

import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)

# Gemini API 초기화
genai.configure(api_key=settings.gemini_api_key)

# 사용 모델 (gemini-pro: 무료 티어 지원)
_model = genai.GenerativeModel("gemini-pro")

# 무료 사용자용 프롬프트 (점수만 반환)
_FREE_PROMPT_TEMPLATE = """
다음 이력서와 채용공고를 분석하여 적합도 점수를 0~100 사이의 정수로만 반환하세요.
다른 텍스트 없이 숫자만 반환하세요.

[이력서]
{resume}

[채용공고 제목]
{job_title}

[채용공고 내용]
{job_desc}

적합도 점수 (0~100 정수만):
"""

# 프리미엄 사용자용 프롬프트 (JSON 응답)
_PREMIUM_PROMPT_TEMPLATE = """
다음 이력서와 채용공고를 분석하여 아래 JSON 형식으로만 응답하세요.

[이력서]
{resume}

[채용공고 제목]
{job_title}

[채용공고 내용]
{job_desc}

응답 JSON 형식:
{{
  "score": <0~100 정수>,
  "reason": "<한국어로 3~5문장의 매칭 분석. 강점, 부족한 점, 추천 이유 포함>"
}}

JSON만 반환하세요:
"""


async def analyze_match(
    resume_text: str,
    job_title: str,
    job_description: str,
    is_premium: bool = False,
) -> tuple[float, str | None]:
    """
    Gemini API로 이력서와 채용공고 매칭 분석
    반환값: (매칭 점수 0.0~100.0, 분석 이유 또는 None)
    """
    # 이력서 길이 제한 (토큰 절약)
    resume_truncated = resume_text[:3000]
    job_desc_truncated = job_description[:1500]

    try:
        if is_premium:
            return await _analyze_premium(resume_truncated, job_title, job_desc_truncated)
        else:
            return await _analyze_free(resume_truncated, job_title, job_desc_truncated)

    except Exception as e:
        logger.error(f"Gemini API 매칭 분석 오류: {e}")
        # API 오류 시 기본값 반환 (서비스 중단 방지)
        return 0.0, None


async def _analyze_free(resume: str, job_title: str, job_desc: str) -> tuple[float, None]:
    """무료 사용자: 점수만 분석"""
    prompt = _FREE_PROMPT_TEMPLATE.format(
        resume=resume,
        job_title=job_title,
        job_desc=job_desc,
    )

    response = _model.generate_content(prompt)
    text = response.text.strip()

    # 숫자만 추출
    numbers = re.findall(r"\d+", text)
    if numbers:
        score = max(0.0, min(100.0, float(numbers[0])))
    else:
        logger.warning(f"점수 파싱 실패, 응답: {text[:100]}")
        score = 0.0

    return score, None


async def _analyze_premium(resume: str, job_title: str, job_desc: str) -> tuple[float, str]:
    """프리미엄 사용자: 점수 + 상세 분석 이유"""
    prompt = _PREMIUM_PROMPT_TEMPLATE.format(
        resume=resume,
        job_title=job_title,
        job_desc=job_desc,
    )

    response = _model.generate_content(prompt)
    text = response.text.strip()

    # JSON 파싱
    try:
        # 마크다운 코드블록 제거
        json_text = re.sub(r"```json\s*|\s*```", "", text).strip()
        data = json.loads(json_text)
        score = max(0.0, min(100.0, float(data.get("score", 0))))
        reason = data.get("reason", "분석 결과를 가져올 수 없습니다.")
        return score, reason

    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"프리미엄 JSON 파싱 실패: {e} | 응답: {text[:200]}")
        # JSON 파싱 실패 시 숫자만 추출하여 폴백
        numbers = re.findall(r"\d+", text)
        score = max(0.0, min(100.0, float(numbers[0]))) if numbers else 0.0
        return score, text[:500] if text else None

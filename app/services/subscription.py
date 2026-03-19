"""JobRadar 구독 플랜"""
from enum import Enum

class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"          # 월 6,900원
    RECRUITER = "recruiter"  # 월 29,900원 (채용담당자용)

PLAN_LIMITS = {
    PlanType.FREE:      {"job_alerts": 3,  "ai_match_score": False, "auto_apply": False, "resume_views": 0},
    PlanType.PRO:       {"job_alerts": 50, "ai_match_score": True,  "auto_apply": True,  "resume_views": 10},
    PlanType.RECRUITER: {"job_alerts": 999,"ai_match_score": True,  "auto_apply": True,  "resume_views": 999},
}

PLAN_PRICES_KRW = {PlanType.FREE: 0, PlanType.PRO: 6900, PlanType.RECRUITER: 29900}

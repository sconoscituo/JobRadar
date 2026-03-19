# JobRadar
> 채용공고 자동 수집 + AI 이력서 매칭 서비스

## 개요

JobRadar는 여러 채용 플랫폼에서 공고를 자동으로 수집하고, Gemini AI로 사용자의 이력서와 채용공고를 매칭하여 합격 가능성을 분석하는 서비스입니다.
APScheduler로 주기적으로 채용공고를 수집하고 실시간으로 최신 정보를 제공합니다.

**수익 구조**: 무료 플랜(공고 열람) / 프리미엄 플랜(AI 매칭 + 지원 자동화)

## 기술 스택

- **Backend**: FastAPI 0.104, Python 3.11
- **DB**: SQLAlchemy 2.0 (async) + SQLite (aiosqlite)
- **AI**: Google Gemini API (이력서 매칭, 합격 예측)
- **스크래핑**: httpx, BeautifulSoup4, feedparser
- **스케줄러**: APScheduler 3.10
- **인증**: JWT (python-jose) + bcrypt
- **배포**: Docker + docker-compose

## 시작하기

### 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 다음 값을 설정합니다:

| 변수명 | 설명 |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API 키 |
| `DATABASE_URL` | SQLite DB 경로 (기본값 사용 가능) |
| `SECRET_KEY` | JWT 서명용 시크릿 키 |
| `DEBUG` | 개발 환경 여부 (True/False) |

### 실행 방법

#### Docker (권장)

```bash
docker-compose up -d
```

#### 직접 실행

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

서버 실행 후 http://localhost:8000/docs 에서 API 문서를 확인하세요.

## API 문서

| 메서드 | 엔드포인트 | 설명 |
|---|---|---|
| GET | `/` | 루트 엔드포인트 |
| GET | `/health` | 헬스체크 |
| POST | `/users/register` | 회원가입 |
| POST | `/users/login` | 로그인 (JWT 발급) |
| GET | `/users/me` | 내 정보 조회 |
| PUT | `/users/me/resume` | 이력서 업로드/수정 |
| GET | `/jobs/` | 채용공고 목록 조회 |
| GET | `/jobs/{id}` | 채용공고 상세 조회 |
| GET | `/jobs/search` | 키워드 검색 |
| POST | `/match/analyze` | AI 이력서-공고 매칭 분석 |
| GET | `/match/recommendations` | 맞춤 공고 추천 |

## 수익 구조

- **무료 플랜**: 채용공고 열람 무제한, AI 매칭 월 3회
- **프리미엄 플랜** (월 9,900원): AI 매칭 무제한, 합격률 예측, 이력서 개선 제안, 지원 현황 대시보드
- **기업 채용 광고**: 채용 기업 대상 공고 상단 노출 광고 수익

## 라이선스

MIT

# JobRadar - 프로젝트 설정 가이드

## 프로젝트 소개

JobRadar는 Google Gemini AI와 웹 크롤링(BeautifulSoup, feedparser)을 활용하여 채용공고를 자동 수집·분석하고, 사용자 맞춤 채용 정보를 제공하는 SaaS 서비스입니다. APScheduler를 통해 주기적으로 채용공고를 수집합니다.

- **기술 스택**: FastAPI, SQLAlchemy, SQLite, Google Gemini AI, APScheduler
- **인증**: JWT (python-jose)
- **채용공고 수집 주기**: 기본 60분

---

## 필요한 API 키 / 환경변수

| 환경변수 | 설명 | 발급 URL |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini AI API 키 (필수) | [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| `SECRET_KEY` | JWT 서명용 비밀 키 (필수) | 직접 생성 (`openssl rand -hex 32`) |
| `DATABASE_URL` | DB 연결 URL (기본: SQLite) | - |
| `DEBUG` | 디버그 모드 (`true`/`false`, 기본: `false`) | - |
| `COLLECT_INTERVAL_MINUTES` | 채용공고 수집 주기(분) (기본: `60`) | - |

---

## GitHub Secrets 설정 방법

저장소의 **Settings > Secrets and variables > Actions** 에서 아래 Secrets를 등록합니다.

```
GEMINI_API_KEY     = <Google AI Studio에서 발급한 키>
SECRET_KEY         = <openssl rand -hex 32 으로 생성한 값>
```

---

## 로컬 개발 환경 설정

### 1. 저장소 클론

```bash
git clone https://github.com/sconoscituo/JobRadar.git
cd JobRadar
```

### 2. Python 가상환경 생성 및 의존성 설치

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 환경변수 파일 생성

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite+aiosqlite:///./jobradar.db
DEBUG=true
COLLECT_INTERVAL_MINUTES=60
```

---

## 실행 방법

### 로컬 실행 (uvicorn)

```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 문서 확인: [http://localhost:8000/docs](http://localhost:8000/docs)

### Docker Compose로 실행

```bash
docker-compose up --build
```

### 테스트 실행

```bash
pytest tests/
```

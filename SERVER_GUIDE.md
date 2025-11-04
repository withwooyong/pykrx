# pykrx 웹 API 서버 실행 가이드

## 📋 목차
1. [서버 개요](#서버-개요)
2. [필수 패키지 설치](#필수-패키지-설치)
3. [서버 실행](#서버-실행)
4. [API 엔드포인트](#api-엔드포인트)
5. [사용 예제](#사용-예제)

---

## 🎯 서버 개요

`server.py`는 pykrx 라이브러리의 기능을 REST API로 제공하는 FastAPI 기반 웹 서버입니다.

**주요 기능:**
- 주식 데이터 조회 (OHLCV, 시가총액, 티커 등)
- 지수 데이터 조회
- 채권 데이터 조회
- 투자자별 순매수 데이터 조회
- 자동 API 문서 생성 (Swagger UI)

---

## 📦 필수 패키지 설치

### 1. FastAPI 및 Uvicorn 설치

```bash
# 가상환경 활성화
source .venv/bin/activate

# FastAPI 및 Uvicorn 설치
pip install fastapi uvicorn
```

### 2. requirements.txt 업데이트 (선택사항)

```bash
# requirements.txt에 추가하려면
echo "fastapi==0.115.0" >> requirements.txt
echo "uvicorn[standard]==0.32.1" >> requirements.txt
```

---

## 🚀 서버 실행

### 방법 1: Python 스크립트 직접 실행

```bash
# 가상환경 활성화
source .venv/bin/activate

# 서버 실행
python server.py
```

### 방법 2: Uvicorn 명령어로 실행

```bash
# 가상환경 활성화
source .venv/bin/activate

# 기본 실행 (포트 8000)
uvicorn server:app --reload

# 포트 변경
uvicorn server:app --reload --port 8080

# 호스트 변경 (외부 접근 허용)
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### 방법 3: 백그라운드 실행

```bash
# 백그라운드 실행
nohup uvicorn server:app --reload --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# 프로세스 확인
ps aux | grep uvicorn

# 로그 확인
tail -f server.log

# 서버 종료
pkill -f uvicorn
```

---

## 📚 API 엔드포인트

### 서버 상태 확인

```bash
# 루트 엔드포인트
GET http://localhost:8000/

# 헬스 체크
GET http://localhost:8000/health
```

### 주식 API

#### 1. 티커 리스트 조회
```bash
GET /api/stock/ticker/list?date=20240115&market=KOSPI
```

**파라미터:**
- `date` (str, 선택사항): 조회 일자 (YYYYMMDD), None일 경우 최근 영업일 사용
- `market` (str, 기본값: "KOSPI"): 시장 (KOSPI/KOSDAQ/KONEX/ALL)

#### 2. 티커 이름 조회
```bash
GET /api/stock/ticker/005930/name
```

**파라미터:**
- `ticker` (path variable): 티커 코드 (예: 005930=삼성전자)

#### 3. 일자별 OHLCV 조회
```bash
GET /api/stock/ohlcv/date?fromdate=20240101&todate=20240131&ticker=005930&freq=d
```

**파라미터:**
- `fromdate` (str, 기본값: 30일 전): 시작 일자 (YYYYMMDD)
- `todate` (str, 기본값: 오늘): 종료 일자 (YYYYMMDD)
- `ticker` (str, 기본값: "005930"): 티커 코드
- `freq` (str, 기본값: "d"): 리샘플링 주기 (d=일, m=월, y=년)

#### 4. 티커별 OHLCV 조회
```bash
GET /api/stock/ohlcv/ticker?date=20240115&market=KOSPI
```

**파라미터:**
- `date` (str, 기본값: 오늘): 조회 일자 (YYYYMMDD)
- `market` (str, 기본값: "KOSPI"): 시장 (KOSPI/KOSDAQ/KONEX)

#### 5. 시가총액 조회
```bash
GET /api/stock/market-cap?fromdate=20240101&todate=20240131&ticker=005930
```

**파라미터:**
- `fromdate` (str, 기본값: 30일 전): 시작 일자 (YYYYMMDD)
- `todate` (str, 기본값: 오늘): 종료 일자 (YYYYMMDD)
- `ticker` (str, 기본값: "005930"): 티커 코드

#### 6. 투자자별 순매수 상위종목
```bash
GET /api/stock/net-purchases?fromdate=20240101&todate=20240131&market=ALL&investor=전체
```

**파라미터:**
- `fromdate` (str, 기본값: 30일 전): 시작 일자 (YYYYMMDD)
- `todate` (str, 기본값: 오늘): 종료 일자 (YYYYMMDD)
- `market` (str, 기본값: "ALL"): 시장 (KOSPI/KOSDAQ/KONEX/ALL)
- `investor` (str, 기본값: "전체"): 투자자 (금융투자/보험/투신/사모/은행/기타금융/연기금/기관합계/기타법인/개인/외국인/기타외국인/전체)

### 지수 API

#### 1. 지수 티커 리스트
```bash
GET /api/index/ticker/list?date=20240115&market=KOSPI
```

**파라미터:**
- `date` (str, 선택사항): 조회 일자 (YYYYMMDD), None일 경우 최근 영업일 사용
- `market` (str, 기본값: "KOSPI"): 시장 (KOSPI/KOSDAQ/KRX/테마)

#### 2. 지수 OHLCV 조회
```bash
GET /api/index/ohlcv?fromdate=20240101&todate=20240131&ticker=1001
```

**파라미터:**
- `fromdate` (str, 기본값: 30일 전): 시작 일자 (YYYYMMDD)
- `todate` (str, 기본값: 오늘): 종료 일자 (YYYYMMDD)
- `ticker` (str, 기본값: "1001"): 지수 티커 (예: 1001=코스피)

### 채권 API

#### 1. 국채 수익률 조회
```bash
GET /api/bond/treasury-yields?fromdate=20240101&todate=20240131&ticker=국고채3년
```

**파라미터:**
- `fromdate` (str, 기본값: 30일 전): 시작 일자 (YYYYMMDD)
- `todate` (str, 기본값: 오늘): 종료 일자 (YYYYMMDD)
- `ticker` (str, 기본값: "국고채3년"): 채권 종류
  - 지원 종류: `국고채1년`, `국고채2년`, `국고채3년`, `국고채5년`, `국고채10년`, `국고채20년`, `국고채30년`, `국민주택1종5년`, `회사채AA`, `회사채BBB`, `CD`

---

## 💻 사용 예제

### 1. cURL 사용

```bash
# 티커 리스트 조회
curl "http://localhost:8000/api/stock/ticker/list?date=20240101&market=KOSPI"

# OHLCV 데이터 조회
curl "http://localhost:8000/api/stock/ohlcv/date?fromdate=20240101&todate=20240105&ticker=005930"

# 투자자별 순매수 조회
curl "http://localhost:8000/api/stock/net-purchases?fromdate=20240101&todate=20240131&market=ALL&investor=전체"

# 채권 수익률 조회
curl "http://localhost:8000/api/bond/treasury-yields?fromdate=20240101&todate=20240131&ticker=국고채3년"
```

### 2. Python requests 사용

```python
import requests

BASE_URL = "http://localhost:8000"

# 티커 리스트 조회
response = requests.get(f"{BASE_URL}/api/stock/ticker/list", params={
    "date": "20240101",
    "market": "KOSPI"
})
print(response.json())

# OHLCV 데이터 조회 (기본값 사용 - 파라미터 생략 가능)
response = requests.get(f"{BASE_URL}/api/stock/ohlcv/date")
data = response.json()
print(f"데이터 개수: {len(data['data'])}")

# 채권 수익률 조회
response = requests.get(f"{BASE_URL}/api/bond/treasury-yields", params={
    "fromdate": "20240101",
    "todate": "20240131",
    "ticker": "국고채3년"
})
data = response.json()
print(data)
```

### 3. JavaScript fetch 사용

```javascript
// 티커 리스트 조회
fetch('http://localhost:8000/api/stock/ticker/list?date=20240101&market=KOSPI')
  .then(response => response.json())
  .then(data => console.log(data));

// OHLCV 데이터 조회 (기본값 사용 - 파라미터 생략 가능)
fetch('http://localhost:8000/api/stock/ohlcv/date')
  .then(response => response.json())
  .then(data => console.log(data));

// 채권 수익률 조회
fetch('http://localhost:8000/api/bond/treasury-yields?fromdate=20240101&todate=20240131&ticker=국고채3년')
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## 📖 API 문서 (Swagger UI)

서버 실행 후 브라우저에서 다음 URL로 접속하면 자동 생성된 API 문서를 확인할 수 있습니다:

```
http://localhost:8000/docs
```

**기능:**
- 모든 API 엔드포인트 목록
- 각 엔드포인트의 파라미터 설명 및 기본값 표시
- 직접 API 테스트 가능 (Try it out) - **기본값이 자동으로 채워짐**
- 응답 예제 확인

**기본값 설정:**
- 날짜 파라미터: `fromdate`는 30일 전, `todate`는 오늘 날짜로 자동 설정
- 티커 파라미터: `005930` (삼성전자), `1001` (코스피) 등으로 자동 설정
- 시장 파라미터: `KOSPI`로 자동 설정
- 채권 종류: `국고채3년`으로 자동 설정

**Swagger UI 사용 팁:**
1. `/docs` 페이지에서 원하는 API 클릭
2. "Try it out" 버튼 클릭
3. 파라미터가 기본값으로 자동 채워짐 (필요시 수정 가능)
4. "Execute" 버튼으로 API 호출 테스트

**대체 문서 (ReDoc):**
```
http://localhost:8000/redoc
```

---

## ⚙️ 서버 설정 변경

### server.py 파일 수정

```python
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",      # 호스트 주소 (0.0.0.0 = 모든 인터페이스)
        port=8000,           # 포트 번호
        reload=True,         # 개발 모드: 코드 변경 시 자동 재시작
        log_level="info"     # 로그 레벨 (debug/info/warning/error)
    )
```

### 환경 변수로 설정

```bash
# 포트 변경
export PORT=8080
uvicorn server:app --reload --port $PORT

# 개발/프로덕션 모드
export ENV=development
uvicorn server:app --reload  # 개발 모드
uvicorn server:app --no-reload  # 프로덕션 모드
```

---

## 🔒 보안 고려사항

프로덕션 환경에서는 다음을 고려하세요:

1. **CORS 설정**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Rate Limiting** (API 호출 제한)
```bash
pip install slowapi
```

3. **인증/인가** (JWT 등)
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

---

## 🐛 문제 해결

### 1. 포트가 이미 사용 중

```bash
# 포트 사용 중인 프로세스 확인
lsof -i :8000

# 프로세스 종료
kill -9 <PID>

# 또는 다른 포트 사용
uvicorn server:app --reload --port 8080
```

### 2. ModuleNotFoundError

```bash
# 가상환경 활성화 확인
source .venv/bin/activate

# 패키지 재설치
pip install -r requirements.txt
pip install fastapi uvicorn
```

### 3. 연결 거부 오류

```bash
# 호스트 확인 (0.0.0.0으로 설정)
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# 방화벽 확인 (macOS)
sudo pfctl -f /etc/pf.conf
```

---

## 📝 서버 실행 명령어 요약

```bash
# 1. 가상환경 활성화
source .venv/bin/activate

# 2. 필수 패키지 설치
pip install fastapi uvicorn

# 3. 서버 실행 (기본)
python server.py

# 또는
uvicorn server:app --reload

# 4. 브라우저에서 확인
# http://localhost:8000/docs
```

---

## 🎯 빠른 시작

```bash
# 전체 명령어 (한 번에 실행)
source .venv/bin/activate && \
pip install fastapi uvicorn && \
python server.py
```

서버가 실행되면:
- API 문서: http://localhost:8000/docs
- 서버 상태: http://localhost:8000/


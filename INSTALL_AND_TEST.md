# pykrx 프로젝트 설치 및 테스트 가이드

## 📋 목차
1. [프로젝트 구조](#프로젝트-구조)
2. [가상환경 설정](#가상환경-설정)
3. [의존성 설치](#의존성-설치)
4. [패키지 설치](#패키지-설치)
5. [테스트 실행](#테스트-실행)
6. [실행 예제](#실행-예제)

---

## 🗂️ 프로젝트 구조

```
pykrx/
├── pykrx/              # 메인 패키지
│   ├── stock/          # 주식 관련 API
│   ├── bond/           # 채권 관련 API
│   └── website/        # 웹 스크래핑 모듈
├── tests/               # 테스트 파일들
├── setup.py            # 패키지 설정 파일
├── requirements.txt    # 의존성 목록
└── .venv/              # 가상환경 (생성됨)
```

---

## 🔧 가상환경 설정

### 1단계: 가상환경 생성

```bash
# 프로젝트 루트 디렉토리에서 실행
python3 -m venv .venv
```

### 2단계: 가상환경 활성화

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

가상환경이 활성화되면 터미널 프롬프트에 `(.venv)`가 표시됩니다.

### 3단계: 가상환경 비활성화 (필요시)

```bash
deactivate
```

---

## 📦 의존성 설치

### 방법 1: requirements.txt 사용 (권장)

```bash
# 가상환경 활성화 후
pip install -r requirements.txt
```

### 방법 2: setup.py를 통한 자동 설치

`setup.py`의 `install_requires`에 정의된 패키지들이 자동으로 설치됩니다.

---

## 🚀 패키지 설치

### Editable Install (개발 모드)

개발 중 코드 변경사항이 즉시 반영되도록 하려면 editable install을 사용합니다:

```bash
pip install -e .
```

또는:

```bash
pip install -e /Users/heowooyong/cursor/stock/pykrx
```

이렇게 설치하면:
- 코드 변경사항이 즉시 반영됨
- `from pykrx import stock` 형태로 import 가능
- 테스트 실행 시 자동으로 패키지를 찾을 수 있음

### 일반 설치 (선택사항)

```bash
pip install .
```

---

## 🧪 테스트 실행

### pytest 사용 (권장)

프로젝트는 `pytest`를 사용하도록 변환되었습니다.

#### 1. pytest 설치 확인

```bash
pip install pytest
```

#### 2. 전체 테스트 실행

```bash
# 프로젝트 루트에서 실행
pytest tests/

# 또는 더 자세한 출력
pytest tests/ -v

# 매우 자세한 출력
pytest tests/ -vv
```

#### 3. 특정 테스트 파일 실행

```bash
# 특정 테스트 파일
pytest tests/test_stock_ohlcv.py

# 특정 테스트 클래스
pytest tests/test_stock_ohlcv.py::TestStockOHLCV

# 특정 테스트 함수
pytest tests/test_stock_ohlcv.py::TestStockOHLCV::test_get_market_ohlcv_by_date_with_string_dates
```

#### 4. 테스트 커버리지 확인

```bash
# pytest-cov 설치
pip install pytest-cov

# 커버리지 실행
pytest tests/ --cov=pykrx --cov-report=html
```

#### 5. 테스트 출력 제어

```bash
# 실패한 테스트만 표시
pytest tests/ -v --tb=short

# 모든 출력 표시 (print 문 포함)
pytest tests/ -v -s

# 특정 패턴의 테스트만 실행
pytest tests/ -k "ohlcv" -v
```

### unittest 사용 (레거시)

기존 `unittest` 기반 스크립트도 사용할 수 있습니다:

```bash
# 모든 테스트 실행
python tests/run_all_tests.py

# 특정 테스트 모듈 실행
python tests/run_all_tests.py test_stock_ohlcv
```

---

## 💻 실행 예제

### 1. 기본 사용 예제

```python
# test.py 파일 생성
from pykrx import stock

# 버전 확인
import pykrx
print(f"pykrx version: {pykrx.__version__}")

# 티커 리스트 조회
tickers = stock.get_market_ticker_list("20240101")
print(f"티커 개수: {len(tickers)}")

# OHLCV 데이터 조회
df = stock.get_market_ohlcv_by_date("20240101", "20240105", "005930")
print(df.head())

# 투자자별 순매수 상위종목
df = stock.get_market_net_purchases_of_equities_by_ticker('20210801', '20210831', 'ALL', '기관합계')
print(df.head())
```

### 2. 테스트 코드 실행

```bash
# 가상환경 활성화 후
source .venv/bin/activate

# Python 스크립트 직접 실행
python tests/test.py
```

---

## 🔍 설치 확인

### 패키지 설치 확인

```bash
# 가상환경 활성화 후
python -c "from pykrx import stock; print('✅ 설치 성공')"
```

### 특정 함수 확인

```bash
python -c "from pykrx import stock; print(hasattr(stock, 'get_market_ohlcv_by_date'))"
# 출력: True
```

---

## ⚠️ 문제 해결

### 1. ModuleNotFoundError: No module named 'pykrx'

**원인**: 패키지가 설치되지 않았거나 editable install이 되지 않음

**해결**:
```bash
pip install -e .
```

### 2. ImportError: cannot import name 'xxx'

**원인**: 의존성 패키지가 설치되지 않음

**해결**:
```bash
pip install -r requirements.txt
```

### 3. pytest: command not found

**원인**: pytest가 설치되지 않음

**해결**:
```bash
pip install pytest
```

### 4. 가상환경에서 패키지를 찾을 수 없음

**원인**: 가상환경이 활성화되지 않음

**해결**:
```bash
source .venv/bin/activate  # macOS/Linux
# 또는
.venv\Scripts\activate     # Windows
```

---

## 📝 테스트 파일 목록

- `test_stock_ohlcv.py` - OHLCV 데이터 테스트
- `test_stock_ticker.py` - 티커 관련 테스트
- `test_stock_market_cap.py` - 시가총액 테스트
- `test_stock_business_days.py` - 영업일 테스트
- `test_stock_utils.py` - 유틸리티 함수 테스트
- `test_index_api.py` - 지수 API 테스트
- `test_etf_api.py` - ETF/ETN/ELW API 테스트
- `test_bond_api.py` - 채권 API 테스트
- `test_short_api.py` - 공매도 API 테스트
- `test_market_api.py` - 시장 데이터 API 테스트

---

## 🎯 빠른 시작 명령어 요약

```bash
# 1. 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 패키지 설치 (editable)
pip install -e .

# 4. pytest 설치
pip install pytest

# 5. 테스트 실행
pytest tests/ -v

# 6. 설치 확인
python -c "from pykrx import stock; print('✅ OK')"
```

---

## 📚 추가 정보

- 프로젝트 루트: `/Users/heowooyong/cursor/stock/pykrx`
- Python 버전: 3.x 이상
- 주요 의존성: pandas, requests, numpy, matplotlib
- 테스트 프레임워크: pytest


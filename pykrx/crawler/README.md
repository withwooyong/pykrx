# 백테스팅 데이터 수집 크롤러

코스피, 코스닥 전체 종목의 일별 OHLCV 데이터를 Parquet 및 DuckDB 형식으로 수집하는 크롤러입니다.

## 기능

- **전체 종목 수집**: 코스피, 코스닥 전체 종목 (상장폐지/신규상장 포함)
- **수정주가 지원**: 배당, 액면분할 등이 반영된 수정주가 데이터
- **기간**: 2020년 1월 1일부터 오늘까지
- **이중 저장**: Parquet 파일 + DuckDB 데이터베이스
- **진행 상황 추적**: 중단 후 재개 가능
- **멀티프로세싱**: 병렬 처리로 수집 속도 향상

## 설치

필요한 라이브러리 설치:

```bash
pip install duckdb pyarrow
```

## 사용 방법

### 기본 실행

```bash
python -m pykrx.crawler.main
```

### 옵션

```bash
# 메타데이터만 수집
python -m pykrx.crawler.main --skip-ohlcv

# OHLCV 데이터만 수집 (메타데이터는 이미 수집된 경우)
python -m pykrx.crawler.main --skip-metadata

# 멀티프로세싱 비활성화
python -m pykrx.crawler.main --no-multiprocessing

# 진행 상황 초기화
python -m pykrx.crawler.main --reset-progress
```

### Python 코드에서 사용

```python
from pykrx.crawler import collect_backtest_data

# 전체 데이터 수집
collect_backtest_data()

# 메타데이터만 수집
collect_backtest_data(skip_ohlcv=True)

# OHLCV 데이터만 수집
collect_backtest_data(skip_metadata=True)
```

## 데이터 구조

### 저장 경로

```
data/
├── parquet/
│   └── daily/
│       ├── KOSPI/
│       │   ├── 2020/
│       │   │   ├── 2020-01.parquet
│       │   │   ├── 2020-02.parquet
│       │   │   └── ...
│       │   └── 2021/
│       └── KOSDAQ/
│           └── (동일 구조)
├── duckdb/
│   └── stock_data.duckdb
└── progress/
    └── progress.json
```

### Parquet 파일 구조

각 Parquet 파일은 다음 컬럼을 포함합니다:

- `date`: 날짜 (YYYY-MM-DD)
- `ticker`: 티커 코드 (6자리)
- `시가`, `고가`, `저가`, `종가`: 가격 데이터
- `거래량`: 거래량
- `market`: 시장 구분 (KOSPI/KOSDAQ)

### DuckDB 테이블

#### ohlcv 테이블

```sql
CREATE TABLE ohlcv (
    date DATE,
    ticker VARCHAR(6),
    market VARCHAR(10),
    시가 DECIMAL(10,2),
    고가 DECIMAL(10,2),
    저가 DECIMAL(10,2),
    종가 DECIMAL(10,2),
    거래량 BIGINT,
    PRIMARY KEY (date, ticker)
);
```

#### ticker_metadata 테이블

```sql
CREATE TABLE ticker_metadata (
    ticker VARCHAR(6),
    종목명 VARCHAR(100),
    market VARCHAR(10),
    상장일 DATE,
    상장폐지일 DATE,
    PRIMARY KEY (ticker)
);
```

## 데이터 조회 예제

### DuckDB 사용

```python
import duckdb

conn = duckdb.connect("data/duckdb/stock_data.duckdb")

# 특정 종목의 데이터 조회
df = conn.execute("""
    SELECT * FROM ohlcv
    WHERE ticker = '005930'
    ORDER BY date
""").df()

# 특정 기간의 데이터 조회
df = conn.execute("""
    SELECT * FROM ohlcv
    WHERE date BETWEEN '2024-01-01' AND '2024-12-31'
    AND market = 'KOSPI'
    ORDER BY date, ticker
""").df()

conn.close()
```

### Parquet 파일 읽기

```python
import pandas as pd

# 특정 월 데이터 읽기
df = pd.read_parquet("data/parquet/daily/KOSPI/2024/2024-01.parquet")

# 여러 파일 읽기
import glob

files = glob.glob("data/parquet/daily/KOSPI/2024/*.parquet")
dfs = [pd.read_parquet(f) for f in files]
df = pd.concat(dfs, ignore_index=True)
```

## 설정 변경

`pykrx/crawler/config.py` 파일에서 설정을 변경할 수 있습니다:

- `START_DATE`: 수집 시작일
- `END_DATE`: 수집 종료일
- `MARKETS`: 수집할 시장 리스트
- `MAX_WORKERS`: 멀티프로세싱 워커 수
- `REQUEST_DELAY`: API 호출 간 딜레이
- `ADJUSTED`: 수정주가 사용 여부

## 주의사항

1. **API 호출 제한**: 과도한 API 호출을 방지하기 위해 딜레이가 설정되어 있습니다.
2. **수집 시간**: 전체 데이터 수집에는 수 시간이 소요될 수 있습니다.
3. **디스크 공간**: 대량의 데이터를 저장하므로 충분한 디스크 공간이 필요합니다.
4. **중단 및 재개**: Ctrl+C로 중단해도 진행 상황이 저장되며, 다시 실행하면 이어서 진행됩니다.

## 문제 해결

### 메모리 부족

멀티프로세싱 워커 수를 줄이거나 배치 크기를 줄이세요:

```python
# config.py에서
MAX_WORKERS = 2
BATCH_SIZE = 50
```

### 네트워크 오류

자동 재시도가 포함되어 있지만, 지속적인 오류 발생 시 `REQUEST_DELAY`를 늘리세요.

### 데이터 누락

진행 상황 파일(`data/progress/progress.json`)을 확인하여 실패한 티커를 확인하고, 필요시 재수집하세요.


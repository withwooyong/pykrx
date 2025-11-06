"""
크롤러 설정 파일
"""

from datetime import datetime
from pathlib import Path


class Config:
    """크롤러 설정 클래스"""

    # 데이터 수집 기간
    START_DATE = "20200101"
    END_DATE = datetime.now().strftime("%Y%m%d")

    # 수집할 시장
    MARKETS = ["KOSPI", "KOSDAQ"]

    # 데이터 저장 경로
    BASE_DIR = Path(__file__).parent.parent.parent / "data"
    PARQUET_DIR = BASE_DIR / "parquet" / "daily"
    DUCKDB_PATH = BASE_DIR / "duckdb" / "stock_data.duckdb"
    PROGRESS_DIR = BASE_DIR / "progress"

    # Parquet 파일 구조
    PARQUET_COMPRESSION = "snappy"  # snappy, gzip, brotli 등

    # API 호출 설정
    MAX_RETRIES = 3  # 최대 재시도 횟수
    RETRY_DELAY = 1  # 재시도 간격 (초)
    REQUEST_DELAY = 5  # API 호출 간 딜레이 (초)
    # REQUEST_DELAY = 0.1  # API 호출 간 딜레이 (초)

    # 멀티프로세싱 설정
    MAX_WORKERS = 4  # 병렬 처리 워커 수

    # 데이터 수집 설정
    ADJUSTED = True  # 수정주가 사용 여부
    BATCH_SIZE = 100  # 배치 처리 크기

    @classmethod
    def setup_directories(cls):
        """필요한 디렉토리 생성"""
        cls.BASE_DIR.mkdir(parents=True, exist_ok=True)
        cls.PARQUET_DIR.mkdir(parents=True, exist_ok=True)
        cls.DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
        cls.PROGRESS_DIR.mkdir(parents=True, exist_ok=True)

        # 시장별 디렉토리 생성
        for market in cls.MARKETS:
            market_dir = cls.PARQUET_DIR / market
            market_dir.mkdir(parents=True, exist_ok=True)

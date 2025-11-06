"""
Parquet 및 DuckDB 저장 모듈
"""

from pathlib import Path

import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .config import Config
from .utils import get_year_month_from_date


class StorageManager:
    """데이터 저장 관리 클래스"""

    def __init__(self):
        """저장 관리자 초기화"""

        Config.setup_directories()
        self.conn = None
        self._init_duckdb()

    def _init_duckdb(self):
        """DuckDB 초기화 및 테이블 생성"""

        try:
            self.conn = duckdb.connect(str(Config.DUCKDB_PATH))
            self._create_tables()
        except Exception as e:
            print(f"⚠️  DuckDB 초기화 실패: {e}")
            self.conn = None

    def _create_tables(self):
        """DuckDB 테이블 생성"""

        if not self.conn:
            return

        # OHLCV 테이블 생성
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ohlcv (
                date DATE,
                ticker VARCHAR(6),
                market VARCHAR(10),
                시가 DECIMAL(10,2),
                고가 DECIMAL(10,2),
                저가 DECIMAL(10,2),
                종가 DECIMAL(10,2),
                거래량 BIGINT,
                PRIMARY KEY (date, ticker)
            )
        """
        )

        # 티커 메타데이터 테이블 생성
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ticker_metadata (
                ticker VARCHAR(6),
                종목명 VARCHAR(100),
                market VARCHAR(10),
                상장일 DATE,
                상장폐지일 DATE,
                PRIMARY KEY (ticker)
            )
        """
        )

        # 인덱스 생성
        try:
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_ohlcv_date ON ohlcv(date)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_ohlcv_ticker ON ohlcv(ticker)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_ohlcv_market ON ohlcv(market)")
        except Exception:
            # 인덱스가 이미 존재할 수 있음
            pass

    def save_to_parquet(
        self, df: pd.DataFrame, market: str, date: pd.Timestamp | str
    ) -> Path | None:
        """DataFrame을 Parquet 파일로 저장"""

        if df.empty:
            return None

        try:
            # 날짜에서 연도와 월 추출
            if isinstance(date, str):
                year, month = get_year_month_from_date(date)
            else:
                year, month = date.year, date.month

            # 디렉토리 경로 생성
            year_dir = Config.PARQUET_DIR / market / str(year)
            year_dir.mkdir(parents=True, exist_ok=True)

            # 파일 경로 생성 (YYYY-MM.parquet 형식)
            parquet_file = year_dir / f"{year}-{month:02d}.parquet"

            # 기존 파일이 있으면 읽어서 병합
            if parquet_file.exists():
                try:
                    existing_df = pd.read_parquet(parquet_file)
                    # 중복 제거 (같은 date, ticker 조합)
                    combined_df = pd.concat([existing_df, df])
                    combined_df = combined_df.drop_duplicates(
                        subset=["date", "ticker"], keep="last"
                    )
                    df = combined_df.sort_values("date")
                except Exception as e:
                    print(f"  ⚠️  기존 Parquet 파일 읽기 실패: {e}")

            # Parquet로 저장
            table = pa.Table.from_pandas(df)
            pq.write_table(
                table,
                parquet_file,
                compression=Config.PARQUET_COMPRESSION,
                use_dictionary=True,
            )

            return parquet_file

        except Exception as e:
            print(f"  ⚠️  Parquet 저장 실패: {e}")
            return None

    def save_to_duckdb(self, df: pd.DataFrame, table_name: str = "ohlcv"):
        """DataFrame을 DuckDB에 저장"""

        if df.empty or not self.conn:
            return

        try:
            # 기존 데이터와 중복 제거를 위해 UPSERT 사용
            if table_name == "ohlcv":
                # 임시 테이블에 데이터 삽입
                self.conn.execute("CREATE TEMP TABLE temp_ohlcv AS SELECT * FROM df")
                # UPSERT (INSERT OR REPLACE)
                self.conn.execute(
                    """
                    INSERT INTO ohlcv
                    SELECT * FROM temp_ohlcv
                    ON CONFLICT (date, ticker) DO UPDATE SET
                        market = EXCLUDED.market,
                        시가 = EXCLUDED.시가,
                        고가 = EXCLUDED.고가,
                        저가 = EXCLUDED.저가,
                        종가 = EXCLUDED.종가,
                        거래량 = EXCLUDED.거래량
                """
                )
                self.conn.execute("DROP TABLE temp_ohlcv")
            elif table_name == "ticker_metadata":
                # 임시 테이블에 데이터 삽입
                self.conn.execute("CREATE TEMP TABLE temp_metadata AS SELECT * FROM df")
                # UPSERT
                self.conn.execute(
                    """
                    INSERT INTO ticker_metadata
                    SELECT * FROM temp_metadata
                    ON CONFLICT (ticker) DO UPDATE SET
                        종목명 = EXCLUDED.종목명,
                        market = EXCLUDED.market,
                        상장일 = EXCLUDED.상장일,
                        상장폐지일 = EXCLUDED.상장폐지일
                """
                )
                self.conn.execute("DROP TABLE temp_metadata")

        except Exception:
            # DuckDB 버전에 따라 ON CONFLICT를 지원하지 않을 수 있음
            try:
                # 대안: DELETE 후 INSERT
                if table_name == "ohlcv" and not df.empty:
                    # 기존 데이터 삭제
                    tickers = df["ticker"].unique().tolist()
                    dates = df["date"].unique().tolist()
                    for ticker in tickers:
                        for date in dates:
                            self.conn.execute(
                                "DELETE FROM ohlcv WHERE ticker = ? AND date = ?",
                                [ticker, date],
                            )
                    # 새 데이터 삽입
                    self.conn.execute("INSERT INTO ohlcv SELECT * FROM df")
                elif table_name == "ticker_metadata" and not df.empty:
                    # 기존 데이터 삭제
                    tickers = df["ticker"].unique().tolist()
                    for ticker in tickers:
                        self.conn.execute("DELETE FROM ticker_metadata WHERE ticker = ?", [ticker])
                    # 새 데이터 삽입
                    self.conn.execute("INSERT INTO ticker_metadata SELECT * FROM df")
            except Exception as e2:
                print(f"  ⚠️  DuckDB 저장 실패: {e2}")

    def save_ohlcv_data(self, df: pd.DataFrame, market: str, date: pd.Timestamp | str):
        """OHLCV 데이터를 Parquet와 DuckDB에 모두 저장"""

        if df.empty:
            return

        # market 컬럼 추가
        if "market" not in df.columns:
            df["market"] = market

        # Parquet 저장
        parquet_path = self.save_to_parquet(df, market, date)
        if parquet_path:
            print(f"  💾 Parquet 저장: {parquet_path}")

        # DuckDB 저장
        self.save_to_duckdb(df, "ohlcv")

    def save_metadata(self, df: pd.DataFrame):
        """메타데이터를 DuckDB에 저장"""

        if df.empty:
            return

        self.save_to_duckdb(df, "ticker_metadata")

    def close(self):
        """연결 종료"""

        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Context manager 진입"""

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""

        self.close()

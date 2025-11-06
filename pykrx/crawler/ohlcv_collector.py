"""
OHLCV 데이터 수집 모듈 (Phase 2)
"""

import time
from multiprocessing import Pool

import pandas as pd

from pykrx import stock

from .config import Config
from .progress_tracker import ProgressTracker
from .storage import StorageManager
from .utils import date_to_string, retry_with_backoff, split_date_range_by_year


class OHLCVCollector:
    """OHLCV 데이터 수집 클래스"""

    def __init__(self, progress_tracker: ProgressTracker, storage: StorageManager):
        """OHLCV 수집 초기화"""

        self.progress_tracker = progress_tracker
        self.storage = storage

    def collect_all_ohlcv(self, use_multiprocessing: bool = True):
        """전체 OHLCV 데이터 수집"""

        print("\n📊 Phase 2: OHLCV 데이터 수집 시작")

        # 수집 대기 중인 티커 리스트 가져오기
        pending_tickers = self.progress_tracker.get_pending_tickers()
        if not pending_tickers:
            # ProgressTracker에서 모든 티커 가져오기
            all_tickers = list(self.progress_tracker.progress.get("tickers", {}).keys())
            pending_tickers = [
                t for t in all_tickers if not self.progress_tracker.is_ticker_collected(t)
            ]

        if not pending_tickers:
            print("  ✅ 수집할 티커가 없습니다.")
            return

        print(f"  총 {len(pending_tickers)}개 티커 수집 예정")

        if use_multiprocessing and Config.MAX_WORKERS > 1:
            self._collect_with_multiprocessing(pending_tickers)
        else:
            self._collect_sequential(pending_tickers)

        # 최종 통계
        stats = self.progress_tracker.get_stats()
        print("\n  ✅ OHLCV 데이터 수집 완료")
        print(f"    - 완료: {stats.get('completed_tickers', 0)}개")
        print(f"    - 실패: {stats.get('failed_tickers', 0)}개")
        print(f"    - 전체: {stats.get('total_tickers', 0)}개")

    def _collect_sequential(self, tickers: list[str]):
        """순차적으로 OHLCV 데이터 수집"""

        total = len(tickers)
        for i, ticker in enumerate(tickers, 1):
            print(f"\n  [{i}/{total}] 티커: {ticker}")
            self._collect_ticker_ohlcv(ticker)
            time.sleep(Config.REQUEST_DELAY)

    def _collect_with_multiprocessing(self, tickers: list[str]):
        """멀티프로세싱으로 OHLCV 데이터 수집"""

        print(f"  멀티프로세싱 모드 (워커: {Config.MAX_WORKERS}, 총 {len(tickers)}개 티커)")

        # 배치로 나누어 처리
        batch_size = Config.BATCH_SIZE
        batches = [tickers[i : i + batch_size] for i in range(0, len(tickers), batch_size)]

        for batch_num, batch in enumerate(batches, 1):
            print(f"\n  배치 {batch_num}/{len(batches)} ({len(batch)}개 티커)")

            with Pool(processes=Config.MAX_WORKERS) as pool:
                results = pool.map(self._collect_ticker_ohlcv_wrapper, batch)

            # 결과 요약
            completed = sum(1 for r in results if r is True)
            failed = sum(1 for r in results if r is False)
            print(f"    완료: {completed}, 실패: {failed}")

            time.sleep(Config.REQUEST_DELAY * 2)  # 배치 간 딜레이

    @staticmethod
    def _collect_ticker_ohlcv_wrapper(ticker: str) -> bool:
        """멀티프로세싱용 래퍼 함수"""

        # 각 프로세스에서 새로운 StorageManager와 ProgressTracker 생성
        from .progress_tracker import ProgressTracker
        from .storage import StorageManager

        progress_tracker = ProgressTracker()
        storage = StorageManager()

        try:
            collector = OHLCVCollector(progress_tracker, storage)
            collector._collect_ticker_ohlcv(ticker)
            storage.close()
            return True
        except Exception as e:
            print(f"  ⚠️  티커 {ticker} 수집 실패: {e}")
            progress_tracker.mark_ticker_failed(ticker, str(e))
            storage.close()
            return False

    def _collect_ticker_ohlcv(self, ticker: str):
        """특정 티커의 OHLCV 데이터 수집 (연도별 분할)"""

        ticker_info = self.progress_tracker.get_ticker_info(ticker)
        if not ticker_info:
            print(f"    ⚠️  티커 {ticker} 정보를 찾을 수 없습니다.")
            return

        # 수집 기간 결정
        listing_date = ticker_info.get("listing_date") or Config.START_DATE
        delisting_date = ticker_info.get("delisting_date")
        end_date = delisting_date if delisting_date else Config.END_DATE

        # 이미 수집된 경우 스킵
        if self.progress_tracker.is_ticker_collected(ticker):
            last_collected = ticker_info.get("last_collected_date")
            if last_collected and last_collected >= end_date:
                print(f"    ⏭️  이미 수집 완료 (마지막 수집일: {last_collected})")
                return

        # 연도별로 분할
        year_ranges = split_date_range_by_year(listing_date, end_date)
        if not year_ranges:
            print("    ⚠️  유효한 날짜 범위가 없습니다.")
            return

        print(f"    📅 {len(year_ranges)}개 연도 분할 수집: {listing_date} ~ {end_date}")

        all_dataframes = []
        failed_years = []

        try:
            # 연도별로 데이터 수집
            for year_start, year_end in year_ranges:
                year = year_start[:4]
                try:
                    print(f"      [{year}] {year_start} ~ {year_end} 수집 중...")
                    df_year = self._fetch_ohlcv_data(ticker, year_start, year_end)

                    if not df_year.empty:
                        all_dataframes.append(df_year)
                        print(f"      [{year}] ✅ {len(df_year)}일 수집 완료")
                    else:
                        print(f"      [{year}] ⚠️  데이터 없음")
                        failed_years.append(year)

                    # 연도 간 딜레이
                    time.sleep(Config.REQUEST_DELAY)

                except Exception as e:
                    print(f"      [{year}] ❌ 수집 실패: {e}")
                    failed_years.append(year)

            # 모든 연도 데이터 합치기
            if not all_dataframes:
                error_msg = (
                    f"모든 연도 수집 실패 (실패 연도: {', '.join(failed_years)})"
                    if failed_years
                    else "데이터 없음"
                )
                print(f"    ⚠️  {error_msg}")
                self.progress_tracker.mark_ticker_failed(ticker, error_msg)
                return

            # DataFrame 합치기
            df = pd.concat(all_dataframes, ignore_index=False)
            df = df.sort_index() if hasattr(df, "sort_index") else df.sort_values("date")
            # 중복 제거 (연도 경계에서 중복 가능)
            df = df.drop_duplicates(subset=["date"] if "date" in df.columns else None, keep="last")

            if df.empty:
                print("    ⚠️  합친 데이터가 비어있습니다.")
                self.progress_tracker.mark_ticker_failed(ticker, "합친 데이터 없음")
                return

            # 데이터 저장
            market = ticker_info.get("market", "UNKNOWN")
            self._save_ticker_data(df, ticker, market)

            # 완료 표시
            last_date = df["date"].max() if "date" in df.columns else df.index.max()

            # Timestamp로 변환 보장
            try:
                if isinstance(last_date, pd.Timestamp) and last_date is not pd.NaT:
                    last_date_str = date_to_string(last_date)
                elif isinstance(last_date, pd.Series) and len(last_date) > 0:
                    last_date_val = last_date.iloc[0]
                    if isinstance(last_date_val, pd.Timestamp) and last_date_val is not pd.NaT:
                        last_date_str = date_to_string(last_date_val)
                    else:
                        last_date_str = Config.END_DATE
                else:
                    # 최후의 수단: 마지막 행의 날짜 사용
                    last_date_val = df["date"].iloc[-1] if "date" in df.columns else df.index[-1]
                    if isinstance(last_date_val, pd.Timestamp) and last_date_val is not pd.NaT:
                        last_date_str = date_to_string(last_date_val)
                    else:
                        last_date_str = Config.END_DATE
            except Exception:
                last_date_str = Config.END_DATE

            self.progress_tracker.mark_ticker_completed(ticker, last_date_str)

            total_days = len(df)
            first_date = df["date"].min() if "date" in df.columns else df.index.min()
            last_date_display = df["date"].max() if "date" in df.columns else df.index.max()
            print(f"    ✅ 수집 완료: {total_days}일 ({first_date} ~ {last_date_display})")
            if failed_years:
                print(f"    ⚠️  일부 연도 실패: {', '.join(failed_years)}")

        except Exception as e:
            print(f"    ❌ 수집 실패: {e}")
            self.progress_tracker.mark_ticker_failed(ticker, str(e))

    @retry_with_backoff(max_retries=Config.MAX_RETRIES, delay=Config.RETRY_DELAY)
    def _fetch_ohlcv_data(self, ticker: str, fromdate: str, todate: str) -> pd.DataFrame:
        """OHLCV 데이터 조회"""

        try:
            df = stock.get_market_ohlcv_by_date(
                fromdate=fromdate,
                todate=todate,
                ticker=ticker,
                adjusted=Config.ADJUSTED,
            )

            if df.empty:
                return df

            # ticker 컬럼 추가
            df["ticker"] = ticker
            # date 컬럼 추가 (인덱스를 컬럼으로)
            df = df.reset_index()
            # 날짜 컬럼 처리
            if "날짜" in df.columns:
                df["date"] = pd.to_datetime(df["날짜"])
            elif "Date" in df.columns:
                df["date"] = pd.to_datetime(df["Date"])
            elif df.index.name in ["날짜", "Date", "date"]:
                df["date"] = pd.to_datetime(df.index)
            else:
                # 인덱스가 날짜인 경우
                df["date"] = pd.to_datetime(df.index)

            return df

        except Exception as e:
            print(f"    ⚠️  OHLCV 조회 실패: {e}")
            return pd.DataFrame()

    def _save_ticker_data(self, df: pd.DataFrame, ticker: str, market: str):
        """티커 데이터를 날짜별로 그룹화하여 저장"""

        if df.empty:
            return

        # 날짜별로 그룹화
        df["date"] = pd.to_datetime(df["date"])
        grouped = df.groupby(df["date"].dt.to_period("M"))

        saved_count = 0
        for period, group_df in grouped:
            # Period를 Timestamp로 변환
            try:
                if isinstance(period, pd.Period):
                    date = period.to_timestamp()
                else:
                    # Period 객체가 아닌 경우 문자열로 변환 후 파싱
                    date = pd.Timestamp(str(period))
            except Exception:
                # 최후의 수단: 첫 번째 날짜 사용
                date = group_df["date"].iloc[0] if not group_df.empty else pd.Timestamp.now()
            # ticker 컬럼이 없으면 추가
            if "ticker" not in group_df.columns:
                group_df["ticker"] = ticker

            # 필요한 컬럼만 선택
            columns = ["date", "ticker", "시가", "고가", "저가", "종가", "거래량"]
            group_df = group_df[columns].copy()

            # 저장 (DataFrame 확인)
            if isinstance(group_df, pd.DataFrame):
                # date가 유효한 Timestamp인지 확인
                if isinstance(date, pd.Timestamp) and not pd.isna(date):
                    self.storage.save_ohlcv_data(group_df, market, date)
                    saved_count += 1
                else:
                    print(f"    ⚠️  날짜 형식 오류로 스킵: {date}")

        if saved_count > 0:
            print(f"    💾 {saved_count}개 파일 저장 완료")

"""
메타데이터 수집 모듈 (Phase 1)
"""

import time

import pandas as pd

from pykrx import stock
from pykrx.website.krx.market.ticker import StockTicker

from .config import Config
from .progress_tracker import ProgressTracker
from .storage import StorageManager
from .utils import date_to_string, retry_with_backoff, string_to_date


class MetadataCollector:
    """메타데이터 수집 클래스"""

    def __init__(self, progress_tracker: ProgressTracker, storage: StorageManager):
        """메타데이터 수집 초기화"""

        self.progress_tracker = progress_tracker
        self.storage = storage
        self.stock_ticker = StockTicker()

    def collect_all_tickers(self) -> pd.DataFrame:
        """전체 티커 리스트 수집 (상장폐지 포함)"""

        print("📋 Phase 1: 메타데이터 수집 시작")
        print(f"  기간: {Config.START_DATE} ~ {Config.END_DATE}")
        print(f"  시장: {', '.join(Config.MARKETS)}")

        all_tickers = set()
        ticker_info = {}

        # 1. 모든 영업일 순회하며 티커 리스트 수집
        print("\n  🔍 날짜별 티커 리스트 수집 중...")
        business_days = self._get_all_business_days()

        for i, date in enumerate(business_days):
            date_str = date_to_string(date)
            if (i + 1) % 50 == 0:
                print(f"    진행: {i + 1}/{len(business_days)} ({date_str})")

            for market in Config.MARKETS:
                tickers = self._get_tickers_for_date(date_str, market)
                all_tickers.update(tickers)

                # 각 티커의 정보 저장
                for ticker in tickers:
                    if ticker not in ticker_info:
                        ticker_info[ticker] = {
                            "ticker": ticker,
                            "market": market,
                            "first_seen_date": date_str,
                            "last_seen_date": date_str,
                        }
                    else:
                        ticker_info[ticker]["last_seen_date"] = date_str

            time.sleep(Config.REQUEST_DELAY)

        print(f"\n  ✅ 총 {len(all_tickers)}개 티커 발견")

        # 2. StockTicker를 사용하여 상장일/상장폐지일 정보 수집
        print("\n  📅 티커별 상장일/상장폐지일 정보 수집 중...")
        metadata_list = []

        for i, ticker in enumerate(sorted(all_tickers)):
            if (i + 1) % 100 == 0:
                print(f"    진행: {i + 1}/{len(all_tickers)}")

            info = self._get_ticker_metadata(ticker, ticker_info.get(ticker, {}))
            if info:
                metadata_list.append(info)
                # ProgressTracker에 티커 추가
                self.progress_tracker.add_ticker(
                    ticker=ticker,
                    market=info["market"],
                    listing_date=info.get("상장일"),
                    delisting_date=info.get("상장폐지일"),
                )

            time.sleep(Config.REQUEST_DELAY * 0.5)  # 메타데이터 조회는 더 짧은 딜레이

        # 3. DataFrame 생성
        metadata_df = pd.DataFrame(metadata_list)

        if not metadata_df.empty:
            # ProgressTracker에 메타데이터 수집 완료 표시
            self.progress_tracker.mark_metadata_collected()

            # DuckDB에 저장
            self.storage.save_metadata(metadata_df)

            print(f"\n  ✅ 메타데이터 수집 완료: {len(metadata_df)}개 티커")
            print(f"    - KOSPI: {len(metadata_df[metadata_df['market'] == 'KOSPI'])}개")
            print(f"    - KOSDAQ: {len(metadata_df[metadata_df['market'] == 'KOSDAQ'])}개")

        return metadata_df

    def _get_all_business_days(self) -> list[pd.Timestamp]:
        """전체 영업일 리스트 수집"""

        business_days = []
        start_date = string_to_date(Config.START_DATE)
        end_date = string_to_date(Config.END_DATE)

        # 연도별로 영업일 수집
        current_year = start_date.year
        end_year = end_date.year

        while current_year <= end_year:
            for month in range(1, 13):
                # 시작 연도의 경우 시작 월부터
                if current_year == start_date.year and month < start_date.month:
                    continue
                # 종료 연도의 경우 종료 월까지만
                if current_year == end_date.year and month > end_date.month:
                    break

                try:
                    days = stock.get_previous_business_days(year=current_year, month=month)
                    # 시작일/종료일 필터링
                    for day in days:
                        if start_date <= day <= end_date:
                            business_days.append(day)
                    time.sleep(Config.REQUEST_DELAY * 0.5)
                except Exception as e:
                    print(f"  ⚠️  {current_year}-{month:02d} 영업일 수집 실패: {e}")

            current_year += 1

        # 중복 제거 및 정렬
        business_days = sorted(set(business_days))
        return business_days

    @retry_with_backoff(max_retries=Config.MAX_RETRIES, delay=Config.RETRY_DELAY)
    def _get_tickers_for_date(self, date: str, market: str) -> list[str]:
        """특정 날짜의 티커 리스트 조회"""

        try:
            tickers = stock.get_market_ticker_list(date=date, market=market)
            return tickers if tickers else []
        except Exception as e:
            print(f"  ⚠️  {date} {market} 티커 리스트 조회 실패: {e}")
            return []

    def _get_ticker_metadata(self, ticker: str, ticker_info: dict) -> dict | None:
        """티커 메타데이터 조회"""

        try:
            ticker_data = self.stock_ticker.get(ticker)
            if ticker_data is None:
                # 상장폐지 종목이거나 정보가 없는 경우
                return {
                    "ticker": ticker,
                    "종목명": ticker_info.get("ticker", "알 수 없음"),
                    "market": ticker_info.get("market", "UNKNOWN"),
                    "상장일": ticker_info.get("first_seen_date"),
                    "상장폐지일": ticker_info.get("last_seen_date"),
                }

            # 시장 정보 변환 (STK -> KOSPI, KSQ -> KOSDAQ)
            market_map = {"STK": "KOSPI", "KSQ": "KOSDAQ", "KNX": "KONEX"}
            market_code = ticker_data.get("시장", "")
            market = market_map.get(market_code, ticker_info.get("market", "UNKNOWN"))

            return {
                "ticker": ticker,
                "종목명": ticker_data.get("종목", "알 수 없음"),
                "market": market,
                "상장일": ticker_info.get("first_seen_date"),
                "상장폐지일": None,  # 상장폐지일은 별도로 추적 필요
            }

        except Exception as e:
            print(f"  ⚠️  티커 {ticker} 메타데이터 조회 실패: {e}")
            return {
                "ticker": ticker,
                "종목명": "알 수 없음",
                "market": ticker_info.get("market", "UNKNOWN"),
                "상장일": ticker_info.get("first_seen_date"),
                "상장폐지일": None,
            }

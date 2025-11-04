"""주식 OHLCV 관련 함수 테스트"""

import datetime
from unittest.mock import patch

import pandas as pd

from pykrx.stock.stock_ohlcv import (
    get_market_ohlcv,
    get_market_ohlcv_by_date,
    get_market_ohlcv_by_ticker,
)


class TestStockOHLCV:
    """주식 OHLCV 관련 함수 테스트 클래스"""

    # 테스트에서 사용할 날짜 상수
    FROMDATE = "20240115"
    TODATE = "20240117"
    TODATE_END = "20240116"
    PREV_DATE = (
        datetime.datetime.strptime(FROMDATE, "%Y%m%d") - datetime.timedelta(days=1)
    ).strftime("%Y%m%d")
    FROMDATE_DASH = datetime.datetime.strptime(FROMDATE, "%Y%m%d").strftime("%Y-%m-%d")
    TICKER = "005930"  # 삼성전자

    # datetime 객체
    FROMDATE_DT = datetime.datetime.strptime(FROMDATE, "%Y%m%d")
    TODATE_DT = datetime.datetime.strptime(TODATE_END, "%Y%m%d")

    def test_get_market_ohlcv_by_date_with_string_dates(self):
        """문자열 날짜로 OHLCV 조회 테스트"""
        with patch("pykrx.website.naver.get_market_ohlcv_by_date") as mock_naver:
            # Mock 데이터 생성
            mock_df = pd.DataFrame(
                {
                    "시가": [100, 101, 102],
                    "고가": [105, 106, 107],
                    "저가": [95, 96, 97],
                    "종가": [101, 102, 103],
                    "거래량": [1000, 1100, 1200],
                },
                index=pd.date_range(self.FROMDATE_DASH, periods=3),
            )
            mock_naver.return_value = mock_df

            result = get_market_ohlcv_by_date(self.FROMDATE, self.TODATE, self.TICKER)

            # 결과 출력
            print("\n[test_get_market_ohlcv_by_date_with_string_dates] result:")
            print(result)

            # 결과 검증
            assert len(result) == 3
            assert "시가" in result.columns
            assert "고가" in result.columns
            assert "저가" in result.columns
            assert "종가" in result.columns
            assert "거래량" in result.columns

            # naver 함수 호출 검증
            mock_naver.assert_called_once_with(self.FROMDATE, self.TODATE, self.TICKER)

    def test_get_market_ohlcv_by_date_with_datetime_dates(self):
        """datetime 객체로 OHLCV 조회 테스트"""
        with (
            patch("pykrx.website.krx.datetime2string") as mock_datetime2string,
            patch("pykrx.website.krx.get_market_ohlcv_by_date") as mock_krx,
        ):
            # datetime2string이 두 번 호출되므로 side_effect 사용
            mock_datetime2string.side_effect = [self.FROMDATE, self.TODATE_END]

            mock_df = pd.DataFrame(
                {
                    "시가": [100, 101],
                    "고가": [105, 106],
                    "저가": [95, 96],
                    "종가": [101, 102],
                    "거래량": [1000, 1100],
                },
                index=pd.date_range(self.FROMDATE_DASH, periods=2),
            )
            mock_krx.return_value = mock_df

            result = get_market_ohlcv_by_date(
                self.FROMDATE_DT,  # type: ignore[arg-type]
                self.TODATE_DT,  # type: ignore[arg-type]
                self.TICKER,
                adjusted=False,
            )

            # 결과 출력
            print("\n[test_get_market_ohlcv_by_date_with_datetime_dates] result:")
            print(result)

            # krx 함수 호출 검증 (adjusted=False인 경우)
            mock_krx.assert_called_once_with(self.FROMDATE, self.TODATE_END, self.TICKER, False)

    def test_get_market_ohlcv_by_date_with_dash_dates(self):
        """하이픈이 포함된 날짜로 OHLCV 조회 테스트"""
        with patch("pykrx.website.naver.get_market_ohlcv_by_date") as mock_naver:
            mock_df = pd.DataFrame(
                {"시가": [100], "고가": [105], "저가": [95], "종가": [101], "거래량": [1000]},
                index=pd.date_range(self.FROMDATE_DASH, periods=1),
            )
            mock_naver.return_value = mock_df

            result = get_market_ohlcv_by_date(self.FROMDATE_DASH, self.FROMDATE_DASH, self.TICKER)

            # 결과 출력
            print("\n[test_get_market_ohlcv_by_date_with_dash_dates] result:")
            print(result)

            # 하이픈이 제거되어야 함
            mock_naver.assert_called_once_with(self.FROMDATE, self.FROMDATE, self.TICKER)

    def test_get_market_ohlcv_by_date_with_name_display(self):
        """name_display 옵션 테스트"""
        with (
            patch("pykrx.website.naver.get_market_ohlcv_by_date") as mock_naver,
            patch("pykrx.stock.stock_ticker.get_market_ticker_name") as mock_ticker_name,
        ):
            mock_df = pd.DataFrame(
                {"시가": [100], "고가": [105], "저가": [95], "종가": [101], "거래량": [1000]},
                index=pd.date_range(self.FROMDATE_DASH, periods=1),
            )
            mock_naver.return_value = mock_df
            mock_ticker_name.return_value = "삼성전자"

            result = get_market_ohlcv_by_date(
                self.FROMDATE, self.FROMDATE, self.TICKER, name_display=True
            )

            # 결과 출력
            print("\n[test_get_market_ohlcv_by_date_with_name_display] result:")
            print(result)

            # columns.name이 설정되어야 함
            assert result.columns.name == "삼성전자"

    def test_get_market_ohlcv_by_ticker(self):
        """티커별 OHLCV 조회 테스트"""
        with patch("pykrx.website.krx.get_market_ohlcv_by_ticker") as mock_krx:
            mock_df = pd.DataFrame(
                {
                    "시가": [100, 101, 102],
                    "고가": [105, 106, 107],
                    "저가": [95, 96, 97],
                    "종가": [101, 102, 103],
                    "거래량": [1000, 1100, 1200],
                },
                index=pd.Index(["005930", "000660", "373220"]),
            )
            mock_krx.return_value = mock_df

            result = get_market_ohlcv_by_ticker(self.FROMDATE, "KOSPI")

            # 결과 출력
            print("\n[test_get_market_ohlcv_by_ticker] result:")
            print(result)

            # 결과 검증
            assert len(result) == 3
            mock_krx.assert_called_once_with(self.FROMDATE, "KOSPI")

    def test_get_market_ohlcv_by_ticker_with_datetime(self):
        """datetime 객체로 티커별 OHLCV 조회 테스트"""
        with (
            patch("pykrx.website.krx.datetime2string") as mock_datetime2string,
            patch("pykrx.website.krx.get_market_ohlcv_by_ticker") as mock_krx,
        ):
            mock_datetime2string.return_value = self.FROMDATE
            mock_df = pd.DataFrame(
                {"시가": [100], "고가": [105], "저가": [95], "종가": [101], "거래량": [1000]},
                index=pd.Index(["005930"]),
            )
            mock_krx.return_value = mock_df

            result = get_market_ohlcv_by_ticker(self.FROMDATE_DT, "KOSPI")  # type: ignore[arg-type]

            # 결과 출력
            print("\n[test_get_market_ohlcv_by_ticker_with_datetime] result:")
            print(result)

            mock_krx.assert_called_once_with(self.FROMDATE, "KOSPI")

    def test_get_market_ohlcv_by_ticker_holiday_alternative(self):
        """휴일 대안 데이터 조회 테스트"""
        with (
            patch("pykrx.stock.stock_ohlcv.krx.get_market_ohlcv_by_ticker") as mock_krx,
            patch(
                "pykrx.stock.stock_ohlcv.get_nearest_business_day_in_a_week"
            ) as mock_business_day,
        ):
            # 첫 번째 호출은 휴일 데이터 (모든 값이 0)
            holiday_df = pd.DataFrame(
                {
                    "시가": [0, 0],
                    "고가": [0, 0],
                    "저가": [0, 0],
                    "종가": [0, 0],
                    "거래량": [0, 0],
                },
                index=pd.Index(["005930", "000660"]),
            )

            # 두 번째 호출은 정상 데이터
            normal_df = pd.DataFrame(
                {
                    "시가": [100, 101],
                    "고가": [105, 106],
                    "저가": [95, 96],
                    "종가": [101, 102],
                    "거래량": [1000, 1100],
                },
                index=pd.Index(["005930", "000660"]),
            )

            mock_krx.side_effect = [holiday_df, normal_df]
            mock_business_day.return_value = self.PREV_DATE

            result = get_market_ohlcv_by_ticker(self.FROMDATE, "KOSPI", alternative=True)

            # 결과 출력
            print("\n[test_get_market_ohlcv_by_ticker_holiday_alternative] result:")
            print(result)

            # alternative=True이므로 이전 영업일 데이터가 반환되어야 함
            assert len(result) == 2
            # 휴일이므로 두 번 호출되어야 함
            assert mock_krx.call_count == 2
            mock_business_day.assert_called_once_with(date=self.FROMDATE, prev=True)

    def test_get_market_ohlcv_function_dispatch(self):
        """get_market_ohlcv 함수의 dispatch 로직 테스트"""
        with (
            patch("pykrx.stock.stock_ohlcv.get_market_ohlcv_by_date") as mock_by_date,
            patch("pykrx.stock.stock_ohlcv.get_market_ohlcv_by_ticker") as mock_by_ticker,
        ):
            mock_by_date.return_value = pd.DataFrame()
            mock_by_ticker.return_value = pd.DataFrame()

            # 2개 날짜 인자로 호출하면 by_date 함수가 호출되어야 함
            get_market_ohlcv(self.FROMDATE, self.TODATE_END, self.TICKER)
            mock_by_date.assert_called_once()
            mock_by_ticker.assert_not_called()

            # 1개 날짜 인자로 호출하면 by_ticker 함수가 호출되어야 함
            get_market_ohlcv(self.FROMDATE)
            mock_by_ticker.assert_called_once()

    def test_get_market_ohlcv_with_kwargs(self):
        """키워드 인자로 OHLCV 조회 테스트"""
        with patch("pykrx.stock.stock_ohlcv.get_market_ohlcv_by_date") as mock_by_date:
            mock_by_date.return_value = pd.DataFrame()

            get_market_ohlcv(fromdate=self.FROMDATE, todate=self.TODATE_END, ticker=self.TICKER)

            mock_by_date.assert_called_once_with(
                fromdate=self.FROMDATE, todate=self.TODATE_END, ticker=self.TICKER
            )

"""주식 시가총액 관련 함수 테스트"""

import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from pykrx.stock.stock_market_cap import (
    get_market_cap,
    get_market_cap_by_date,
    get_market_cap_by_ticker,
)


class TestStockMarketCap:
    """주식 시가총액 관련 함수 테스트 클래스"""

    def test_get_market_cap_by_date_with_string_dates(self):
        """문자열 날짜로 시가총액 조회 테스트"""
        with patch("pykrx.website.krx.get_market_cap_by_date") as mock_krx:
            # Mock 데이터 생성
            mock_df = pd.DataFrame(
                {
                    "시가총액": [1000000, 1100000, 1200000],
                    "거래량": [1000, 1100, 1200],
                    "거래대금": [100000, 110000, 120000],
                    "상장주식수": [10000, 11000, 12000],
                },
                index=pd.date_range("2024-01-15", periods=3),
            )
            mock_krx.return_value = mock_df

            result = get_market_cap_by_date("20240115", "20240117", "005930")

            # 결과 검증
            assert len(result) == 3
            assert "시가총액" in result.columns
            assert "거래량" in result.columns
            assert "거래대금" in result.columns
            assert "상장주식수" in result.columns

            # krx 함수 호출 검증
            mock_krx.assert_called_once_with("20240115", "20240117", "005930")

    def test_get_market_cap_by_date_with_datetime_dates(self):
        """datetime 객체로 시가총액 조회 테스트"""
        with (
            patch("pykrx.website.krx.datetime2string") as mock_datetime2string,
            patch("pykrx.website.krx.get_market_cap_by_date") as mock_krx,
        ):
            mock_datetime2string.side_effect = ["20240115", "20240116"]

            mock_df = pd.DataFrame(
                {
                    "시가총액": [1000000, 1100000],
                    "거래량": [1000, 1100],
                    "거래대금": [100000, 110000],
                    "상장주식수": [10000, 11000],
                },
                index=pd.date_range("2024-01-15", periods=2),
            )
            mock_krx.return_value = mock_df

            start_date = datetime.datetime(2024, 1, 15)
            end_date = datetime.datetime(2024, 1, 16)

            result = get_market_cap_by_date(start_date, end_date, "005930")  # type: ignore[arg-type]  # noqa: F841

            # krx 함수 호출 검증
            mock_krx.assert_called_once_with("20240115", "20240116", "005930")

    def test_get_market_cap_by_date_with_dash_dates(self):
        """하이픈이 포함된 날짜로 시가총액 조회 테스트"""
        with patch("pykrx.website.krx.get_market_cap_by_date") as mock_krx:
            mock_df = pd.DataFrame(
                {
                    "시가총액": [1000000],
                    "거래량": [1000],
                    "거래대금": [100000],
                    "상장주식수": [10000],
                },
                index=pd.date_range("2024-01-15", periods=1),
            )
            mock_krx.return_value = mock_df

            result = get_market_cap_by_date("2024-01-15", "2024-01-15", "005930")  # noqa: F841

            # 하이픈이 제거되어야 함
            mock_krx.assert_called_once_with("20240115", "20240115", "005930")

    def test_get_market_cap_by_date_with_freq(self):
        """주기별 시가총액 조회 테스트"""
        with patch("pykrx.website.krx.get_market_cap_by_date") as mock_krx:
            # 월별 데이터로 리샘플링 테스트
            mock_df = pd.DataFrame(
                {
                    "시가총액": [1000000] * 30,  # 30일 데이터
                    "거래량": [1000] * 30,
                    "거래대금": [100000] * 30,
                    "상장주식수": [10000] * 30,
                },
                index=pd.date_range("2024-01-01", periods=30, freq="D"),
            )
            mock_krx.return_value = mock_df

            result = get_market_cap_by_date("20240101", "20240130", "005930", freq="m")

            # 월별로 리샘플링되어 1개 행이 되어야 함
            assert len(result) == 1
            assert result.iloc[0]["시가총액"] == 1000000  # 마지막 시가총액
            assert result.iloc[0]["거래량"] == 30000  # 거래량 합계
            assert result.iloc[0]["거래대금"] == 3000000  # 거래대금 합계
            assert result.iloc[0]["상장주식수"] == 10000  # 마지막 상장주식수

    def test_get_market_cap_by_ticker(self):
        """티커별 시가총액 조회 테스트"""
        with patch("pykrx.website.krx.get_market_cap_by_ticker") as mock_krx:
            mock_df = pd.DataFrame(
                {
                    "종가": [100, 101, 102],
                    "시가총액": [1000000, 1100000, 1200000],
                    "거래량": [1000, 1100, 1200],
                    "거래대금": [100000, 110000, 120000],
                    "상장주식수": [10000, 11000, 12000],
                },
                index=pd.Index(["005930", "000660", "373220"]),
            )
            mock_krx.return_value = mock_df

            result = get_market_cap_by_ticker("20240115", "KOSPI")

            # 결과 검증
            assert len(result) == 3
            mock_krx.assert_called_once_with("20240115", "KOSPI", False)

    def test_get_market_cap_by_ticker_with_ascending(self):
        """오름차순 정렬로 시가총액 조회 테스트"""
        with patch("pykrx.website.krx.get_market_cap_by_ticker") as mock_krx:
            mock_df = pd.DataFrame(
                {
                    "종가": [100, 101, 102],
                    "시가총액": [1000000, 1100000, 1200000],
                    "거래량": [1000, 1100, 1200],
                    "거래대금": [100000, 110000, 120000],
                    "상장주식수": [10000, 11000, 12000],
                },
                index=pd.Index(["005930", "000660", "373220"]),
            )
            mock_krx.return_value = mock_df

            result = get_market_cap_by_ticker("20240115", "KOSPI", acending=True)  # noqa: F841

            mock_krx.assert_called_once_with("20240115", "KOSPI", True)

    def test_get_market_cap_by_ticker_with_datetime(self):
        """datetime 객체로 티커별 시가총액 조회 테스트"""
        with (
            patch("pykrx.website.krx.datetime2string") as mock_datetime2string,
            patch("pykrx.website.krx.get_market_cap_by_ticker") as mock_krx,
        ):
            mock_datetime2string.return_value = "20240115"
            mock_df = pd.DataFrame(
                {
                    "종가": [100],
                    "시가총액": [1000000],
                    "거래량": [1000],
                    "거래대금": [100000],
                    "상장주식수": [10000],
                },
                index=pd.Index(["005930"]),
            )
            mock_krx.return_value = mock_df

            test_date = datetime.datetime(2024, 1, 15)
            result = get_market_cap_by_ticker(test_date, "KOSPI")  # type: ignore[arg-type]  # noqa: F841

            mock_krx.assert_called_once_with("20240115", "KOSPI", False)

    def test_get_market_cap_by_ticker_holiday_alternative(self):
        """휴일 대안 데이터 조회 테스트"""
        with (
            patch("pykrx.stock.stock_market_cap.krx.get_market_cap_by_ticker") as mock_krx,
            patch(
                "pykrx.stock.stock_market_cap.get_nearest_business_day_in_a_week"
            ) as mock_business_day,
        ):
            # 첫 번째 호출은 휴일 데이터 (모든 값이 0)
            holiday_df = pd.DataFrame(
                {
                    "종가": [0, 0],
                    "시가총액": [0, 0],
                    "거래량": [0, 0],
                    "거래대금": [0, 0],
                    "상장주식수": [0, 0],
                },
                index=pd.Index(["005930", "000660"]),
            )

            # 두 번째 호출은 정상 데이터
            normal_df = pd.DataFrame(
                {
                    "종가": [100, 101],
                    "시가총액": [1000000, 1100000],
                    "거래량": [1000, 1100],
                    "거래대금": [100000, 110000],
                    "상장주식수": [10000, 11000],
                },
                index=pd.Index(["005930", "000660"]),
            )

            mock_krx.side_effect = [holiday_df, normal_df]
            mock_business_day.return_value = "20240114"

            result = get_market_cap_by_ticker("20240115", "KOSPI", alternative=True)

            # alternative=True이므로 이전 영업일 데이터가 반환되어야 함
            assert len(result) == 2
            mock_business_day.assert_called_once_with(date="20240115", prev=True)

    def test_get_market_cap_function_dispatch(self):
        """get_market_cap 함수의 dispatch 로직 테스트"""
        with (
            patch("pykrx.stock.stock_market_cap.get_market_cap_by_date") as mock_by_date,
            patch("pykrx.stock.stock_market_cap.get_market_cap_by_ticker") as mock_by_ticker,
        ):
            mock_by_date.return_value = pd.DataFrame()
            mock_by_ticker.return_value = pd.DataFrame()

            # 2개 날짜 인자로 호출하면 by_date 함수가 호출되어야 함
            get_market_cap("20240115", "20240116", "005930")
            mock_by_date.assert_called_once()
            mock_by_ticker.assert_not_called()

            # 1개 날짜 인자로 호출하면 by_ticker 함수가 호출되어야 함
            get_market_cap("20240115")
            mock_by_ticker.assert_called_once()

    def test_get_market_cap_with_kwargs(self):
        """키워드 인자로 시가총액 조회 테스트"""
        with patch("pykrx.stock.stock_market_cap.get_market_cap_by_date") as mock_by_date:
            mock_by_date.return_value = pd.DataFrame()

            get_market_cap(fromdate="20240115", todate="20240116", ticker="005930")

            mock_by_date.assert_called_once_with(
                fromdate="20240115", todate="20240116", ticker="005930"
            )

    def test_get_market_cap_by_ticker_market_validation(self):
        """시장 유효성 검사 테스트"""
        with patch("pykrx.website.krx.get_market_cap_by_ticker") as mock_krx:
            mock_df = pd.DataFrame(
                {
                    "종가": [100],
                    "시가총액": [1000000],
                    "거래량": [1000],
                    "거래대금": [100000],
                    "상장주식수": [10000],
                },
                index=pd.Index(["005930"]),
            )
            mock_krx.return_value = mock_df

            # 유효한 시장
            result = get_market_cap_by_ticker("20240115", "KOSPI")
            assert len(result) == 1

            # 유효하지 않은 시장 (market_valid_check 데코레이터에 의해 빈 DataFrame 반환)
            result = get_market_cap_by_ticker("20240115", "INVALID")
            assert isinstance(result, pd.DataFrame)
            assert result.empty

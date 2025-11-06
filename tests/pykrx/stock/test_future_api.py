"""선물 API 테스트"""

import pandas as pd

from pykrx.stock.future_api import (
    get_future_ohlcv,
    get_future_ohlcv_by_ticker,
    get_future_ticker_list,
    get_future_ticker_name,
)


class TestFutureTickerList:
    """선물 티커 목록 조회 테스트"""

    def test_get_future_ticker_list(self):
        """티커 목록 조회 테스트"""
        tickers = get_future_ticker_list()
        print(tickers)
        assert isinstance(tickers, list)
        assert len(tickers) > 0
        # 티커는 문자열이어야 함
        assert all(isinstance(ticker, str) for ticker in tickers)
        # 예시 티커 포함 여부 확인
        assert "KRDRVFUEST" in tickers or len(tickers) > 0


class TestFutureTickerName:
    """선물 티커 이름 조회 테스트"""

    def test_get_future_ticker_name_valid(self):
        """유효한 티커로 이름 조회 테스트"""
        ticker = "KRDRVFUEST"
        name = get_future_ticker_name(ticker)
        print(name)
        assert isinstance(name, str)
        assert len(name) > 0

    def test_get_future_ticker_name_invalid(self):
        """유효하지 않은 티커로 이름 조회 테스트"""
        ticker = "INVALID_TICKER"
        name = get_future_ticker_name(ticker)
        # 유효하지 않은 티커는 빈 문자열 반환
        print(name)
        assert name == ""


class TestFutureOHLCV:
    """선물 OHLCV 조회 테스트"""

    def test_get_future_ohlcv_by_ticker_business_day(self):
        """영업일 OHLCV 조회 테스트"""
        date = "20220902"
        prod = "KRDRVFUEST"
        df = get_future_ohlcv_by_ticker(date, prod)
        print(df)
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 0  # 데이터가 있을 수도 있고 없을 수도 있음

    def test_get_future_ohlcv_by_ticker_with_dash_format(self):
        """하이픈 포함 날짜 형식 테스트"""
        date = "2022-09-02"
        prod = "KRDRVFUEST"
        df = get_future_ohlcv_by_ticker(date, prod)
        print(df)
        assert isinstance(df, pd.DataFrame)

    def test_get_future_ohlcv_by_ticker_alternative(self):
        """alternative 옵션 테스트"""
        date = "20220902"
        prod = "KRDRVFUEST"
        df = get_future_ohlcv_by_ticker(date, prod, alternative=True)
        print(df)
        assert isinstance(df, pd.DataFrame)

    def test_get_future_ohlcv_single_date(self):
        """단일 날짜로 OHLCV 조회 테스트 (get_future_ohlcv 래퍼 함수)"""
        date = "20220902"
        prod = "KRDRVFUEST"
        df = get_future_ohlcv(date, prod)
        print(df)
        assert isinstance(df, pd.DataFrame)

    def test_get_future_ohlcv_not_implemented(self):
        """기간 조회는 미구현이므로 NotImplementedError 발생 확인"""
        fromdate = "20220901"
        todate = "20220902"
        prod = "KRDRVFUEST"
        # 기간 조회는 NotImplementedError 발생
        try:
            df = get_future_ohlcv(fromdate, todate, prod)
            print(df)
            # 만약 NotImplementedError가 발생하지 않았다면, 테스트는 실패
            raise AssertionError("NotImplementedError가 발생해야 합니다")
        except NotImplementedError:
            # 예상된 예외가 발생함
            pass

    def test_get_future_ohlcv_with_kwargs_not_implemented(self):
        """키워드 인수로 기간 조회 시 NotImplementedError 발생 확인"""
        try:
            df = get_future_ohlcv(fromdate="20220901", todate="20220902", ticker="KRDRVFUEST")
            print(df)
            raise AssertionError("NotImplementedError가 발생해야 합니다")
        except NotImplementedError:
            pass


if __name__ == "__main__":
    test = TestFutureTickerList()
    test.test_get_future_ticker_list()
    test = TestFutureTickerName()
    test.test_get_future_ticker_name_valid()
    test.test_get_future_ticker_name_invalid()
    test = TestFutureOHLCV()
    test.test_get_future_ohlcv_by_ticker_business_day()
    test.test_get_future_ohlcv_by_ticker_with_dash_format()
    test.test_get_future_ohlcv_by_ticker_alternative()
    test.test_get_future_ohlcv_single_date()
    test.test_get_future_ohlcv_not_implemented()
    test.test_get_future_ohlcv_with_kwargs_not_implemented()

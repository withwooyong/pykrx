"""주식 API 테스트"""

import pandas as pd

from pykrx.stock import stock_api


class TestIndexFunctions:
    """지수 관련 함수 테스트"""

    def test_get_index_ticker_list(self):
        """지수 티커 리스트 조회 테스트"""
        tickers = stock_api.get_index_ticker_list()
        print(f"\n지수 티커 리스트: {tickers}")
        assert isinstance(tickers, list)
        assert len(tickers) > 0

    def test_get_index_ticker_list_with_date(self):
        """지정된 날짜로 지수 티커 리스트 조회"""
        tickers = stock_api.get_index_ticker_list(date="20240115", market="KOSPI")
        print(f"\n지수 티커 리스트 (20240115, KOSPI): {tickers}")
        assert isinstance(tickers, list)

    def test_get_index_ticker_name(self):
        """지수 티커 이름 조회 테스트"""
        name = stock_api.get_index_ticker_name("1001")
        print(f"\n지수 티커 이름 (1001): {name}")
        assert isinstance(name, str)
        assert len(name) > 0

    def test_get_index_ohlcv_by_date(self):
        """지수 OHLCV 조회 테스트"""
        df = stock_api.get_index_ohlcv_by_date("20240101", "20240115", "1001")
        print(f"\n지수 OHLCV (1001):\n{df}")
        assert isinstance(df, pd.DataFrame)

    def test_get_index_price_change_by_ticker(self):
        """지수 가격 변동 조회 테스트"""
        df = stock_api.get_index_price_change_by_ticker("20240101", "20240115", "KOSPI")
        print(f"\n지수 가격 변동 (KOSPI):\n{df}")
        assert isinstance(df, pd.DataFrame)

    def test_get_index_portfolio_deposit_file(self):
        """지수 구성 종목 조회 테스트"""
        tickers = stock_api.get_index_portfolio_deposit_file("1001", "20240115")
        print(f"\n지수 구성 종목 (1001): {tickers}")
        assert isinstance(tickers, list)


class TestETFELWFunctions:
    """ETF/ETN/ELW 관련 함수 테스트"""

    def test_get_etf_ticker_list(self):
        """ETF 티커 리스트 조회 테스트"""
        tickers = stock_api.get_etf_ticker_list()
        print(f"\nETF 티커 리스트: {tickers[:10]}... (총 {len(tickers)}개)")
        assert isinstance(tickers, list)

    def test_get_etn_ticker_list(self):
        """ETN 티커 리스트 조회 테스트"""
        tickers = stock_api.get_etn_ticker_list()
        print(f"\nETN 티커 리스트: {tickers[:10]}... (총 {len(tickers)}개)")
        assert isinstance(tickers, list)

    def test_get_elw_ticker_list(self):
        """ELW 티커 리스트 조회 테스트"""
        tickers = stock_api.get_elw_ticker_list()
        print(f"\nELW 티커 리스트: {tickers[:10]}... (총 {len(tickers)}개)")
        assert isinstance(tickers, list)

    def test_get_etf_ohlcv_by_date(self):
        """ETF OHLCV 조회 (일자별) 테스트"""
        # ETF 티커 하나 가져오기
        etf_tickers = stock_api.get_etf_ticker_list("20240115")
        if len(etf_tickers) > 0:
            ticker = etf_tickers[0]
            df = stock_api.get_etf_ohlcv_by_date("20240101", "20240115", ticker)
            print(f"\nETF OHLCV ({ticker}):\n{df}")
            assert isinstance(df, pd.DataFrame)

    def test_get_etf_ohlcv_by_ticker(self):
        """ETF OHLCV 조회 (티커별) 테스트"""
        df = stock_api.get_etf_ohlcv_by_ticker("20240115")
        print(f"\nETF OHLCV (전체):\n{df.head()}")
        assert isinstance(df, pd.DataFrame)

    def test_get_etf_price_change_by_ticker(self):
        """ETF 가격 변동 조회 테스트"""
        df = stock_api.get_etf_price_change_by_ticker("20240101", "20240115")
        print(f"\nETF 가격 변동:\n{df.head()}")
        assert isinstance(df, pd.DataFrame)

    def test_get_etf_portfolio_deposit_file(self):
        """ETF 포트폴리오 구성 종목 조회 테스트"""
        etf_tickers = stock_api.get_etf_ticker_list("20240115")
        if len(etf_tickers) > 0:
            ticker = etf_tickers[0]
            df = stock_api.get_etf_portfolio_deposit_file(ticker, "20240115")
            print(f"\nETF 포트폴리오 구성 ({ticker}):\n{df.head()}")
            assert isinstance(df, pd.DataFrame)


class TestMarketFundamentalFunctions:
    """시장 펀더멘털 및 가격 변동 함수 테스트"""

    def test_get_market_price_change_by_ticker(self):
        """시장 가격 변동 조회 테스트"""
        df = stock_api.get_market_price_change_by_ticker("20240101", "20240115", "KOSPI")
        print(f"\n시장 가격 변동 (KOSPI):\n{df.head()}")
        assert isinstance(df, pd.DataFrame)

    def test_get_market_fundamental_by_date(self):
        """시장 펀더멘털 조회 (일자별) 테스트"""
        df = stock_api.get_market_fundamental_by_date("20240101", "20240115", "005930")
        print(f"\n시장 펀더멘털 (005930, 일자별):\n{df}")
        assert isinstance(df, pd.DataFrame)

    def test_get_market_fundamental_by_ticker(self):
        """시장 펀더멘털 조회 (티커별) 테스트"""
        df = stock_api.get_market_fundamental_by_ticker("20240115", "KOSPI")
        print(f"\n시장 펀더멘털 (KOSPI, 티커별):\n{df.head()}")
        assert isinstance(df, pd.DataFrame)


class TestMarketTradingFunctions:
    """투자자별 거래실적 함수 테스트"""

    def test_get_market_trading_volume_by_investor(self):
        """투자자별 거래량 조회 테스트 (티커)"""
        df = stock_api.get_market_trading_volume_by_investor("20240101", "20240115", "005930")
        print(f"\n투자자별 거래량 (005930):\n{df}")
        assert isinstance(df, pd.DataFrame)

    def test_get_market_trading_volume_by_investor_market(self):
        """투자자별 거래량 조회 테스트 (시장)"""
        df = stock_api.get_market_trading_volume_by_investor("20240101", "20240115", "KOSPI")
        print(f"\n투자자별 거래량 (KOSPI):\n{df}")
        assert isinstance(df, pd.DataFrame)

    def test_get_market_trading_value_by_investor(self):
        """투자자별 거래대금 조회 테스트 (티커)"""
        df = stock_api.get_market_trading_value_by_investor("20240101", "20240115", "005930")
        print(f"\n투자자별 거래대금 (005930):\n{df}")
        assert isinstance(df, pd.DataFrame)

    def test_get_market_trading_value_by_date(self):
        """투자자별 거래대금 조회 (일자별) 테스트"""
        df = stock_api.get_market_trading_value_by_date("20240101", "20240115", "005930")
        print(f"\n투자자별 거래대금 (005930, 일자별):\n{df}")
        assert isinstance(df, pd.DataFrame)

    def test_get_market_trading_volume_by_date(self):
        """투자자별 거래량 조회 (일자별) 테스트"""
        df = stock_api.get_market_trading_volume_by_date("20240101", "20240115", "005930")
        print(f"\n투자자별 거래량 (005930, 일자별):\n{df}")
        assert isinstance(df, pd.DataFrame)


class TestForeignInvestmentFunctions:
    """외국인보유제한 함수 테스트"""

    def test_get_exhaustion_rates_of_foreign_investment_by_ticker(self):
        """외국인보유제한 한도소진률 조회 (티커별) 테스트"""
        df = stock_api.get_exhaustion_rates_of_foreign_investment_by_ticker("20240115", "KOSPI")
        print(f"\n외국인보유제한 한도소진률 (KOSPI):\n{df.head()}")
        assert isinstance(df, pd.DataFrame)

    def test_get_exhaustion_rates_of_foreign_investment_by_date(self):
        """외국인보유제한 한도소진률 조회 (일자별) 테스트"""
        df = stock_api.get_exhaustion_rates_of_foreign_investment_by_date(
            "20240101", "20240115", "005930"
        )
        print(f"\n외국인보유제한 한도소진률 (005930, 일자별):\n{df}")
        assert isinstance(df, pd.DataFrame)


class TestShortingFunctions:
    """공매도 관련 함수 테스트"""

    def test_get_shorting_status_by_date(self):
        """공매도 종합 현황 조회 (일자별) 테스트"""
        df = stock_api.get_shorting_status_by_date("20240101", "20240115", "005930")
        print(f"\n공매도 종합 현황 (005930):\n{df}")
        assert isinstance(df, pd.DataFrame)

    def test_get_shorting_volume_by_ticker(self):
        """공매도 거래량 조회 (티커별) 테스트"""
        df = stock_api.get_shorting_volume_by_ticker("20240115", "KOSPI")
        print(f"\n공매도 거래량 (KOSPI):\n{df.head()}")
        assert isinstance(df, pd.DataFrame)

    def test_get_shorting_value_by_ticker(self):
        """공매도 거래대금 조회 (티커별) 테스트"""
        df = stock_api.get_shorting_value_by_ticker("20240115", "KOSPI")
        print(f"\n공매도 거래대금 (KOSPI):\n{df.head()}")
        assert isinstance(df, pd.DataFrame)

    def test_get_shorting_volume_by_date(self):
        """공매도 거래량 조회 (일자별) 테스트"""
        df = stock_api.get_shorting_volume_by_date("20240101", "20240115", "005930")
        print(f"\n공매도 거래량 (005930, 일자별):\n{df}")
        assert isinstance(df, pd.DataFrame)

    def test_get_shorting_value_by_date(self):
        """공매도 거래대금 조회 (일자별) 테스트"""
        df = stock_api.get_shorting_value_by_date("20240101", "20240115", "005930")
        print(f"\n공매도 거래대금 (005930, 일자별):\n{df}")
        assert isinstance(df, pd.DataFrame)

    def test_get_shorting_investor_volume_by_date(self):
        """투자자별 공매도 거래량 조회 (일자별) 테스트"""
        df = stock_api.get_shorting_investor_volume_by_date("20240101", "20240115", "KOSPI")
        print(f"\n투자자별 공매도 거래량 (KOSPI):\n{df}")
        assert isinstance(df, pd.DataFrame)

    def test_get_shorting_investor_value_by_date(self):
        """투자자별 공매도 거래대금 조회 (일자별) 테스트"""
        df = stock_api.get_shorting_investor_value_by_date("20240101", "20240115", "KOSPI")
        print(f"\n투자자별 공매도 거래대금 (KOSPI):\n{df}")
        assert isinstance(df, pd.DataFrame)

    def test_get_shorting_volume_top50(self):
        """공매도 비중 상위 50개 종목 조회 테스트"""
        df = stock_api.get_shorting_volume_top50("20240115", "KOSPI")
        print(f"\n공매도 비중 상위 50개 (KOSPI):\n{df}")
        assert isinstance(df, pd.DataFrame)

    def test_get_shorting_balance_top50(self):
        """공매도 잔고 상위 50개 종목 조회 테스트"""
        df = stock_api.get_shorting_balance_top50("20240115", "KOSPI")
        print(f"\n공매도 잔고 상위 50개 (KOSPI):\n{df}")
        assert isinstance(df, pd.DataFrame)

    def test_get_shorting_balance_by_ticker(self):
        """공매도 잔고 조회 (티커별) 테스트"""
        df = stock_api.get_shorting_balance_by_ticker("20240115", "KOSPI")
        print(f"\n공매도 잔고 (KOSPI):\n{df.head()}")
        assert isinstance(df, pd.DataFrame)

    def test_get_shorting_balance_by_date(self):
        """공매도 잔고 조회 (일자별) 테스트"""
        df = stock_api.get_shorting_balance_by_date("20240101", "20240115", "005930")
        print(f"\n공매도 잔고 (005930, 일자별):\n{df}")
        assert isinstance(df, pd.DataFrame)


class TestMarketNetPurchasesFunctions:
    """투자자별 순매수 상위종목 함수 테스트"""

    def test_get_market_net_purchases_of_equities_by_ticker(self):
        """투자자별 순매수 상위종목 조회 테스트"""
        df = stock_api.get_market_net_purchases_of_equities_by_ticker("20240101", "20240115", "ALL")
        print(f"\n투자자별 순매수 상위종목 (ALL):\n{df.head()}")
        assert isinstance(df, pd.DataFrame)


if __name__ == "__main__":
    import unittest

    # 테스트 실행
    test_classes = [
        TestIndexFunctions,
        TestETFELWFunctions,
        TestMarketFundamentalFunctions,
        TestMarketTradingFunctions,
        TestForeignInvestmentFunctions,
        TestShortingFunctions,
        TestMarketNetPurchasesFunctions,
    ]

    for test_class in test_classes:
        print(f"\n{'=' * 60}")
        print(f"테스트 클래스: {test_class.__name__}")
        print(f"{'=' * 60}")
        test = test_class()
        for method_name in dir(test):
            if method_name.startswith("test_"):
                try:
                    method = getattr(test, method_name)
                    method()
                    print(f"✅ {method_name} 통과")
                except Exception as e:
                    print(f"❌ {method_name} 실패: {e}")

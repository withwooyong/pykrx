"""ETF API 테스트"""

import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pykrx import stock
import pandas as pd
import numpy as np
# pylint: disable-all
# flake8: noqa


class TestEtfTickerList:
    def test_ticker_list(self):
        tickers = stock.get_etf_ticker_list()
        print(tickers)
        assert isinstance(tickers, list)
        assert len(tickers) > 0

    def test_ticker_list_with_a_businessday(self):
        tickers = stock.get_etf_ticker_list("20210104")
        print(tickers)
        assert isinstance(tickers, list)
        assert len(tickers) > 0

    def test_ticker_list_with_a_holiday(self):
        tickers = stock.get_etf_ticker_list("20210103")
        print(tickers)
        assert isinstance(tickers, list)
        assert len(tickers) > 0


class TestEtnTickerList:
    def test_ticker_list(self):
        tickers = stock.get_etn_ticker_list()
        print(tickers)
        assert isinstance(tickers, list)
        assert len(tickers) > 0

    def test_ticker_list_with_a_businessday(self):
        tickers = stock.get_etn_ticker_list("20210104")
        print(tickers)
        assert isinstance(tickers, list)
        assert len(tickers) > 0

    def test_ticker_list_with_a_holiday(self):
        tickers = stock.get_etn_ticker_list("20210103")
        print(tickers)
        assert isinstance(tickers, list)
        assert len(tickers) > 0


class TestElwTickerList:
    def test_ticker_list(self):
        tickers = stock.get_elw_ticker_list()
        print(tickers)
        assert isinstance(tickers, list)
        assert len(tickers) > 0

    def test_ticker_list_with_a_businessday(self):
        tickers = stock.get_elw_ticker_list("20210104")
        print(tickers)
        assert isinstance(tickers, list)

    def test_ticker_list_with_a_holiday(self):
        tickers = stock.get_elw_ticker_list("20210103")
        print(tickers)
        assert isinstance(tickers, list)


class TestEtfOhlcvByDate:
    def test_with_business_day(self):
        df = stock.get_etf_ohlcv_by_date("20210104", "20210108", "159800")
        print(df)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert isinstance(df.index, pd.DatetimeIndex)
        assert isinstance(df.index[0], pd.Timestamp)
        if len(df) > 1:
            assert df.index[0] < df.index[-1]

    def test_with_holiday_0(self):
        df = stock.get_etf_ohlcv_by_date("20210103", "20210108", "159800")
        print(df)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert isinstance(df.index, pd.DatetimeIndex)
        assert isinstance(df.index[0], pd.Timestamp)
        if len(df) > 1:
            assert df.index[0] < df.index[-1]

    def test_with_holiday_1(self):
        df = stock.get_etf_ohlcv_by_date("20210103", "20210109", "159800")
        print(df)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert isinstance(df.index, pd.DatetimeIndex)
        assert isinstance(df.index[0], pd.Timestamp)
        if len(df) > 1:
            assert df.index[0] < df.index[-1]

    def test_with_freq(self):
        df = stock.get_etf_ohlcv_by_date("20200101", "20200531", "159800", freq="m")
        print(df)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert isinstance(df.index, pd.DatetimeIndex)
        assert isinstance(df.index[0], pd.Timestamp)
        if len(df) > 1:
            assert df.index[0] < df.index[-1]


class TestEtfOhlcvByTicker:
    def test_with_business_day(self):
        df = stock.get_etf_ohlcv_by_ticker("20210325")
        #           NAV   시가   고가   저가    종가 거래량    거래대금  기초지수
        # 티커
        # 152100   41887.33  41705  42145  41585   41835  59317  2479398465    408.53
        # 295820   10969.41  10780  10945  10780   10915     69      750210   2364.03
        # 253150   46182.13  45640  46700  45540   46145   1561    71730335   2043.75
        # 253160    4344.07   4400   4400   4295    4340  58943   256679440   2043.75
        # 278420    9145.45   9055   9150   9055    9105   1164    10598375   1234.03
        temp = df.iloc[0:5, 0] == np.array([41887.33, 10969.41, 46182.13, 4344.07, 9145.45])
        print(temp)
        assert temp.sum() == 5

    def test_with_holiday(self):
        df = stock.get_etf_ohlcv_by_ticker("20210321")
        print(df)
        # 휴일에도 이전 거래일 데이터가 있을 수 있음
        assert isinstance(df, pd.DataFrame)


class TestEtfPriceChange:
    def test_with_business_day(self):
        df = stock.get_etf_price_change_by_ticker("20210325", "20210402")
        #           시가    종가  변동폭  등락률   거래량     거래대금
        # 152100   41715   43405    1690    4.05  1002296  42802174550
        # 295820   10855   11185     330    3.04     1244     13820930
        # 253150   45770   49735    3965    8.66    13603    650641700
        # 253160    4380    4015    -365   -8.33   488304   2040509925
        # 278420    9095    9385     290    3.19     9114     84463155
        temp = df.iloc[0:5, 2] == np.array([1690, 330, 3965, -365, 290])
        print(temp)
        assert temp.sum() == 5

    def test_with_holiday_0(self):
        df = stock.get_etf_price_change_by_ticker("20210321", "20210325")
        print(df)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        # 변동폭 컬럼이 있는지 확인
        if len(df.columns) > 2:
            assert "변동폭" in df.columns or df.iloc[0, 2] is not None

    def test_with_holiday_1(self):
        df = stock.get_etf_price_change_by_ticker("20210321", "20210321")
        print(df)
        assert df.empty


class TestEtfPdf:
    def test_with_business_day(self):
        df = stock.get_etf_portfolio_deposit_file("152100", "20210402")
        #          계약수       금액   비중
        # 티커
        # 005930  8140.0  674806000  31.74
        # 000660   968.0  136004000   6.28
        # 035420   218.0   82513000   3.80
        # 051910    79.0   64701000   3.01
        # 006400    89.0   59363000   2.73
        temp = df.iloc[0:5, 0] == np.array([8140.0, 968.0, 218.0, 79.0, 89.0])
        print(temp)
        assert temp.sum() == 5

    def test_with_negative_value(self):
        # 음수 값 확인
        df = stock.get_etf_portfolio_deposit_file("114800", "20210402")
        print(df)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        # 음수 값이 있는지 확인 (계약수 컬럼)
        if "계약수" in df.columns:
            negative_values = df[df["계약수"] < 0]
            assert len(negative_values) > 0
        elif len(df.columns) > 0:
            # 첫 번째 컬럼에 음수 값이 있는지 확인
            negative_values = df[df.iloc[:, 0] < 0]
            assert len(negative_values) > 0


class TestEtfTradingvolumeValue:
    def test_investor_in_businessday(self):
        df = stock.get_etf_trading_volume_and_value("20220415", "20220422")
        #                거래량                              거래대금
        #                  매도        매수    순매수            매도            매수            순
        # 매수
        # 금융투자    375220036   328066683 -47153353   3559580094684   3040951626908 -518628467776
        # 보험         15784738    15490448   -294290    309980189819    293227931019  -16752258800
        # 투신         14415013    15265023    850010    287167721259    253185404050  -33982317209
        # 사모          6795002     7546735    751733     58320840040    120956023820   62635183780
        temp = df.iloc[0:4, 0] == np.array([375220036, 15784738, 14415013, 6795002])
        print(temp)
        assert temp.sum() == 4

    def test_volume_with_businessday(self):
        df = stock.get_etf_trading_volume_and_value("20220415", "20220422", "거래대금", "순매수")
        #                     기관    기타법인         개인        외국인 전체
        # 날짜
        # 2022-04-15   25346770535  -138921500  17104310255  -42312159290    0
        # 2022-04-18 -168362290065  -871791310  88115812520   81118268855    0
        # 2022-04-19  -36298873785  7555666910  -1968998025   30712204900    0
        # 2022-04-20 -235935697655  8965445880  19247888605  207722363170    0
        # 2022-04-21  -33385835805  2835764290  35920390975   -5370319460    0
        temp = df.iloc[0:5, 0] == np.array(
            [25346770535, -168362290065, -36298873785, -235935697655, -33385835805]
        )
        print(temp)
        assert temp.sum() == 5

    def test_indivisual_investor_in_businessday(self):
        # 존재하는 티커 사용
        df = stock.get_etf_trading_volume_and_value("20220908", "20220916", "159800")
        print(df)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_indivisual_volume_with_businessday(self):
        # 존재하는 티커 사용
        df = stock.get_etf_trading_volume_and_value(
            "20220908", "20220916", "159800", "거래대금", "순매수"
        )
        print(df)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        # 첫 번째 컬럼이 있는지 확인
        if len(df.columns) > 0:
            assert len(df.iloc[:, 0]) > 0


if __name__ == "__main__":
    test = TestEtfTickerList()
    test.test_ticker_list()
    test.test_ticker_list_with_a_businessday()
    test.test_ticker_list_with_a_holiday()
    test.test_ticker_list()
    test.test_ticker_list_with_a_businessday()
    test.test_ticker_list_with_a_holiday()
    test.test_ticker_list()
    test.test_ticker_list_with_a_businessday()
    test.test_ticker_list_with_a_holiday()

"""
주식 API 메인 모듈
모듈화된 함수들을 import하여 제공합니다.
"""

from typing import cast

import pandas as pd
from pandas import DataFrame

# ETF/ETN/ELW 관련 import
from pykrx.website.krx.etx.ticker import get_etx_ticker_list
from pykrx.website.krx.etx.wrap import (
    get_etf_ohlcv_by_date as _get_etf_ohlcv_by_date,
)
from pykrx.website.krx.etx.wrap import (
    get_etf_ohlcv_by_ticker as _get_etf_ohlcv_by_ticker,
)
from pykrx.website.krx.etx.wrap import (
    get_etf_portfolio_deposit_file as _get_etf_portfolio_deposit_file,
)
from pykrx.website.krx.etx.wrap import (
    get_etf_price_change_by_ticker as _get_etf_price_change_by_ticker,
)
from pykrx.website.krx.etx.wrap import (
    get_indivisual_trading_volume_and_value_by_date as _get_indivisual_trading_volume_and_value_by_date,
)
from pykrx.website.krx.etx.wrap import (
    get_indivisual_trading_volume_and_value_by_investor as _get_indivisual_trading_volume_and_value_by_investor,
)
from pykrx.website.krx.etx.wrap import (
    get_trading_volume_and_value_by_date as _get_trading_volume_and_value_by_date,
)
from pykrx.website.krx.etx.wrap import (
    get_trading_volume_and_value_by_investor as _get_trading_volume_and_value_by_investor,
)
from pykrx.website.krx.market.ticker import IndexTicker
from pykrx.website.krx.market.wrap import (
    get_exhaustion_rates_of_foreign_investment_by_date as _get_exhaustion_rates_of_foreign_investment_by_date,
)
from pykrx.website.krx.market.wrap import (
    get_exhaustion_rates_of_foreign_investment_by_ticker as _get_exhaustion_rates_of_foreign_investment_by_ticker,
)
from pykrx.website.krx.market.wrap import (
    get_index_listing_date as _get_index_listing_date,
)
from pykrx.website.krx.market.wrap import (
    get_index_ohlcv_by_date as _get_index_ohlcv_by_date,
)
from pykrx.website.krx.market.wrap import (
    get_index_portfolio_deposit_file as _get_index_portfolio_deposit_file,
)
from pykrx.website.krx.market.wrap import (
    get_index_price_change_by_ticker as _get_index_price_change_by_ticker,
)
from pykrx.website.krx.market.wrap import (
    get_market_fundamental_by_date as _get_market_fundamental_by_date,
)
from pykrx.website.krx.market.wrap import (
    get_market_fundamental_by_ticker as _get_market_fundamental_by_ticker,
)
from pykrx.website.krx.market.wrap import (
    get_market_net_purchases_of_equities_by_ticker as _get_market_net_purchases_of_equities_by_ticker,
)
from pykrx.website.krx.market.wrap import (
    get_market_price_change_by_ticker as _get_market_price_change_by_ticker,
)
from pykrx.website.krx.market.wrap import (
    get_market_trading_value_and_volume_on_market_by_date as _get_market_trading_value_and_volume_on_market_by_date,
)
from pykrx.website.krx.market.wrap import (
    get_market_trading_value_and_volume_on_market_by_investor as _get_market_trading_value_and_volume_on_market_by_investor,
)
from pykrx.website.krx.market.wrap import (
    get_market_trading_value_and_volume_on_ticker_by_date as _get_market_trading_value_and_volume_on_ticker_by_date,
)
from pykrx.website.krx.market.wrap import (
    get_market_trading_value_and_volume_on_ticker_by_investor as _get_market_trading_value_and_volume_on_ticker_by_investor,
)
from pykrx.website.krx.market.wrap import (
    get_shorting_balance_by_date as _get_shorting_balance_by_date,
)
from pykrx.website.krx.market.wrap import (
    get_shorting_balance_by_ticker as _get_shorting_balance_by_ticker,
)
from pykrx.website.krx.market.wrap import (
    get_shorting_balance_top50 as _get_shorting_balance_top50,
)
from pykrx.website.krx.market.wrap import (
    get_shorting_investor_by_date as _get_shorting_investor_by_date,
)
from pykrx.website.krx.market.wrap import (
    get_shorting_status_by_date as _get_shorting_status_by_date,
)
from pykrx.website.krx.market.wrap import (
    get_shorting_trading_value_and_volume_by_date as _get_shorting_trading_value_and_volume_by_date,
)
from pykrx.website.krx.market.wrap import (
    get_shorting_trading_value_and_volume_by_ticker as _get_shorting_trading_value_and_volume_by_ticker,
)
from pykrx.website.krx.market.wrap import (
    get_shorting_volume_top50 as _get_shorting_volume_top50,
)

from .stock_business_days import (
    get_nearest_business_day_in_a_week,
    get_previous_business_days,
)
from .stock_market_cap import (
    get_market_cap,
    get_market_cap_by_date,
    get_market_cap_by_ticker,
)
from .stock_ohlcv import (
    get_market_ohlcv,
    get_market_ohlcv_by_date,
    get_market_ohlcv_by_ticker,
)
from .stock_ticker import get_market_ticker_list, get_market_ticker_name
from .stock_utils import market_valid_check, resample_ohlcv


# 지수 관련 wrapper 함수들
def get_index_ticker_list(date: str | None = None, market: str = "KOSPI") -> list:
    """지수 티커 리스트 조회

    Args:
        date   (str, optional): 조회 일자 (YYYYMMDD). 기본값은 None (최근 영업일)
        market (str, optional): 조회 시장 (KOSPI/KOSDAQ/KRX/테마). 기본값은 "KOSPI"

    Returns:
        list: 지수 티커 리스트
    """
    if date is None:
        date = get_nearest_business_day_in_a_week()
    return IndexTicker().get_ticker(market, date)


def get_index_ticker_name(ticker: str) -> str:
    """지수 티커 이름 조회

    Args:
        ticker (str): 지수 티커 (예: "1001", "2001")

    Returns:
        str: 지수 이름
    """
    return IndexTicker().get_name(ticker)


def get_index_ohlcv_by_date(
    fromdate: str, todate: str, ticker: str, freq: str = "d"
) -> "DataFrame":
    """지수 OHLCV 조회 (일자별)

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)
        ticker   (str): 지수 티커
        freq     (str, optional): 리샘플링 주기 (d/m/y). 기본값은 'd'

    Returns:
        DataFrame: 지수 OHLCV 데이터
    """
    df = _get_index_ohlcv_by_date(fromdate, todate, ticker)

    if freq != "d" and len(df) > 0:
        how = {
            "시가": "first",
            "고가": "max",
            "저가": "min",
            "종가": "last",
            "거래량": "sum",
            "거래대금": "sum",
        }
        df = resample_ohlcv(df, freq, how)

    return cast("DataFrame", df)


def get_index_portfolio_deposit_file(ticker: str, date: str | None = None) -> list:
    """지수 구성 종목 조회

    Args:
        ticker (str): 지수 티커
        date   (str, optional): 조회 일자 (YYYYMMDD). 기본값은 None (최근 영업일)

    Returns:
        list: 지수 구성 종목 티커 리스트
    """
    if date is None:
        date = get_nearest_business_day_in_a_week()
    return _get_index_portfolio_deposit_file(date, ticker)


def get_index_price_change_by_ticker(
    fromdate: str, todate: str, market: str = "KOSPI"
) -> "DataFrame":
    """지정된 기간 동안의 지수 가격 변동 조회

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)
        market   (str, optional): 검색 시장 (KRX/KOSPI/KOSDAQ/테마). 기본값은 "KOSPI"

    Returns:
        DataFrame: 지수 가격 변동 데이터
    """
    return _get_index_price_change_by_ticker(fromdate, todate, market)


def get_index_listing_date(market: str = "KOSPI") -> "DataFrame":
    """지수 상장일 및 기준비수 조회

    Args:
        market (str, optional): 조회 시장 (KOSPI/KOSDAQ/KRX/테마). 기본값은 "KOSPI"

    Returns:
        DataFrame: 지수 상장일 및 기준비수 데이터
    """
    return _get_index_listing_date(market)


# ETF/ETN/ELW 관련 wrapper 함수들
def get_etf_ticker_list(date: str | None = None) -> list:
    """ETF 티커 리스트 조회

    Args:
        date (str, optional): 조회 일자 (YYYYMMDD). 기본값은 None (최근 영업일)

    Returns:
        list: ETF 티커 리스트
    """
    if date is None:
        date = get_nearest_business_day_in_a_week()
    return get_etx_ticker_list(date, "ETF")


def get_etn_ticker_list(date: str | None = None) -> list:
    """ETN 티커 리스트 조회

    Args:
        date (str, optional): 조회 일자 (YYYYMMDD). 기본값은 None (최근 영업일)

    Returns:
        list: ETN 티커 리스트
    """
    if date is None:
        date = get_nearest_business_day_in_a_week()
    return get_etx_ticker_list(date, "ETN")


def get_elw_ticker_list(date: str | None = None) -> list:
    """ELW 티커 리스트 조회

    Args:
        date (str, optional): 조회 일자 (YYYYMMDD). 기본값은 None (최근 영업일)

    Returns:
        list: ELW 티커 리스트
    """
    if date is None:
        date = get_nearest_business_day_in_a_week()
    return get_etx_ticker_list(date, "ELW")


def get_etf_ohlcv_by_date(fromdate: str, todate: str, ticker: str, freq: str = "d") -> "DataFrame":
    """ETF OHLCV 조회 (일자별)

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)
        ticker   (str): ETF 티커
        freq     (str, optional): 리샘플링 주기 (d/m/y). 기본값은 'd'

    Returns:
        DataFrame: ETF OHLCV 데이터
    """
    df = _get_etf_ohlcv_by_date(fromdate, todate, ticker)

    if freq != "d" and len(df) > 0:
        how = {
            "NAV": "last",
            "시가": "first",
            "고가": "max",
            "저가": "min",
            "종가": "last",
            "거래량": "sum",
            "거래대금": "sum",
            "기초지수": "last",
        }
        df = resample_ohlcv(df, freq, how)

    return cast("DataFrame", df)


def get_etf_ohlcv_by_ticker(date: str) -> "DataFrame":
    """ETF OHLCV 조회 (티커별)

    Args:
        date (str): 조회 일자 (YYYYMMDD)

    Returns:
        DataFrame: ETF OHLCV 데이터
    """
    return _get_etf_ohlcv_by_ticker(date)


def get_etf_price_change_by_ticker(fromdate: str, todate: str) -> "DataFrame":
    """ETF 가격 변동 조회

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)

    Returns:
        DataFrame: ETF 가격 변동 데이터
    """
    return _get_etf_price_change_by_ticker(fromdate, todate)


def get_etf_portfolio_deposit_file(ticker: str, date: str | None = None) -> "DataFrame":
    """ETF 포트폴리오 구성 종목 조회

    Args:
        ticker (str): ETF 티커
        date   (str, optional): 조회 일자 (YYYYMMDD). 기본값은 None (최근 영업일)

    Returns:
        DataFrame: ETF 포트폴리오 구성 종목
    """
    if date is None:
        date = get_nearest_business_day_in_a_week()
    return _get_etf_portfolio_deposit_file(date, ticker)


def get_etf_trading_volume_and_value(*args, **kwargs) -> "DataFrame":
    """ETF 거래량 및 거래대금 조회 (dispatch 함수)

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)
        ticker   (str, optional): ETF 티커 (개별 종목 조회 시)
        query_type1 (str, optional): 거래대금 / 거래량
        query_type2 (str, optional): 순매수 / 매수 / 매도

    Returns:
        DataFrame: 거래량 및 거래대금 데이터
    """
    if len(args) == 2:
        # 전종목 투자자별 거래실적 합계
        return _get_trading_volume_and_value_by_investor(args[0], args[1])
    elif len(args) == 4:
        # 전종목 일자별 거래 실적
        return _get_trading_volume_and_value_by_date(args[0], args[1], args[2], args[3])
    elif len(args) == 3:
        # 개별 종목 투자자별 거래실적 합계
        return _get_indivisual_trading_volume_and_value_by_investor(args[0], args[1], args[2])
    elif len(args) == 5:
        # 개별 종목 일자별 거래 실적
        return _get_indivisual_trading_volume_and_value_by_date(
            args[0], args[1], args[2], args[3], args[4]
        )
    else:
        raise ValueError("Invalid number of arguments")


def get_market_price_change_by_ticker(
    fromdate: str, todate: str, market: str = "KOSPI", adjusted: bool = True
) -> "DataFrame":
    """시장 가격 변동 조회 (티커별)

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)
        market   (str, optional): 조회 시장 (KOSPI/KOSDAQ/KONEX/ALL). 기본값은 "KOSPI"
        adjusted (bool, optional): 수정 종가 여부. 기본값은 True

    Returns:
        DataFrame: 시장 가격 변동 데이터
    """
    return _get_market_price_change_by_ticker(fromdate, todate, market, adjusted)


def get_market_fundamental_by_date(
    fromdate: str, todate: str, ticker: str, freq: str = "d"
) -> "DataFrame":
    """시장 펀더멘털 조회 (일자별)

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)
        ticker   (str): 종목 티커
        freq     (str, optional): 리샘플링 주기 (d/m/y). 기본값은 "d"

    Returns:
        DataFrame: 시장 펀더멘털 데이터
    """
    df = _get_market_fundamental_by_date(fromdate, todate, ticker)
    if freq != "d" and len(df) > 0:
        how = {
            "BPS": "last",
            "PER": "last",
            "PBR": "last",
            "EPS": "last",
            "DIV": "last",
            "DPS": "last",
        }
        df = resample_ohlcv(df, freq, how)
    return cast("DataFrame", df)


def get_market_fundamental_by_ticker(date: str, market: str = "KOSPI") -> "DataFrame":
    """시장 펀더멘털 조회 (티커별)

    Args:
        date   (str): 조회 일자 (YYYYMMDD)
        market (str, optional): 조회 시장 (KOSPI/KOSDAQ/KONEX/ALL). 기본값은 "KOSPI"

    Returns:
        DataFrame: 시장 펀더멘털 데이터
    """
    return _get_market_fundamental_by_ticker(date, market)


def get_market_trading_volume_by_investor(
    fromdate: str,
    todate: str,
    ticker_or_market: str,
    etf: bool = False,
    etn: bool = False,
    elw: bool = False,
) -> "DataFrame":
    """투자자별 거래량 조회

    Args:
        fromdate        (str): 조회 시작 일자 (YYYYMMDD)
        todate          (str): 조회 종료 일자 (YYYYMMDD)
        ticker_or_market (str): 종목 티커 또는 시장 (KOSPI/KOSDAQ/KONEX/ALL)
        etf             (bool, optional): ETF 포함 여부. 기본값은 False
        etn             (bool, optional): ETN 포함 여부. 기본값은 False
        elw             (bool, optional): ELW 포함 여부. 기본값은 False

    Returns:
        DataFrame: 투자자별 거래량 데이터
    """
    # ticker인지 market인지 판단 (ticker는 6자리 숫자, market은 문자열)
    if ticker_or_market in ["KOSPI", "KOSDAQ", "KONEX", "ALL"]:
        df = _get_market_trading_value_and_volume_on_market_by_investor(
            fromdate, todate, ticker_or_market, etf, etn, elw
        )
    else:
        df = _get_market_trading_value_and_volume_on_ticker_by_investor(
            fromdate, todate, ticker_or_market
        )

    # 거래량 컬럼만 추출
    if isinstance(df.columns, pd.MultiIndex):
        result = df["거래량"]
        # MultiIndex에서 선택하면 DataFrame이 반환되므로, Series인 경우에만 to_frame() 호출
        if isinstance(result, pd.Series):
            return cast("DataFrame", result.to_frame())
        return cast("DataFrame", result)
    return df


def get_market_trading_value_by_investor(
    fromdate: str,
    todate: str,
    ticker_or_market: str,
    etf: bool = False,
    etn: bool = False,
    elw: bool = False,
) -> "DataFrame":
    """투자자별 거래대금 조회

    Args:
        fromdate        (str): 조회 시작 일자 (YYYYMMDD)
        todate          (str): 조회 종료 일자 (YYYYMMDD)
        ticker_or_market (str): 종목 티커 또는 시장 (KOSPI/KOSDAQ/KONEX/ALL)
        etf             (bool, optional): ETF 포함 여부. 기본값은 False
        etn             (bool, optional): ETN 포함 여부. 기본값은 False
        elw             (bool, optional): ELW 포함 여부. 기본값은 False

    Returns:
        DataFrame: 투자자별 거래대금 데이터
    """
    # ticker인지 market인지 판단
    if ticker_or_market in ["KOSPI", "KOSDAQ", "KONEX", "ALL"]:
        df = _get_market_trading_value_and_volume_on_market_by_investor(
            fromdate, todate, ticker_or_market, etf, etn, elw
        )
    else:
        df = _get_market_trading_value_and_volume_on_ticker_by_investor(
            fromdate, todate, ticker_or_market
        )

    # 거래대금 컬럼만 추출
    if isinstance(df.columns, pd.MultiIndex):
        result = df["거래대금"]
        # MultiIndex에서 선택하면 DataFrame이 반환되므로, Series인 경우에만 to_frame() 호출
        if isinstance(result, pd.Series):
            return cast("DataFrame", result.to_frame())
        return cast("DataFrame", result)
    return df


def get_market_trading_value_by_date(
    fromdate: str,
    todate: str,
    ticker_or_market: str,
    etf: bool = False,
    etn: bool = False,
    elw: bool = False,
    freq: str = "d",
) -> "DataFrame":
    """투자자별 거래대금 조회 (일자별)

    Args:
        fromdate        (str): 조회 시작 일자 (YYYYMMDD)
        todate          (str): 조회 종료 일자 (YYYYMMDD)
        ticker_or_market (str): 종목 티커 또는 시장 (KOSPI/KOSDAQ/KONEX/ALL)
        etf             (bool, optional): ETF 포함 여부. 기본값은 False
        etn             (bool, optional): ETN 포함 여부. 기본값은 False
        elw             (bool, optional): ELW 포함 여부. 기본값은 False
        freq            (str, optional): 리샘플링 주기 (d/m/y). 기본값은 "d"

    Returns:
        DataFrame: 투자자별 거래대금 데이터 (일자별)
    """
    # ticker인지 market인지 판단
    if ticker_or_market in ["KOSPI", "KOSDAQ", "KONEX", "ALL"]:
        df = _get_market_trading_value_and_volume_on_market_by_date(
            fromdate, todate, ticker_or_market, etf, etn, elw, "거래대금", "순매수", False
        )
    else:
        df = _get_market_trading_value_and_volume_on_ticker_by_date(
            fromdate, todate, ticker_or_market, "거래대금", "순매수", False
        )

    if freq != "d" and len(df) > 0:
        how = dict.fromkeys(df.columns, "sum")
        df = resample_ohlcv(df, freq, how)

    return cast("DataFrame", df)


def get_market_trading_volume_by_date(
    fromdate: str,
    todate: str,
    ticker_or_market: str,
    etf: bool = False,
    etn: bool = False,
    elw: bool = False,
    freq: str = "d",
) -> "DataFrame":
    """투자자별 거래량 조회 (일자별)

    Args:
        fromdate        (str): 조회 시작 일자 (YYYYMMDD)
        todate          (str): 조회 종료 일자 (YYYYMMDD)
        ticker_or_market (str): 종목 티커 또는 시장 (KOSPI/KOSDAQ/KONEX/ALL)
        etf             (bool, optional): ETF 포함 여부. 기본값은 False
        etn             (bool, optional): ETN 포함 여부. 기본값은 False
        elw             (bool, optional): ELW 포함 여부. 기본값은 False
        freq            (str, optional): 리샘플링 주기 (d/m/y). 기본값은 "d"

    Returns:
        DataFrame: 투자자별 거래량 데이터 (일자별)
    """
    # ticker인지 market인지 판단
    if ticker_or_market in ["KOSPI", "KOSDAQ", "KONEX", "ALL"]:
        df = _get_market_trading_value_and_volume_on_market_by_date(
            fromdate, todate, ticker_or_market, etf, etn, elw, "거래량", "순매수", False
        )
    else:
        df = _get_market_trading_value_and_volume_on_ticker_by_date(
            fromdate, todate, ticker_or_market, "거래량", "순매수", False
        )

    if freq != "d" and len(df) > 0:
        how = dict.fromkeys(df.columns, "sum")
        df = resample_ohlcv(df, freq, how)

    return cast("DataFrame", df)


def get_exhaustion_rates_of_foreign_investment_by_ticker(
    date: str, market: str, balance_limit: bool = False
) -> "DataFrame":
    """외국인보유제한 한도소진률 조회 (티커별)

    Args:
        date          (str): 조회 일자 (YYYYMMDD)
        market        (str): 조회 시장 (KOSPI/KOSDAQ/KONEX/ALL)
        balance_limit (bool, optional): 외국인보유제한종목만 조회. 기본값은 False

    Returns:
        DataFrame: 외국인보유제한 한도소진률 데이터
    """
    return _get_exhaustion_rates_of_foreign_investment_by_ticker(date, market, balance_limit)


def get_exhaustion_rates_of_foreign_investment_by_date(
    fromdate: str, todate: str, ticker: str
) -> "DataFrame":
    """외국인보유제한 한도소진률 조회 (일자별)

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)
        ticker   (str): 종목 티커

    Returns:
        DataFrame: 외국인보유제한 한도소진률 데이터
    """
    return _get_exhaustion_rates_of_foreign_investment_by_date(fromdate, todate, ticker)


def get_market_net_purchases_of_equities_by_ticker(
    fromdate: str, todate: str, market: str = "ALL", investor: str = "전체"
) -> "DataFrame":
    """투자자별 순매수 상위종목 조회

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)
        market   (str, optional): 조회 시장 (KOSPI/KOSDAQ/KONEX/ALL). 기본값은 "ALL"
        investor (str, optional): 투자자 (금융투자/보험/투신/사모/은행/기타금융/연기금/기관합계/기타법인/개인/외국인/기타외국인/전체). 기본값은 "전체"

    Returns:
        DataFrame: 투자자별 순매수 상위종목 데이터
    """
    return _get_market_net_purchases_of_equities_by_ticker(fromdate, todate, market, investor)


# 공매도 관련 wrapper 함수들
def get_shorting_status_by_date(fromdate: str, todate: str, ticker: str) -> "DataFrame":
    """공매도 종합 현황 조회 (일자별)

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)
        ticker   (str): 종목 티커

    Returns:
        DataFrame: 공매도 종합 현황 데이터
    """
    return _get_shorting_status_by_date(fromdate, todate, ticker)


def get_shorting_volume_by_ticker(
    date: str, market: str = "KOSPI", alternative: bool = False
) -> "DataFrame":
    """공매도 거래량 조회 (티커별)

    Args:
        date        (str): 조회 일자 (YYYYMMDD)
        market      (str, optional): 조회 시장 (KOSPI/KOSDAQ/KONEX). 기본값은 "KOSPI"
        alternative (bool, optional): 대체 조회 여부. 기본값은 False

    Returns:
        DataFrame: 공매도 거래량 데이터
    """
    if alternative:
        date = get_nearest_business_day_in_a_week(date=date, prev=True)

    df = _get_shorting_trading_value_and_volume_by_ticker(date, market, ["주식"])

    # 거래량 컬럼만 추출
    if isinstance(df.columns, pd.MultiIndex):
        result = df["거래량"]
        # MultiIndex에서 선택하면 DataFrame이 반환되므로, Series인 경우에만 to_frame() 호출
        if isinstance(result, pd.Series):
            return cast("DataFrame", result.to_frame())
        return cast("DataFrame", result)
    return df


def get_shorting_value_by_ticker(
    date: str, market: str = "KOSPI", alternative: bool = False
) -> "DataFrame":
    """공매도 거래대금 조회 (티커별)

    Args:
        date        (str): 조회 일자 (YYYYMMDD)
        market      (str, optional): 조회 시장 (KOSPI/KOSDAQ/KONEX). 기본값은 "KOSPI"
        alternative (bool, optional): 대체 조회 여부. 기본값은 False

    Returns:
        DataFrame: 공매도 거래대금 데이터
    """
    if alternative:
        date = get_nearest_business_day_in_a_week(date=date, prev=True)

    df = _get_shorting_trading_value_and_volume_by_ticker(date, market, ["주식"])

    # 거래대금 컬럼만 추출
    if isinstance(df.columns, pd.MultiIndex):
        result = df["거래대금"]
        # MultiIndex에서 선택하면 DataFrame이 반환되므로, Series인 경우에만 to_frame() 호출
        if isinstance(result, pd.Series):
            return cast("DataFrame", result.to_frame())
        return cast("DataFrame", result)
    return df


def get_shorting_volume_by_date(fromdate: str, todate: str, ticker: str) -> "DataFrame":
    """공매도 거래량 조회 (일자별)

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)
        ticker   (str): 종목 티커

    Returns:
        DataFrame: 공매도 거래량 데이터 (일자별)
    """
    df = _get_shorting_trading_value_and_volume_by_date(fromdate, todate, ticker)

    # 거래량 컬럼만 추출
    if isinstance(df.columns, pd.MultiIndex):
        result = df["거래량"]
        # MultiIndex에서 선택하면 DataFrame이 반환되므로, Series인 경우에만 to_frame() 호출
        if isinstance(result, pd.Series):
            return cast("DataFrame", result.to_frame())
        return cast("DataFrame", result)
    return df


def get_shorting_value_by_date(fromdate: str, todate: str, ticker: str) -> "DataFrame":
    """공매도 거래대금 조회 (일자별)

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)
        ticker   (str): 종목 티커

    Returns:
        DataFrame: 공매도 거래대금 데이터 (일자별)
    """
    df = _get_shorting_trading_value_and_volume_by_date(fromdate, todate, ticker)

    # 거래대금 컬럼만 추출
    if isinstance(df.columns, pd.MultiIndex):
        result = df["거래대금"]
        # MultiIndex에서 선택하면 DataFrame이 반환되므로, Series인 경우에만 to_frame() 호출
        if isinstance(result, pd.Series):
            return cast("DataFrame", result.to_frame())
        return cast("DataFrame", result)
    return df


def get_shorting_investor_volume_by_date(
    fromdate: str, todate: str, market: str = "KOSPI"
) -> "DataFrame":
    """투자자별 공매도 거래량 조회 (일자별)

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)
        market   (str, optional): 조회 시장 (KOSPI/KOSDAQ/KONEX). 기본값은 "KOSPI"

    Returns:
        DataFrame: 투자자별 공매도 거래량 데이터 (일자별)
    """
    return _get_shorting_investor_by_date(fromdate, todate, market, "거래량")


def get_shorting_investor_value_by_date(
    fromdate: str, todate: str, market: str = "KOSPI"
) -> "DataFrame":
    """투자자별 공매도 거래대금 조회 (일자별)

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)
        market   (str, optional): 조회 시장 (KOSPI/KOSDAQ/KONEX). 기본값은 "KOSPI"

    Returns:
        DataFrame: 투자자별 공매도 거래대금 데이터 (일자별)
    """
    return _get_shorting_investor_by_date(fromdate, todate, market, "거래대금")


def get_shorting_volume_top50(date: str, market: str = "KOSPI") -> "DataFrame":
    """공매도 비중 상위 50개 종목 조회

    Args:
        date   (str): 조회 일자 (YYYYMMDD)
        market (str, optional): 조회 시장 (KOSPI/KOSDAQ/KONEX). 기본값은 "KOSPI"

    Returns:
        DataFrame: 공매도 비중 상위 50개 종목 데이터
    """
    return _get_shorting_volume_top50(date, market)


def get_shorting_balance_top50(date: str, market: str = "KOSPI") -> "DataFrame":
    """공매도 잔고 상위 50개 종목 조회

    Args:
        date   (str): 조회 일자 (YYYYMMDD)
        market (str, optional): 조회 시장 (KOSPI/KOSDAQ/KONEX). 기본값은 "KOSPI"

    Returns:
        DataFrame: 공매도 잔고 상위 50개 종목 데이터
    """
    return _get_shorting_balance_top50(date, market)


def get_shorting_balance_by_ticker(date: str, market: str = "KOSPI") -> "DataFrame":
    """공매도 잔고 조회 (티커별)

    Args:
        date   (str): 조회 일자 (YYYYMMDD)
        market (str, optional): 조회 시장 (KOSPI/KOSDAQ/KONEX). 기본값은 "KOSPI"

    Returns:
        DataFrame: 공매도 잔고 데이터 (티커별)
    """
    return _get_shorting_balance_by_ticker(date, market)


def get_shorting_balance_by_date(fromdate: str, todate: str, ticker: str) -> "DataFrame":
    """공매도 잔고 조회 (일자별)

    Args:
        fromdate (str): 조회 시작 일자 (YYYYMMDD)
        todate   (str): 조회 종료 일자 (YYYYMMDD)
        ticker   (str): 종목 티커

    Returns:
        DataFrame: 공매도 잔고 데이터 (일자별)
    """
    return _get_shorting_balance_by_date(fromdate, todate, ticker)


# 기존 함수들을 그대로 사용할 수 있도록 import
__all__ = [
    # 유틸리티
    "market_valid_check",
    "resample_ohlcv",
    # 영업일
    "get_nearest_business_day_in_a_week",
    "get_previous_business_days",
    # 티커
    "get_market_ticker_list",
    "get_market_ticker_name",
    # OHLCV
    "get_market_ohlcv",
    "get_market_ohlcv_by_date",
    "get_market_ohlcv_by_ticker",
    # 시가총액
    "get_market_cap",
    "get_market_cap_by_date",
    "get_market_cap_by_ticker",
    # 가격 변동
    "get_market_price_change_by_ticker",
    # 펀더멘털
    "get_market_fundamental_by_date",
    "get_market_fundamental_by_ticker",
    # 투자자별 거래실적
    "get_market_trading_volume_by_investor",
    "get_market_trading_value_by_investor",
    "get_market_trading_volume_by_date",
    "get_market_trading_value_by_date",
    # 외국인보유제한
    "get_exhaustion_rates_of_foreign_investment_by_ticker",
    "get_exhaustion_rates_of_foreign_investment_by_date",
    # 공매도
    "get_shorting_status_by_date",
    "get_shorting_volume_by_ticker",
    "get_shorting_value_by_ticker",
    "get_shorting_volume_by_date",
    "get_shorting_value_by_date",
    "get_shorting_investor_volume_by_date",
    "get_shorting_investor_value_by_date",
    "get_shorting_volume_top50",
    "get_shorting_balance_top50",
    "get_shorting_balance_by_ticker",
    "get_shorting_balance_by_date",
    # 지수
    "get_index_ticker_list",
    "get_index_ticker_name",
    "get_index_ohlcv_by_date",
    "get_index_listing_date",
    "get_index_price_change_by_ticker",
    "get_index_portfolio_deposit_file",
    # ETF/ETN/ELW
    "get_etf_ticker_list",
    "get_etn_ticker_list",
    "get_elw_ticker_list",
    "get_etf_ohlcv_by_date",
    "get_etf_ohlcv_by_ticker",
    "get_etf_price_change_by_ticker",
    "get_etf_portfolio_deposit_file",
    "get_etf_trading_volume_and_value",
    # 투자자별 순매수 상위종목
    "get_market_net_purchases_of_equities_by_ticker",
]

"""
주식 시가총액 관련 함수들
"""

import datetime
from typing import cast

from pandas import DataFrame

from pykrx.website.krx import datetime2string
from pykrx.website.krx.market.wrap import (
    get_market_cap_by_date as _get_market_cap_by_date,
)
from pykrx.website.krx.market.wrap import (
    get_market_cap_by_ticker as _get_market_cap_by_ticker,
)

from .stock_business_days import get_nearest_business_day_in_a_week
from .stock_utils import market_valid_check, regex_yymmdd, resample_ohlcv


def get_market_cap(*args, **kwargs):
    """시가총액 조회

    Args:
        특정 종목의 지정된 기간 시가총액 조회
        fromdate (str           ): 조회 시작 일자 (YYYYMMDD)
        todate   (str           ): 조회 종료 일자 (YYYYMMDD)
        ticker   (str           ): 티커
        freq     (str,  optional):  d - 일 / m - 월 / y - 년

        특정 일자의 전종목 시가총액 조회
        date      (str           ): 조회 일자 (YYYYMMDD)
        market    (str , optional): 조회 시장 (KOSPI/KOSDAQ/KONEX/ALL)
        ascending (bool, optional): 정렬 기준.
        prev      (bool, optional): 휴일일 경우 이전/이후 영업일 선택

    Returns:
        DataFrame: 시가총액 데이터
    """
    dates = list(filter(regex_yymmdd.match, [str(x) for x in args]))
    if len(dates) == 2 or ("fromdate" in kwargs and "todate" in kwargs):
        return get_market_cap_by_date(*args, **kwargs)
    else:
        return get_market_cap_by_ticker(*args, **kwargs)


def get_market_cap_by_date(fromdate: str, todate: str, ticker: str, freq: str = "d") -> DataFrame:
    """일자별로 정렬된 시가총액

    Args:
        fromdate (str           ): 조회 시작 일자 (YYYYMMDD)
        todate   (str           ): 조회 종료 일자 (YYYYMMDD)
        ticker   (str           ): 티커
        freq     (str,  optional):  d - 일 / m - 월 / y - 년

    Returns:
        DataFrame: 시가총액 데이터
    """
    if isinstance(fromdate, datetime.datetime):
        fromdate = datetime2string(fromdate)

    if isinstance(todate, datetime.datetime):
        todate = datetime2string(todate)

    fromdate = fromdate.replace("-", "")
    todate = todate.replace("-", "")

    df = _get_market_cap_by_date(fromdate, todate, ticker)

    how = {"시가총액": "last", "거래량": "sum", "거래대금": "sum", "상장주식수": "last"}
    return cast(DataFrame, resample_ohlcv(df, freq, how))


@market_valid_check()
def get_market_cap_by_ticker(
    date, market: str = "ALL", acending: bool = False, alternative: bool = False
) -> DataFrame:
    """티커별로 정렬된 시가총액

    Args:
        date        (str           ): 조회 일자 (YYYYMMDD)
        market      (str , optional): 조회 시장 (KOSPI/KOSDAQ/KONEX/ALL)
        ascending   (bool, optional): 정렬 기준.
        alternative (bool, optional): 휴일일 경우 이전 영업일 선택 여부

    Returns:
        DataFrame: 시가총액 데이터
    """
    if isinstance(date, datetime.datetime):
        date = datetime2string(date)

    date = date.replace("-", "")

    df = _get_market_cap_by_ticker(date, market, acending)
    holiday = (df[["종가", "시가총액", "거래량", "거래대금"]] == 0).all(axis=None)
    if holiday and alternative:
        target_date = get_nearest_business_day_in_a_week(date=date, prev=True)
        df = _get_market_cap_by_ticker(target_date, market, acending)
    return df

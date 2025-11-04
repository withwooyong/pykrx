"""
주식 OHLCV 관련 함수들
"""

import datetime
from typing import cast

from pandas import DataFrame

from pykrx.website.krx import datetime2string
from pykrx.website.krx.market.wrap import (
    get_market_ohlcv_by_date as _get_market_ohlcv_by_date,
)
from pykrx.website.krx.market.wrap import (
    get_market_ohlcv_by_ticker as _get_market_ohlcv_by_ticker,
)
from pykrx.website.naver.wrap import get_market_ohlcv_by_date as _get_naver_market_ohlcv_by_date

from .stock_business_days import get_nearest_business_day_in_a_week
from .stock_ticker import get_market_ticker_name
from .stock_utils import market_valid_check, regex_yymmdd, resample_ohlcv


def get_market_ohlcv(*args, **kwargs):
    """OHLCV 조회

    Args:
        특정 종목의 지정된 기간 OHLCV 조회
        fromdate     (str           ): 조회 시작 일자 (YYYYMMDD)
        todate       (str           ): 조회 종료 일자 (YYYYMMDD)
        ticker       (str,  optional): 조회할 종목의 티커
        freq         (str,  optional): d - 일 / m - 월 / y - 년
        adjusted     (bool, optional): 수정 종가 여부 (True/False)

        특정 일자의 전종목 OHLCV 조회
        date   (str): 조회 일자 (YYYYMMDD)
        market (str): 조회 시장 (KOSPI/KOSDAQ/KONEX/ALL)

    Returns:
        DataFrame: OHLCV 데이터
    """
    dates = list(filter(regex_yymmdd.match, [str(x) for x in args]))
    if len(dates) == 2 or ("fromdate" in kwargs and "todate" in kwargs):
        return get_market_ohlcv_by_date(*args, **kwargs)
    else:
        return get_market_ohlcv_by_ticker(*args, **kwargs)


def get_market_ohlcv_by_date(
    fromdate: str,
    todate: str,
    ticker: str,
    freq: str = "d",
    adjusted: bool = True,
    name_display: bool = False,
) -> DataFrame:
    """특정 종목의 일자별로 정렬된 OHLCV

    Args:
        fromdate     (str           ): 조회 시작 일자 (YYYYMMDD)
        todate       (str           ): 조회 종료 일자 (YYYYMMDD)
        ticker       (str           ): 조회할 종목의 티커
        freq         (str,  optional): d - 일 / m - 월 / y - 년
        adjusted     (bool, optional): 수정 종가 여부 (True/False)
        name_display (bool, optional): columns의 이름 출력 여부 (True/False)

    Returns:
        DataFrame: OHLCV 데이터
    """
    if isinstance(fromdate, datetime.datetime):
        fromdate = datetime2string(fromdate)

    if isinstance(todate, datetime.datetime):
        todate = datetime2string(todate)

    fromdate = fromdate.replace("-", "")
    todate = todate.replace("-", "")

    if adjusted:
        df = _get_naver_market_ohlcv_by_date(fromdate, todate, ticker)
    else:
        df = _get_market_ohlcv_by_date(fromdate, todate, ticker, False)

    if name_display:
        df.columns.name = get_market_ticker_name(ticker)

    how = {"시가": "first", "고가": "max", "저가": "min", "종가": "last", "거래량": "sum"}

    return cast(DataFrame, resample_ohlcv(df, freq, how))


@market_valid_check()
def get_market_ohlcv_by_ticker(date, market: str = "KOSPI", alternative: bool = False) -> DataFrame:
    """티커별로 정리된 전종목 OHLCV

    Args:
        date        (str           ): 조회 일자 (YYYYMMDD)
        market      (str           ): 조회 시장 (KOSPI/KOSDAQ/KONEX/ALL)
        alternative (bool, optional): 휴일일 경우 이전 영업일 선택 여부

    Returns:
        DataFrame: OHLCV 데이터
    """
    if isinstance(date, datetime.datetime):
        date = datetime2string(date)

    date = date.replace("-", "")

    df = _get_market_ohlcv_by_ticker(date, market)
    holiday = (df[["시가", "고가", "저가", "종가"]] == 0).all(axis=None)
    if holiday and alternative:
        target_date = get_nearest_business_day_in_a_week(date=date, prev=True)
        df = _get_market_ohlcv_by_ticker(target_date, market)
    return df

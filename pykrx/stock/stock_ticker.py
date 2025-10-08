"""
주식 티커 관련 함수들
"""
from pykrx.website import krx
from .stock_business_days import get_nearest_business_day_in_a_week


def get_market_ticker_list(date: str = None, market: str = "KOSPI") -> list:
    """티커 목록 조회

    Args:
        date   (str, optional): 조회 일자 (YYYYMMDD)
        market (str, optional): 조회 시장 (KOSPI/KOSDAQ/KONEX/ALL)

    Returns:
        list: 티커가 담긴 리스트
    """
    if date is None:
        date = get_nearest_business_day_in_a_week()

    s = krx.get_market_ticker_and_name(date, market)
    return s.index.to_list()


def get_market_ticker_name(ticker: str) -> str:
    """티커에 대응되는 종목 이름 반환

    Args:
        ticker (str): 티커

    Returns:
        str: 종목명
    """
    return krx.get_stock_name(ticker)

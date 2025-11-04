import datetime
import re

from pandas import DataFrame

from pykrx.website.krx import datetime2string, get_nearest_business_day_in_a_week
from pykrx.website.krx.future.wrap import (
    get_future_ohlcv_by_ticker as _get_future_ohlcv_by_ticker,
)
from pykrx.website.krx.future.wrap import (
    get_future_ticker_and_name as _get_future_ticker_and_name,
)
from pykrx.website.krx.future.wrap import (
    get_future_ticker_list as _get_future_ticker_list,
)

yymmdd = re.compile(r"\d{4}[-/]?\d{2}[-/]?\d{2}")


def get_future_ticker_list() -> list:
    """티커 목록 조회

    Args: None

    Returns:
        list: 티커가 담긴 리스트

        > get_future_ticker_list()

        ['KRDRVFUK2I', 'KRDRVFUMKI', 'KRDRVOPK2I', 'KRDRVOPWKI', 'KRDRVOPMKI', 'KRDRVFUKQI', 'KRDRVOPKQI', 'KRDRVFUXI3', 'KRDRVFUVKI', 'KRDRVFUXAT', 'KRDRVFUBM3', 'KRDRVFUBM5', 'KRDRVFUBMA', 'KRDRVFURFR', 'KRDRVFUUSD', 'KRDRVFXUSD', 'KRDRVFUJPY', 'KRDRVFUEUR', 'KRDRVFUCNH', 'KRDRVFUKGD', 'KRDRVFUEQU', 'KRDRVOPEQU', 'KRDRVFUEST']
    """  # pylint: disable=line-too-long # noqa: E501

    return _get_future_ticker_list()  # type: ignore[return-value]


def get_future_ticker_name(ticker: str) -> str:
    """티커에 대응되는 종목 이름 반환

    Args:
        ticker (str): 티커

    Returns:
        str: 종목명

        > get_future_ticker_name('KRDRVFUEST')

        EURO STOXX50 Futures
    """
    df = _get_future_ticker_and_name()
    # ticker로 필터링하여 해당 종목명 반환
    if ticker in df.index:
        return str(df.loc[ticker, "종목명"])  # type: ignore[index]
    return ""


def get_future_ohlcv(*args, **kwargs):
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

    Returns:
        DataFrame:

            특정 종목의 지정된 기간 OHLCV 조회
            >> get_future_ohlcv("20210118", "20210126", "xxx")
                미구현

            특정 일자의 전종목 OHLCV 조회
            >> get_market_ohlcv("20210122")

                      시가    고가    저가    종가   거래량     거래대금     등락률
            티커
            095570    4190    4245    4160    4210   216835    910274405   0.839844
            006840   25750   29550   25600   29100   727088  20462325950  12.570312
            027410    5020    5250    4955    5220  1547629   7990770515   4.191406
            282330  156500  156500  151500  152000    62510   9555364000  -2.560547

    """  # pylint: disable=line-too-long # noqa: E501

    dates = list(filter(yymmdd.match, [str(x) for x in args]))
    if len(dates) == 2 or ("fromdate" in kwargs and "todate" in kwargs):
        raise NotImplementedError
        # return get_future_ohlcv_by_date(*args, **kwargs)
    else:
        return get_future_ohlcv_by_ticker(*args, **kwargs)


def get_future_ohlcv_by_ticker(
    date: str, prod: str, alternative: bool = False, prev: bool = True
) -> DataFrame:
    if isinstance(date, datetime.datetime):
        date = datetime2string(date)

    date = date.replace("-", "")

    df = _get_future_ohlcv_by_ticker(date, prod)
    if df.empty and alternative:
        target_date = get_nearest_business_day_in_a_week(date=date, prev=prev)
        df = _get_future_ohlcv_by_ticker(target_date, prod)
    return df


if __name__ == "__main__":
    # tickers = get_future_ticker_list()
    # print(tickers)

    # names = get_future_ticker_name('KRDRVFUEST')
    # print(names)

    df = get_future_ohlcv("20220902", "KRDRVFUEST")
    print(df)

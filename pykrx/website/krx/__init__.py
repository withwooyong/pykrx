import datetime
from typing import cast

from pandas import DatetimeIndex

from .market.wrap import get_index_ohlcv_by_date


def datetime2string(dt, freq="d"):
    if freq.upper() == "Y":
        return dt.strftime("%Y")
    elif freq.upper() == "M":
        return dt.strftime("%Y%m")
    else:
        return dt.strftime("%Y%m%d")


def get_nearest_business_day_in_a_week(date: str | None = None, prev: bool = True) -> str:
    """인접한 영업일을 조회한다.

    Args:
        date (str , optional): 조회할 날짜로 입력하지 않으면 현재 시간으로 대체
        prev (bool, optional): 이전 영업일을 조회할지 이후 영업일을 조회할지
                               조정하는 flag

    Returns:
        str: 날짜 (YYMMDD)
    """
    curr = datetime.datetime.now() if date is None else datetime.datetime.strptime(date, "%Y%m%d")

    if prev:
        prev_dt = curr - datetime.timedelta(days=7)
        curr_str = curr.strftime("%Y%m%d")
        prev_str = prev_dt.strftime("%Y%m%d")
        df = get_index_ohlcv_by_date(prev_str, curr_str, "1001")
        index = cast(DatetimeIndex, df.index)
        return index[-1].strftime("%Y%m%d")  # type: ignore[attr-defined]
    else:
        next_dt = curr + datetime.timedelta(days=7)
        next_str = next_dt.strftime("%Y%m%d")
        curr_str = curr.strftime("%Y%m%d")
        df = get_index_ohlcv_by_date(curr_str, next_str, "1001")
        index = cast(DatetimeIndex, df.index)
        return index[0].strftime("%Y%m%d")  # type: ignore[attr-defined]

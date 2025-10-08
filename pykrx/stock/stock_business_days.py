"""
주식 영업일 관련 함수들
"""
from pykrx.website import krx
from deprecated import deprecated


def get_nearest_business_day_in_a_week(date: str = None, prev: bool = True) -> str:
    """인접한 영업일을 조회한다.

    Args:
        date (str , optional): 조회할 날짜, 입력하지 않으면 현재 시간으로 대체
        prev (bool, optional): 휴일일 경우 이전/이후 영업일 선택

    Returns:
        str: 날짜 (YYMMDD)
    """
    return krx.get_nearest_business_day_in_a_week(date, prev)


def __get_business_days_0(year: int, month: int):
    """연도와 월로 영업일 조회 (내부 함수)"""
    strt = f"{year}{month:02}01"
    if month == 12:
        last = f"{year+1}0101"
    else:
        last = f"{year}{month+1:02}01"
    df = krx.get_market_ohlcv_by_date(strt, last, "000020")
    cond = df.index.month[0] == df.index.month
    return df.index[cond].to_list()


def __get_business_days_1(strt: str, last: str):
    """시작일과 종료일로 영업일 조회 (내부 함수)"""
    df = krx.get_market_ohlcv_by_date(strt, last, "000020")
    return df.index.to_list()


def get_previous_business_days(**kwargs) -> list:
    """과거의 영업일 조회

    Returns:
        list: 영업일을 pandas의 Timestamp로 저장해서 리스트로 반환

        >> get_previous_business_days(year=2020, month=10)
         -> 10월의 영업일을 조회

        >> get_previous_business_days(fromdate="20200101", todate="20200115")
         -> 주어진 기간 동안의 영업일을 조회
    """
    if "year" in kwargs and "month" in kwargs:
        return __get_business_days_0(kwargs['year'], kwargs['month'])

    elif 'fromdate' in kwargs and "todate" in kwargs:
        return __get_business_days_1(kwargs['fromdate'], kwargs['todate'])
    else:
        print("This option is not supported.")
        return []


@deprecated(version='1.1',
            reason="You should use get_previous_business_days() instead")
def get_business_days(year, month) -> list:
    """Deprecated: get_previous_business_days() 사용을 권장"""
    return get_previous_business_days(year=year, month=month)

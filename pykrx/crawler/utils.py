"""
크롤러 유틸리티 함수들
"""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any

import pandas as pd


def retry_with_backoff(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """재시도 데코레이터 (exponential backoff)"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise e
                    print(f"  ⚠️  {func.__name__} 실패 (재시도 {retries}/{max_retries}): {str(e)}")
                    time.sleep(current_delay)
                    current_delay *= backoff
            return None

        return wrapper

    return decorator


def date_to_string(date: str | pd.Timestamp) -> str:
    """날짜를 YYYYMMDD 형식 문자열로 변환"""

    if isinstance(date, pd.Timestamp):
        return date.strftime("%Y%m%d")
    if isinstance(date, str):
        # 이미 YYYYMMDD 형식인지 확인
        if len(date) == 8 and date.isdigit():
            return date
        # YYYY-MM-DD 형식인 경우
        if "-" in date:
            return date.replace("-", "")
    raise ValueError(f"날짜 형식이 올바르지 않습니다: {date}")


def string_to_date(date_str: str) -> pd.Timestamp:
    """YYYYMMDD 형식 문자열을 pd.Timestamp로 변환"""

    if len(date_str) == 8 and date_str.isdigit():
        try:
            result = pd.Timestamp(f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}")
            # NaT 체크 (pd.isna는 스칼라에 대해서만 사용)
            if result is pd.NaT:
                raise ValueError(f"날짜 형식이 올바르지 않습니다: {date_str}")
            # 타입 체크를 통해 NaTType 제거
            if not isinstance(result, pd.Timestamp):
                raise ValueError(f"날짜 형식이 올바르지 않습니다: {date_str}")
            return result
        except (ValueError, TypeError) as e:
            raise ValueError(f"날짜 형식이 올바르지 않습니다: {date_str}") from e
    raise ValueError(f"날짜 형식이 올바르지 않습니다: {date_str}")


def format_number(num: int | float) -> str:
    """숫자를 읽기 쉬운 형식으로 포맷팅"""

    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    if num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    if num >= 1_000:
        return f"{num / 1_000:.2f}K"
    return str(num)


def get_year_month_from_date(date: pd.Timestamp | str) -> tuple[int, int]:
    """날짜에서 연도와 월 추출"""

    if isinstance(date, str):
        date = string_to_date(date)
    return date.year, date.month


def split_date_range_by_year(fromdate: str, todate: str) -> list[tuple[str, str]]:
    """날짜 범위를 연도별로 분할

    Args:
        fromdate: 시작일 (YYYYMMDD)
        todate: 종료일 (YYYYMMDD)

    Returns:
        연도별 (시작일, 종료일) 튜플 리스트

    Example:
        split_date_range_by_year("20200101", "20241231")
        -> [("20200101", "20201231"), ("20210101", "20211231"), ...]
    """

    start = string_to_date(fromdate)
    end = string_to_date(todate)

    ranges = []
    current_year = start.year

    while current_year <= end.year:
        # 연도 시작일
        year_start = max(start, pd.Timestamp(f"{current_year}-01-01"))
        # 연도 종료일
        if current_year == end.year:
            year_end = end
        else:
            year_end = pd.Timestamp(f"{current_year}-12-31")

        # 날짜가 유효한 범위인 경우만 추가
        if year_start <= year_end:
            ranges.append((date_to_string(year_start), date_to_string(year_end)))

        current_year += 1

    return ranges

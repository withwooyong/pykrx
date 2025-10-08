"""
주식 API 유틸리티 함수들
"""
import re
import inspect
import functools
import pandas as pd
from pandas import DataFrame


regex_yymmdd = re.compile(r"\d{4}[-/]?\d{2}[-/]?\d{2}")


def market_valid_check(param=None):
    """시장 유효성 검사 데코레이터"""
    def _market_valid_check(func):
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # default parameter
            if 'market' in sig.bind_partial(*args, **kwargs).arguments:
                if param is None:
                    valid_market_list = ["ALL", "KOSPI", "KOSDAQ", "KONEX"]
                else:
                    valid_market_list = param

                for v in [x for x in kwargs.values()] + list(args):
                    if v in valid_market_list:
                        return func(*args, **kwargs)
                print("market 옵션이 올바르지 않습니다.")
                return DataFrame()
            return func(*args, **kwargs)
        return wrapper
    return _market_valid_check


def resample_ohlcv(df, freq, how):
    """
    KRX OLCV format의 DataFrame을 리샘플링
    
    Args:
        df   : KRX OLCV format의 DataFrame
        freq : d - 일 / m - 월 / y - 년
        how  : 리샘플링 방법
        
    Returns:
        resampling된 DataFrame
    """
    if freq != 'd' and len(df) > 0:
        if freq == 'm':
            df = df.resample('M').apply(how)
        elif freq == 'y':
            df = df.resample('Y').apply(how)
        else:
            print("choose a freq parameter in ('m', 'y', 'd')")
            raise RuntimeError
    return df

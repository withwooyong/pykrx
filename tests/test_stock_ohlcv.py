"""
주식 OHLCV 관련 함수 테스트
"""
import unittest
import pandas as pd
import datetime
from unittest.mock import patch, MagicMock
from pykrx.stock.stock_ohlcv import (
    get_market_ohlcv,
    get_market_ohlcv_by_date,
    get_market_ohlcv_by_ticker
)


class TestStockOHLCV(unittest.TestCase):
    """주식 OHLCV 관련 함수 테스트 클래스"""

    def test_get_market_ohlcv_by_date_with_string_dates(self):
        """문자열 날짜로 OHLCV 조회 테스트"""
        with patch('pykrx.website.naver.get_market_ohlcv_by_date') as mock_naver:
            # Mock 데이터 생성
            mock_df = pd.DataFrame({
                '시가': [100, 101, 102],
                '고가': [105, 106, 107],
                '저가': [95, 96, 97],
                '종가': [101, 102, 103],
                '거래량': [1000, 1100, 1200]
            }, index=pd.date_range('2024-01-15', periods=3))
            mock_naver.return_value = mock_df
            
            result = get_market_ohlcv_by_date("20240115", "20240117", "005930")
            
            # 결과 검증
            self.assertEqual(len(result), 3)
            self.assertIn('시가', result.columns)
            self.assertIn('고가', result.columns)
            self.assertIn('저가', result.columns)
            self.assertIn('종가', result.columns)
            self.assertIn('거래량', result.columns)
            
            # naver 함수 호출 검증
            mock_naver.assert_called_once_with("20240115", "20240117", "005930")

    def test_get_market_ohlcv_by_date_with_datetime_dates(self):
        """datetime 객체로 OHLCV 조회 테스트"""
        with patch('pykrx.website.krx.datetime2string') as mock_datetime2string:
            with patch('pykrx.website.krx.get_market_ohlcv_by_date') as mock_krx:
                mock_datetime2string.return_value = "20240115"
                
                mock_df = pd.DataFrame({
                    '시가': [100, 101],
                    '고가': [105, 106],
                    '저가': [95, 96],
                    '종가': [101, 102],
                    '거래량': [1000, 1100]
                }, index=pd.date_range('2024-01-15', periods=2))
                mock_krx.return_value = mock_df
                
                start_date = datetime.datetime(2024, 1, 15)
                end_date = datetime.datetime(2024, 1, 16)
                
                result = get_market_ohlcv_by_date(start_date, end_date, "005930", adjusted=False)
                
                # krx 함수 호출 검증 (adjusted=False인 경우)
                mock_krx.assert_called_once_with("20240115", "20240116", "005930", False)

    def test_get_market_ohlcv_by_date_with_dash_dates(self):
        """하이픈이 포함된 날짜로 OHLCV 조회 테스트"""
        with patch('pykrx.website.naver.get_market_ohlcv_by_date') as mock_naver:
            mock_df = pd.DataFrame({
                '시가': [100],
                '고가': [105],
                '저가': [95],
                '종가': [101],
                '거래량': [1000]
            }, index=pd.date_range('2024-01-15', periods=1))
            mock_naver.return_value = mock_df
            
            result = get_market_ohlcv_by_date("2024-01-15", "2024-01-15", "005930")
            
            # 하이픈이 제거되어야 함
            mock_naver.assert_called_once_with("20240115", "20240115", "005930")

    def test_get_market_ohlcv_by_date_with_name_display(self):
        """name_display 옵션 테스트"""
        with patch('pykrx.website.naver.get_market_ohlcv_by_date') as mock_naver:
            with patch('pykrx.stock.stock_ticker.get_market_ticker_name') as mock_ticker_name:
                mock_df = pd.DataFrame({
                    '시가': [100],
                    '고가': [105],
                    '저가': [95],
                    '종가': [101],
                    '거래량': [1000]
                }, index=pd.date_range('2024-01-15', periods=1))
                mock_naver.return_value = mock_df
                mock_ticker_name.return_value = "삼성전자"
                
                result = get_market_ohlcv_by_date("20240115", "20240115", "005930", name_display=True)
                
                # columns.name이 설정되어야 함
                self.assertEqual(result.columns.name, "삼성전자")

    def test_get_market_ohlcv_by_ticker(self):
        """티커별 OHLCV 조회 테스트"""
        with patch('pykrx.website.krx.get_market_ohlcv_by_ticker') as mock_krx:
            mock_df = pd.DataFrame({
                '시가': [100, 101, 102],
                '고가': [105, 106, 107],
                '저가': [95, 96, 97],
                '종가': [101, 102, 103],
                '거래량': [1000, 1100, 1200]
            }, index=['005930', '000660', '373220'])
            mock_krx.return_value = mock_df
            
            result = get_market_ohlcv_by_ticker("20240115", "KOSPI")
            
            # 결과 검증
            self.assertEqual(len(result), 3)
            mock_krx.assert_called_once_with("20240115", "KOSPI")

    def test_get_market_ohlcv_by_ticker_with_datetime(self):
        """datetime 객체로 티커별 OHLCV 조회 테스트"""
        with patch('pykrx.website.krx.datetime2string') as mock_datetime2string:
            with patch('pykrx.website.krx.get_market_ohlcv_by_ticker') as mock_krx:
                mock_datetime2string.return_value = "20240115"
                mock_df = pd.DataFrame({
                    '시가': [100],
                    '고가': [105],
                    '저가': [95],
                    '종가': [101],
                    '거래량': [1000]
                }, index=['005930'])
                mock_krx.return_value = mock_df
                
                test_date = datetime.datetime(2024, 1, 15)
                result = get_market_ohlcv_by_ticker(test_date, "KOSPI")
                
                mock_krx.assert_called_once_with("20240115", "KOSPI")

    def test_get_market_ohlcv_by_ticker_holiday_alternative(self):
        """휴일 대안 데이터 조회 테스트"""
        with patch('pykrx.website.krx.get_market_ohlcv_by_ticker') as mock_krx:
            with patch('pykrx.stock.stock_business_days.get_nearest_business_day_in_a_week') as mock_business_day:
                # 첫 번째 호출은 휴일 데이터 (모든 값이 0)
                holiday_df = pd.DataFrame({
                    '시가': [0, 0],
                    '고가': [0, 0],
                    '저가': [0, 0],
                    '종가': [0, 0],
                    '거래량': [0, 0]
                }, index=['005930', '000660'])
                
                # 두 번째 호출은 정상 데이터
                normal_df = pd.DataFrame({
                    '시가': [100, 101],
                    '고가': [105, 106],
                    '저가': [95, 96],
                    '종가': [101, 102],
                    '거래량': [1000, 1100]
                }, index=['005930', '000660'])
                
                mock_krx.side_effect = [holiday_df, normal_df]
                mock_business_day.return_value = "20240114"
                
                result = get_market_ohlcv_by_ticker("20240115", "KOSPI", alternative=True)
                
                # alternative=True이므로 이전 영업일 데이터가 반환되어야 함
                self.assertEqual(len(result), 2)
                mock_business_day.assert_called_once_with(date="20240115", prev=True)

    def test_get_market_ohlcv_function_dispatch(self):
        """get_market_ohlcv 함수의 dispatch 로직 테스트"""
        with patch('pykrx.stock.stock_ohlcv.get_market_ohlcv_by_date') as mock_by_date:
            with patch('pykrx.stock.stock_ohlcv.get_market_ohlcv_by_ticker') as mock_by_ticker:
                mock_by_date.return_value = pd.DataFrame()
                mock_by_ticker.return_value = pd.DataFrame()
                
                # 2개 날짜 인자로 호출하면 by_date 함수가 호출되어야 함
                get_market_ohlcv("20240115", "20240116", "005930")
                mock_by_date.assert_called_once()
                mock_by_ticker.assert_not_called()
                
                # 1개 날짜 인자로 호출하면 by_ticker 함수가 호출되어야 함
                get_market_ohlcv("20240115")
                mock_by_ticker.assert_called_once()

    def test_get_market_ohlcv_with_kwargs(self):
        """키워드 인자로 OHLCV 조회 테스트"""
        with patch('pykrx.stock.stock_ohlcv.get_market_ohlcv_by_date') as mock_by_date:
            mock_by_date.return_value = pd.DataFrame()
            
            get_market_ohlcv(fromdate="20240115", todate="20240116", ticker="005930")
            
            mock_by_date.assert_called_once_with(fromdate="20240115", todate="20240116", ticker="005930")


if __name__ == '__main__':
    unittest.main()

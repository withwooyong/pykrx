"""
주식 티커 관련 함수 테스트
"""
import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from pykrx.stock.stock_ticker import (
    get_market_ticker_list,
    get_market_ticker_name
)


class TestStockTicker(unittest.TestCase):
    """주식 티커 관련 함수 테스트 클래스"""

    def test_get_market_ticker_list_default_params(self):
        """기본 파라미터로 티커 목록 조회 테스트"""
        with patch('pykrx.stock.stock_business_days.get_nearest_business_day_in_a_week') as mock_business_day:
            with patch('pykrx.website.krx.get_market_ticker_and_name') as mock_krx:
                # Mock 데이터 설정
                mock_business_day.return_value = "20240115"
                
                mock_df = pd.DataFrame({
                    '종목명': ['삼성전자', 'SK하이닉스', 'LG에너지솔루션']
                }, index=['005930', '000660', '373220'])
                mock_krx.return_value = mock_df
                
                result = get_market_ticker_list()
                
                # 결과 검증
                self.assertEqual(len(result), 3)
                self.assertIn('005930', result)
                self.assertIn('000660', result)
                self.assertIn('373220', result)
                
                # 함수 호출 검증
                mock_business_day.assert_called_once()
                mock_krx.assert_called_once_with("20240115", "KOSPI")

    def test_get_market_ticker_list_with_date(self):
        """날짜를 지정하여 티커 목록 조회 테스트"""
        with patch('pykrx.website.krx.get_market_ticker_and_name') as mock_krx:
            mock_df = pd.DataFrame({
                '종목명': ['삼성전자', 'SK하이닉스']
            }, index=['005930', '000660'])
            mock_krx.return_value = mock_df
            
            result = get_market_ticker_list("20240115")
            
            self.assertEqual(len(result), 2)
            mock_krx.assert_called_once_with("20240115", "KOSPI")

    def test_get_market_ticker_list_with_market(self):
        """시장을 지정하여 티커 목록 조회 테스트"""
        with patch('pykrx.stock.stock_business_days.get_nearest_business_day_in_a_week') as mock_business_day:
            with patch('pykrx.website.krx.get_market_ticker_and_name') as mock_krx:
                mock_business_day.return_value = "20240115"
                mock_df = pd.DataFrame({
                    '종목명': ['테스트종목1', '테스트종목2']
                }, index=['123456', '789012'])
                mock_krx.return_value = mock_df
                
                result = get_market_ticker_list(market="KOSDAQ")
                
                self.assertEqual(len(result), 2)
                mock_krx.assert_called_once_with("20240115", "KOSDAQ")

    def test_get_market_ticker_list_all_markets(self):
        """전체 시장 티커 목록 조회 테스트"""
        with patch('pykrx.stock.stock_business_days.get_nearest_business_day_in_a_week') as mock_business_day:
            with patch('pykrx.website.krx.get_market_ticker_and_name') as mock_krx:
                mock_business_day.return_value = "20240115"
                mock_df = pd.DataFrame({
                    '종목명': ['전체시장종목1', '전체시장종목2', '전체시장종목3']
                }, index=['111111', '222222', '333333'])
                mock_krx.return_value = mock_df
                
                result = get_market_ticker_list(market="ALL")
                
                self.assertEqual(len(result), 3)
                mock_krx.assert_called_once_with("20240115", "ALL")

    def test_get_market_ticker_name(self):
        """티커로 종목명 조회 테스트"""
        with patch('pykrx.website.krx.get_stock_name') as mock_krx:
            mock_krx.return_value = "삼성전자"
            
            result = get_market_ticker_name("005930")
            
            self.assertEqual(result, "삼성전자")
            mock_krx.assert_called_once_with("005930")

    def test_get_market_ticker_name_multiple_calls(self):
        """여러 번의 티커명 조회 테스트"""
        with patch('pykrx.website.krx.get_stock_name') as mock_krx:
            mock_krx.side_effect = ["삼성전자", "SK하이닉스", "LG에너지솔루션"]
            
            result1 = get_market_ticker_name("005930")
            result2 = get_market_ticker_name("000660")
            result3 = get_market_ticker_name("373220")
            
            self.assertEqual(result1, "삼성전자")
            self.assertEqual(result2, "SK하이닉스")
            self.assertEqual(result3, "LG에너지솔루션")
            
            # 호출 횟수 확인
            self.assertEqual(mock_krx.call_count, 3)

    def test_get_market_ticker_list_empty_result(self):
        """빈 결과 반환 테스트"""
        with patch('pykrx.stock.stock_business_days.get_nearest_business_day_in_a_week') as mock_business_day:
            with patch('pykrx.website.krx.get_market_ticker_and_name') as mock_krx:
                mock_business_day.return_value = "20240115"
                mock_df = pd.DataFrame()
                mock_krx.return_value = mock_df
                
                result = get_market_ticker_list()
                
                self.assertEqual(len(result), 0)
                self.assertIsInstance(result, list)

    def test_get_market_ticker_list_datetime_input(self):
        """datetime 객체 입력 테스트"""
        with patch('pykrx.website.krx.get_market_ticker_and_name') as mock_krx:
            import datetime
            test_date = datetime.datetime(2024, 1, 15)
            
            mock_df = pd.DataFrame({
                '종목명': ['테스트종목']
            }, index=['123456'])
            mock_krx.return_value = mock_df
            
            result = get_market_ticker_list(test_date)
            
            self.assertEqual(len(result), 1)
            mock_krx.assert_called_once()


if __name__ == '__main__':
    unittest.main()

"""
주식 영업일 관련 함수 테스트
"""
import unittest
import pandas as pd
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import patch, MagicMock
from pykrx.stock.stock_business_days import (
    get_nearest_business_day_in_a_week,
    get_previous_business_days,
    get_business_days
)


class TestStockBusinessDays(unittest.TestCase):
    """주식 영업일 관련 함수 테스트 클래스"""

    def setUp(self):
        """테스트 시작 전 실행"""
        print(f"\n🚀 {self._testMethodName} 테스트 시작")

    def tearDown(self):
        """테스트 종료 후 실행"""
        print(f"✅ {self._testMethodName} 테스트 완료\n")

    def test_get_nearest_business_day_in_a_week(self):
        """get_nearest_business_day_in_a_week 함수 테스트"""
        print("  📅 인접한 영업일 조회 테스트 실행 중...")
        
        with patch('pykrx.website.krx.get_nearest_business_day_in_a_week') as mock_krx:
            mock_krx.return_value = "20240115"
            
            result = get_nearest_business_day_in_a_week()
            print(f"    결과: {result}")
            self.assertEqual(result, "20240115")
            mock_krx.assert_called_once_with(None, True)
            
            result = get_nearest_business_day_in_a_week("20240120", False)
            print(f"    파라미터 변경 결과: {result}")
            self.assertEqual(result, "20240115")
            mock_krx.assert_called_with("20240120", False)
            
            print("  ✅ 인접한 영업일 조회 테스트 성공")

    def test_get_previous_business_days_by_year_month(self):
        """연도와 월로 영업일 조회 테스트"""
        print("  📅 연도/월로 영업일 조회 테스트 실행 중...")
        
        with patch('pykrx.website.krx.get_market_ohlcv_by_date') as mock_krx:
            # Mock 데이터 생성
            mock_dates = pd.date_range('2024-01-01', periods=31, freq='D')
            mock_df = pd.DataFrame(index=mock_dates)
            mock_krx.return_value = mock_df
            
            result = get_previous_business_days(year=2024, month=1)
            print(f"    2024년 1월 영업일 수: {len(result)}일")
            
            # 1월의 모든 날짜가 반환되어야 함
            self.assertEqual(len(result), 31)
            self.assertIsInstance(result[0], pd.Timestamp)
            
            # krx 함수가 올바른 파라미터로 호출되었는지 확인
            mock_krx.assert_called_once_with("20240101", "20240201", "000020")
            
            print("  ✅ 연도/월로 영업일 조회 테스트 성공")

    def test_get_previous_business_days_by_date_range(self):
        """날짜 범위로 영업일 조회 테스트"""
        print("  📅 날짜 범위로 영업일 조회 테스트 실행 중...")
        
        with patch('pykrx.website.krx.get_market_ohlcv_by_date') as mock_krx:
            # Mock 데이터 생성
            mock_dates = pd.date_range('2024-01-01', periods=15, freq='D')
            mock_df = pd.DataFrame(index=mock_dates)
            mock_krx.return_value = mock_df
            
            result = get_previous_business_days(fromdate="20240101", todate="20240115")
            print(f"    2024-01-01 ~ 2024-01-15 영업일 수: {len(result)}일")
            
            # 15일의 데이터가 반환되어야 함
            self.assertEqual(len(result), 15)
            self.assertIsInstance(result[0], pd.Timestamp)
            
            # krx 함수가 올바른 파라미터로 호출되었는지 확인
            mock_krx.assert_called_once_with("20240101", "20240115", "000020")
            
            print("  ✅ 날짜 범위로 영업일 조회 테스트 성공")

    def test_get_previous_business_days_invalid_params(self):
        """잘못된 파라미터로 영업일 조회 시도 시 빈 리스트 반환 테스트"""
        print("  ❌ 잘못된 파라미터 테스트 실행 중...")
        
        result = get_previous_business_days(invalid_param="test")
        print(f"    잘못된 파라미터 결과: {result}")
        
        self.assertEqual(result, [])
        print("  ✅ 잘못된 파라미터 테스트 성공")

    def test_get_previous_business_days_december_edge_case(self):
        """12월 경계 케이스 테스트"""
        print("  📅 12월 경계 케이스 테스트 실행 중...")
        
        with patch('pykrx.website.krx.get_market_ohlcv_by_date') as mock_krx:
            mock_dates = pd.date_range('2024-12-01', periods=31, freq='D')
            mock_df = pd.DataFrame(index=mock_dates)
            mock_krx.return_value = mock_df
            
            result = get_previous_business_days(year=2024, month=12)
            print(f"    2024년 12월 영업일 수: {len(result)}일")
            
            # krx 함수가 다음해 1월 1일로 호출되었는지 확인
            mock_krx.assert_called_once_with("20241201", "20250101", "000020")
            
            print("  ✅ 12월 경계 케이스 테스트 성공")

    def test_get_business_days_deprecated(self):
        """get_business_days 함수가 deprecated되었는지 테스트"""
        print("  ⚠️  Deprecated 함수 테스트 실행 중...")
        
        with patch('pykrx.stock.stock_business_days.get_previous_business_days') as mock_func:
            mock_func.return_value = ["20240101", "20240102"]
            
            result = get_business_days(2024, 1)
            print(f"    get_business_days 결과: {result}")
            
            # get_previous_business_days가 호출되었는지 확인
            mock_func.assert_called_once_with(year=2024, month=1)
            self.assertEqual(result, ["20240101", "20240102"])
            
            print("  ✅ Deprecated 함수 테스트 성공")

    def test_business_days_month_filtering(self):
        """영업일 월별 필터링 테스트"""
        print("  🔍 월별 필터링 테스트 실행 중...")
        
        with patch('pykrx.website.krx.get_market_ohlcv_by_date') as mock_krx:
            # 1월과 2월 데이터가 섞인 Mock 데이터 생성
            mock_dates = pd.date_range('2024-01-01', periods=60, freq='D')
            mock_df = pd.DataFrame(index=mock_dates)
            mock_krx.return_value = mock_df
            
            result = get_previous_business_days(year=2024, month=1)
            print(f"    1월 데이터만 필터링된 결과: {len(result)}일")
            
            # 1월 데이터만 필터링되어야 함
            self.assertEqual(len(result), 31)
            for date in result:
                self.assertEqual(date.month, 1)
            
            print("  ✅ 월별 필터링 테스트 성공")


if __name__ == '__main__':
    print("🎯 주식 영업일 관련 함수 테스트 시작")
    print("=" * 50)
    
    unittest.main(verbosity=2)
    
    print("=" * 50)
    print("🎉 모든 테스트 완료!")

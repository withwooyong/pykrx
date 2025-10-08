"""
주식 유틸리티 함수 테스트
"""
import unittest
import pandas as pd
import numpy as np
from pykrx.stock.stock_utils import market_valid_check, resample_ohlcv


class TestStockUtils(unittest.TestCase):
    """주식 유틸리티 함수 테스트 클래스"""

    def setUp(self):
        """테스트 시작 전 실행"""
        print(f"\n🚀 {self._testMethodName} 테스트 시작")

    def tearDown(self):
        """테스트 종료 후 실행"""
        print(f"✅ {self._testMethodName} 테스트 완료\n")

    def test_market_valid_check_decorator(self):
        """market_valid_check 데코레이터 테스트"""
        print("  🎯 market_valid_check 데코레이터 테스트 실행 중...")
        
        @market_valid_check()
        def test_function(market="KOSPI"):
            return f"Valid market: {market}"
        
        # 유효한 시장
        result = test_function("KOSPI")
        print(f"    KOSPI 결과: {result}")
        self.assertEqual(result, "Valid market: KOSPI")
        
        # 유효하지 않은 시장
        result = test_function("INVALID")
        print(f"    INVALID 결과: {type(result)} - {len(result) if hasattr(result, '__len__') else 'N/A'}")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
        
        print("  ✅ market_valid_check 데코레이터 테스트 성공")

    def test_market_valid_check_with_custom_params(self):
        """사용자 정의 파라미터로 market_valid_check 테스트"""
        print("  🎯 사용자 정의 파라미터 테스트 실행 중...")
        
        @market_valid_check(["KOSPI", "KOSDAQ"])
        def test_function(market="KOSPI"):
            return f"Valid market: {market}"
        
        # 유효한 시장
        result = test_function("KOSPI")
        print(f"    KOSPI 결과: {result}")
        self.assertEqual(result, "Valid market: KOSPI")
        
        result = test_function("KOSDAQ")
        print(f"    KOSDAQ 결과: {result}")
        self.assertEqual(result, "Valid market: KOSDAQ")
        
        # 유효하지 않은 시장
        result = test_function("KONEX")
        print(f"    KONEX 결과: {type(result)} - {len(result) if hasattr(result, '__len__') else 'N/A'}")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
        
        print("  ✅ 사용자 정의 파라미터 테스트 성공")

    def test_resample_ohlcv_daily(self):
        """일별 데이터 리샘플링 테스트"""
        print("  📊 일별 데이터 리샘플링 테스트 실행 중...")
        
        # 테스트용 OHLCV 데이터 생성
        dates = pd.date_range('2024-01-01', periods=5, freq='D')
        data = {
            '시가': [100, 101, 102, 103, 104],
            '고가': [105, 106, 107, 108, 109],
            '저가': [95, 96, 97, 98, 99],
            '종가': [101, 102, 103, 104, 105],
            '거래량': [1000, 1100, 1200, 1300, 1400]
        }
        df = pd.DataFrame(data, index=dates)
        print(f"    원본 데이터: {len(df)}행")
        
        # 일별 데이터는 변경되지 않아야 함
        result = resample_ohlcv(df, 'd', 'sum')
        print(f"    일별 리샘플링 결과: {len(result)}행")
        pd.testing.assert_frame_equal(result, df)
        
        print("  ✅ 일별 데이터 리샘플링 테스트 성공")

    def test_resample_ohlcv_monthly(self):
        """월별 데이터 리샘플링 테스트"""
        print("  📊 월별 데이터 리샘플링 테스트 실행 중...")
        
        # 테스트용 OHLCV 데이터 생성 (1개월)
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        data = {
            '시가': [100] * 30,
            '고가': [110] * 30,
            '저가': [90] * 30,
            '종가': [105] * 30,
            '거래량': [1000] * 30
        }
        df = pd.DataFrame(data, index=dates)
        print(f"    원본 데이터: {len(df)}행 (30일)")
        
        # 월별 데이터로 리샘플링
        result = resample_ohlcv(df, 'm', 'sum')
        print(f"    월별 리샘플링 결과: {len(result)}행")
        
        self.assertEqual(len(result), 1)  # 1개월 데이터
        self.assertEqual(result.iloc[0]['시가'], 100)  # 첫 번째 시가
        self.assertEqual(result.iloc[0]['고가'], 110)  # 최고 고가
        self.assertEqual(result.iloc[0]['저가'], 90)   # 최저 저가
        self.assertEqual(result.iloc[0]['종가'], 105)  # 마지막 종가
        self.assertEqual(result.iloc[0]['거래량'], 30000)  # 거래량 합계
        
        print("  ✅ 월별 데이터 리샘플링 테스트 성공")

    def test_resample_ohlcv_yearly(self):
        """연별 데이터 리샘플링 테스트"""
        print("  📊 연별 데이터 리샘플링 테스트 실행 중...")
        
        # 테스트용 OHLCV 데이터 생성 (1년)
        dates = pd.date_range('2024-01-01', periods=365, freq='D')
        data = {
            '시가': [100] * 365,
            '고가': [120] * 365,
            '저가': [80] * 365,
            '종가': [110] * 365,
            '거래량': [1000] * 365
        }
        df = pd.DataFrame(data, index=dates)
        print(f"    원본 데이터: {len(df)}행 (365일)")
        
        # 연별 데이터로 리샘플링
        result = resample_ohlcv(df, 'y', 'sum')
        print(f"    연별 리샘플링 결과: {len(result)}행")
        
        self.assertEqual(len(result), 1)  # 1년 데이터
        self.assertEqual(result.iloc[0]['시가'], 100)  # 첫 번째 시가
        self.assertEqual(result.iloc[0]['고가'], 120)  # 최고 고가
        self.assertEqual(result.iloc[0]['저가'], 80)   # 최저 저가
        self.assertEqual(result.iloc[0]['종가'], 110)  # 마지막 종가
        self.assertEqual(result.iloc[0]['거래량'], 365000)  # 거래량 합계
        
        print("  ✅ 연별 데이터 리샘플링 테스트 성공")

    def test_resample_ohlcv_invalid_freq(self):
        """잘못된 주기로 리샘플링 시도 시 예외 발생 테스트"""
        print("  ❌ 잘못된 주기 테스트 실행 중...")
        
        dates = pd.date_range('2024-01-01', periods=5, freq='D')
        data = {'시가': [100, 101, 102, 103, 104]}
        df = pd.DataFrame(data, index=dates)
        
        with self.assertRaises(RuntimeError):
            resample_ohlcv(df, 'w', 'sum')  # 주별은 지원하지 않음
            print("    RuntimeError 발생 확인")
        
        print("  ✅ 잘못된 주기 테스트 성공")

    def test_resample_ohlcv_empty_dataframe(self):
        """빈 DataFrame 리샘플링 테스트"""
        print("  📊 빈 DataFrame 테스트 실행 중...")
        
        df = pd.DataFrame()
        print(f"    빈 DataFrame 크기: {df.shape}")
        
        result = resample_ohlcv(df, 'm', 'sum')
        print(f"    리샘플링 결과: {result.shape}")
        
        self.assertTrue(result.empty)
        print("  ✅ 빈 DataFrame 테스트 성공")


if __name__ == '__main__':
    print("🎯 주식 유틸리티 함수 테스트 시작")
    print("=" * 50)
    
    unittest.main(verbosity=2)
    
    print("=" * 50)
    print("🎉 모든 테스트 완료!")

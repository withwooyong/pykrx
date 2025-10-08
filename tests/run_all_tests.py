#!/usr/bin/env python3
"""
모든 주식 API 테스트를 실행하는 스크립트
"""
import unittest
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_all_tests():
    """모든 테스트를 실행합니다."""
    # 테스트할 모듈들
    test_modules = [
        'test_stock_utils',
        'test_stock_business_days', 
        'test_stock_ticker',
        'test_stock_ohlcv',
        'test_stock_market_cap'
    ]
    
    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 각 테스트 모듈을 스위트에 추가
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            tests = loader.loadTestsFromModule(module)
            suite.addTests(tests)
            print(f"✅ {module_name} 테스트 로드 완료")
        except ImportError as e:
            print(f"❌ {module_name} 테스트 로드 실패: {e}")
        except Exception as e:
            print(f"⚠️  {module_name} 테스트 로드 중 오류: {e}")
    
    # 테스트 실행
    print("\n🚀 테스트 실행 시작...")
    print("=" * 50)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약:")
    print(f"   실행된 테스트: {result.testsRun}")
    print(f"   실패한 테스트: {len(result.failures)}")
    print(f"   오류가 발생한 테스트: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 실패한 테스트:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n⚠️  오류가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # 종료 코드 설정
    if result.failures or result.errors:
        print("\n❌ 일부 테스트가 실패했습니다.")
        return 1
    else:
        print("\n✅ 모든 테스트가 성공했습니다!")
        return 0

def run_specific_test(test_name):
    """특정 테스트 모듈을 실행합니다."""
    try:
        module = __import__(test_name)
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        
        print(f"🚀 {test_name} 테스트 실행 시작...")
        print("=" * 50)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if not (result.failures or result.errors) else 1
        
    except ImportError as e:
        print(f"❌ {test_name} 모듈을 찾을 수 없습니다: {e}")
        return 1

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 특정 테스트 모듈 실행
        test_name = sys.argv[1]
        if test_name.startswith('test_'):
            exit_code = run_specific_test(test_name)
        else:
            print(f"❌ 잘못된 테스트 이름: {test_name}")
            print("사용법: python run_all_tests.py [test_module_name]")
            exit_code = 1
    else:
        # 모든 테스트 실행
        exit_code = run_all_tests()
    
    sys.exit(exit_code)

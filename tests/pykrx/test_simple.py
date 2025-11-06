import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_basic_imports():
    """기본 import 테스트"""
    try:
        from pykrx.stock import stock_business_days

        print("✅ stock_business_days 모듈 import 성공")

        from pykrx.stock import stock_ticker

        print("✅ stock_ticker 모듈 import 성공")

        from pykrx.stock import stock_ohlcv

        print("✅ stock_ohlcv 모듈 import 성공")

        print("\n🎉 모든 모듈 import 성공!")
        return True

    except ImportError as e:
        print(f"❌ Import 오류: {e}")
        return False


if __name__ == "__main__":
    test_basic_imports()

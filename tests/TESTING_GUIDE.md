# 테스트 코드 작성 가이드

## 테스트 패턴 선택 기준

### 참고: https://www.bangseongbeom.com/unittest-vs-pytest.html

프로젝트에서는 두 가지 테스트 패턴을 사용합니다:

### 1. 단위 테스트 (Unit Test) - Mock 패턴

**사용 시기:**

- 함수의 로직과 동작을 검증하고 싶을 때
- 빠른 테스트 실행이 필요할 때
- 외부 API 의존성 없이 테스트하고 싶을 때
- CI/CD 파이프라인에서 안정적인 테스트가 필요할 때

**사용 예시:**

```python
from unittest.mock import patch
import pandas as pd

def test_get_market_ohlcv_by_date():
    with patch("pykrx.website.naver.get_market_ohlcv_by_date") as mock_naver:
        mock_df = pd.DataFrame({"시가": [100], "고가": [105]})
        mock_naver.return_value = mock_df

        result = get_market_ohlcv_by_date("20240101", "20240115", "005930")

        assert isinstance(result, pd.DataFrame)
        mock_naver.assert_called_once_with("20240101", "20240115", "005930")
```

**파일 위치:** `tests/pykrx/` 하위 또는 `tests/test_xxx.py` (단위 테스트)

### 2. 통합 테스트 (Integration Test) - 실제 API 호출

**사용 시기:**

- 실제 API 응답 데이터를 검증하고 싶을 때
- 실제 데이터 값의 정확성을 확인하고 싶을 때
- 전체 시스템의 동작을 검증하고 싶을 때
- 실제 사용 예시를 문서화하고 싶을 때

**사용 예시:**

```python
from pykrx import stock
import pandas as pd

def test_get_market_ohlcv_by_date():
    df = stock.get_market_ohlcv_by_date("20210118", "20210126", "005930")
    print(df)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "시가" in df.columns
    # 실제 데이터 값 검증
    assert abs(df.iloc[0, 0] - 86600) < 0.01
```

**파일 위치:** `tests/test_xxx_api.py` 또는 `tests/pykrx/xxx/test_xxx_api.py` (통합 테스트)

## 권장 사항

### 1. 테스트 파일 구조

```
tests/
├── pykrx/              # 단위 테스트 (Mock 사용)
│   ├── stock/
│   │   ├── test_stock_ohlcv.py
│   │   ├── test_stock_business_days.py
│   │   └── test_stock_ticker.py
│   └── bond/
│       └── test_bond_api.py
├── test_market_api.py  # 통합 테스트 (실제 API 호출)
└── test_index_api.py   # 통합 테스트
```

### 2. 테스트 작성 원칙

#### 단위 테스트 (Mock 패턴)

- ✅ 함수의 로직 검증에 집중
- ✅ Mock을 사용하여 외부 의존성 제거
- ✅ 빠른 실행 속도
- ✅ 안정적인 CI/CD 통합
- ✅ 에러 케이스 테스트 용이

#### 통합 테스트 (실제 API 호출)

- ✅ 실제 데이터 검증
- ✅ Print 문으로 결과 출력 (사용자 확인용)
- ✅ 실제 사용 시나리오 테스트
- ✅ 문서화 목적
- ⚠️ 네트워크 의존성 (느리고 불안정할 수 있음)

### 3. 일관성 유지

같은 목적의 테스트는 같은 패턴을 사용하세요:

- **Wrapper 함수 테스트** (`stock_api.py`):

  - 옵션 1: Mock 패턴 (함수 로직 검증)
  - 옵션 2: 실제 API 호출 (통합 검증)

- **Core 함수 테스트** (`stock_ohlcv.py`, `stock_ticker.py`):
  - Mock 패턴 권장 (단위 테스트)

### 4. 현재 프로젝트 상황

현재 `test_stock_api.py`는 **통합 테스트 스타일**로 작성되어 있습니다. 이는 다음 이유로 적절합니다:

- ✅ 실제 API 응답 데이터 검증
- ✅ 사용자에게 실제 사용 예시 제공
- ✅ Print 출력으로 결과 확인 가능

하지만 다음 개선을 고려할 수 있습니다:

1. **하이브리드 접근**: 핵심 로직은 Mock으로, 실제 데이터 검증은 통합 테스트로
2. **테스트 분리**: `test_stock_api_unit.py` (Mock)와 `test_stock_api_integration.py` (실제 호출)로 분리

## 결론

**`test_stock_api.py`의 현재 스타일(통합 테스트)은 유지하는 것이 좋습니다.**

이유:

1. 실제 API 응답 데이터의 정확성을 검증할 수 있음
2. Print 출력으로 사용자가 결과를 확인할 수 있음
3. 실제 사용 시나리오를 테스트할 수 있음
4. `test_bond_api.py`와 일관된 스타일 유지

**`test_stock_business_days.py`의 Mock 패턴도 유지하는 것이 좋습니다.**

이유:

1. 함수 로직 검증에 집중
2. 빠르고 안정적인 테스트
3. 외부 의존성 없이 테스트 가능

두 패턴은 서로 다른 목적을 가지고 있으므로, 각각의 목적에 맞게 사용하는 것이 좋습니다.

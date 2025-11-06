"""채권 API 테스트"""

import numpy as np
import pandas as pd

from pykrx import bond


class TestBondOtcTreasuryYieldByTicker:
    def test_holiday(self):
        df = bond.get_otc_treasury_yields("20220202")
        print(df)
        assert len(df) != 0
        assert isinstance(df, pd.DataFrame)

    def test_business_day(self):
        df = bond.get_otc_treasury_yields("20220204")
        print(df)
        #              수익률   대비
        # 채권종류
        # 국고채 1년    1.467  0.015
        # 국고채 2년    1.995  0.026
        # 국고채 3년    2.194  0.036
        # 국고채 5년    2.418  0.045
        # 국고채 10년   2.619  0.053
        assert abs(df.iloc[0, 0] - 1.467) < 0.001
        assert abs(df.iloc[1, 0] - 1.995) < 0.001


class TestBondOtcTreasuryYieldByDate:
    def test_business_day(self):
        df = bond.get_otc_treasury_yields("20220104", "20220203", "국고채1년")
        print(df)
        assert len(df) != 0
        assert isinstance(df, pd.DataFrame)


if __name__ == "__main__":
    test = TestBondOtcTreasuryYieldByTicker()
    test.test_holiday()
    test.test_business_day()
    test = TestBondOtcTreasuryYieldByDate()
    test.test_business_day()

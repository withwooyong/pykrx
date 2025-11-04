#!/usr/bin/env python3
"""
pykrx 웹 API 서버
pykrx 라이브러리의 기능을 REST API로 제공합니다.
"""

from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI, HTTPException, Path, Query

from pykrx import bond, stock

# 기본 날짜 설정 (최근 영업일 기준)
_DEFAULT_TO_DATE = datetime.now().strftime("%Y%m%d")
_DEFAULT_FROM_DATE = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

app = FastAPI(
    title="pykrx API Server",
    description="KRX 주식 데이터를 제공하는 REST API 서버",
    version="1.0.0",
)


@app.get("/")
async def root():
    """서버 상태 확인"""
    return {"status": "ok", "message": "pykrx API Server is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


# ==================== Stock API ====================


@app.get("/api/stock/ticker/list")
async def get_ticker_list(
    date: str | None = Query(None, description="조회 일자 (YYYYMMDD)", example="20240115"),
    market: str | None = Query(
        "KOSPI", description="시장 (KOSPI/KOSDAQ/KONEX/ALL)", example="KOSPI"
    ),
):
    """티커 리스트 조회"""
    try:
        # 타입 체커를 만족시키기 위해 기본값 명시
        market_value = market if market is not None else "KOSPI"
        # date는 None을 허용 (함수 내부에서 처리)
        tickers = stock.get_market_ticker_list(date, market=market_value)  # type: ignore
        return {"date": date, "market": market_value, "count": len(tickers), "tickers": tickers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/stock/ticker/{ticker}/name")
async def get_ticker_name(
    ticker: str = Path(..., description="티커 코드", example="005930"),
):
    """티커 이름 조회"""
    try:
        name = stock.get_market_ticker_name(ticker)
        return {"ticker": ticker, "name": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/stock/ohlcv/date")
async def get_ohlcv_by_date(
    fromdate: str = Query(
        _DEFAULT_FROM_DATE, description="시작 일자 (YYYYMMDD)", example="20240101"
    ),
    todate: str = Query(_DEFAULT_TO_DATE, description="종료 일자 (YYYYMMDD)", example="20240131"),
    ticker: str = Query("005930", description="티커 코드 (예: 005930=삼성전자)", example="005930"),
    freq: str | None = Query("d", description="리샘플링 주기 (d/m/y)", example="d"),
):
    """일자별 OHLCV 데이터 조회"""
    try:
        freq_value = freq if freq is not None else "d"
        df = stock.get_market_ohlcv_by_date(fromdate, todate, ticker, freq=freq_value)
        # DataFrame을 JSON으로 변환
        df.reset_index(inplace=True)
        df["날짜"] = df["날짜"].astype(str)
        return {
            "fromdate": fromdate,
            "todate": todate,
            "ticker": ticker,
            "data": df.to_dict(orient="records"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/stock/ohlcv/ticker")
async def get_ohlcv_by_ticker(
    date: str = Query(_DEFAULT_TO_DATE, description="조회 일자 (YYYYMMDD)", example="20240115"),
    market: str | None = Query("KOSPI", description="시장 (KOSPI/KOSDAQ/KONEX)", example="KOSPI"),
):
    """티커별 OHLCV 데이터 조회"""
    try:
        market_value = market if market is not None else "KOSPI"
        df = stock.get_market_ohlcv_by_ticker(date, market_value)
        df.reset_index(inplace=True)
        return {
            "date": date,
            "market": market_value,
            "count": len(df),
            "data": df.to_dict(orient="records"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/stock/market-cap")
async def get_market_cap(
    fromdate: str = Query(
        _DEFAULT_FROM_DATE, description="시작 일자 (YYYYMMDD)", example="20240101"
    ),
    todate: str = Query(_DEFAULT_TO_DATE, description="종료 일자 (YYYYMMDD)", example="20240131"),
    ticker: str = Query("005930", description="티커 코드 (예: 005930=삼성전자)", example="005930"),
):
    """시가총액 조회"""
    try:
        df = stock.get_market_cap_by_date(fromdate, todate, ticker)
        df.reset_index(inplace=True)
        df["날짜"] = df["날짜"].astype(str)
        return {
            "fromdate": fromdate,
            "todate": todate,
            "ticker": ticker,
            "data": df.to_dict(orient="records"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/stock/net-purchases")
async def get_net_purchases(
    fromdate: str = Query(
        _DEFAULT_FROM_DATE, description="시작 일자 (YYYYMMDD)", example="20240101"
    ),
    todate: str = Query(_DEFAULT_TO_DATE, description="종료 일자 (YYYYMMDD)", example="20240131"),
    market: str | None = Query("ALL", description="시장 (KOSPI/KOSDAQ/KONEX/ALL)", example="ALL"),
    investor: str | None = Query("전체", description="투자자", example="전체"),
):
    """투자자별 순매수 상위종목 조회"""
    try:
        market_value = market if market is not None else "ALL"
        investor_value = investor if investor is not None else "전체"
        df = stock.get_market_net_purchases_of_equities_by_ticker(
            fromdate, todate, market_value, investor_value
        )
        df.reset_index(inplace=True)
        return {
            "fromdate": fromdate,
            "todate": todate,
            "market": market_value,
            "investor": investor_value,
            "count": len(df),
            "data": df.to_dict(orient="records"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================== Index API ====================


@app.get("/api/index/ticker/list")
async def get_index_ticker_list(
    date: str | None = Query(None, description="조회 일자 (YYYYMMDD)", example="20240115"),
    market: str | None = Query(
        "KOSPI", description="시장 (KOSPI/KOSDAQ/KRX/테마)", example="KOSPI"
    ),
):
    """지수 티커 리스트 조회"""
    try:
        market_value = market if market is not None else "KOSPI"
        # date는 None을 허용 (함수 내부에서 처리)
        tickers = stock.get_index_ticker_list(date, market_value)  # type: ignore
        return {"date": date, "market": market_value, "count": len(tickers), "tickers": tickers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/index/ohlcv")
async def get_index_ohlcv(
    fromdate: str = Query(
        _DEFAULT_FROM_DATE, description="시작 일자 (YYYYMMDD)", example="20240101"
    ),
    todate: str = Query(_DEFAULT_TO_DATE, description="종료 일자 (YYYYMMDD)", example="20240131"),
    ticker: str = Query("1001", description="지수 티커 (예: 1001=코스피)", example="1001"),
):
    """지수 OHLCV 조회"""
    try:
        df = stock.get_index_ohlcv_by_date(fromdate, todate, ticker)
        df.reset_index(inplace=True)
        df["날짜"] = df["날짜"].astype(str)
        return {
            "fromdate": fromdate,
            "todate": todate,
            "ticker": ticker,
            "data": df.to_dict(orient="records"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================== Bond API ====================


@app.get("/api/bond/treasury-yields")
async def get_treasury_yields(
    fromdate: str = Query(
        _DEFAULT_FROM_DATE, description="시작 일자 (YYYYMMDD)", example="20240101"
    ),
    todate: str = Query(_DEFAULT_TO_DATE, description="종료 일자 (YYYYMMDD)", example="20240131"),
    ticker: str = Query(
        "국고채3년",
        description="채권 종류 (국고채1년/국고채2년/국고채3년/국고채5년/국고채10년/국고채20년/국고채30년/국민주택1종5년/회사채AA/회사채BBB/CD)",
        example="국고채3년",
    ),
):
    """국채 수익률 조회"""
    try:
        df = bond.get_otc_treasury_yields(fromdate, todate, ticker)

        # 빈 DataFrame 체크
        if df.empty:
            return {
                "fromdate": fromdate,
                "todate": todate,
                "ticker": ticker,
                "data": [],
                "message": "조회 결과가 없습니다.",
            }

        df.reset_index(inplace=True)

        # 인덱스 컬럼 이름 확인 및 변환
        if "일자" in df.columns:
            df.rename(columns={"일자": "날짜"}, inplace=True)
        elif df.index.name == "일자":
            df.index.name = "날짜"

        # 날짜 컬럼이 있으면 문자열로 변환
        if "날짜" in df.columns:
            df["날짜"] = df["날짜"].astype(str)

        return {
            "fromdate": fromdate,
            "todate": todate,
            "ticker": ticker,
            "data": df.to_dict(orient="records"),
        }
    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"잘못된 채권 종류입니다. 지원하는 종류: 국고채1년/국고채2년/국고채3년/국고채5년/국고채10년/국고채20년/국고채30년/국민주택1종5년/회사채AA/회사채BBB/CD. 오류: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}") from e


if __name__ == "__main__":
    # 서버 실행
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 개발 모드: 코드 변경 시 자동 재시작
        log_level="info",
    )

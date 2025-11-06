"""
진행 상황 추적 모듈
"""

import json
from datetime import datetime

from .config import Config


class ProgressTracker:
    """진행 상황 추적 클래스"""

    def __init__(self, progress_file: str = "progress.json"):
        """진행 상황 추적 초기화"""

        self.progress_file = Config.PROGRESS_DIR / progress_file
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        self.progress = self._load_progress()

    def _load_progress(self) -> dict:
        """진행 상황 파일 로드"""

        if self.progress_file.exists():
            try:
                with open(self.progress_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  진행 상황 파일 로드 실패: {e}")
                return {}
        return {
            "metadata_collected": False,
            "tickers": {},
            "last_updated": None,
            "stats": {
                "total_tickers": 0,
                "completed_tickers": 0,
                "failed_tickers": 0,
            },
        }

    def save_progress(self):
        """진행 상황 저장"""

        self.progress["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.progress_file, "w", encoding="utf-8") as f:
                json.dump(self.progress, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  진행 상황 저장 실패: {e}")

    def mark_metadata_collected(self):
        """메타데이터 수집 완료 표시"""

        self.progress["metadata_collected"] = True
        self.save_progress()

    def is_metadata_collected(self) -> bool:
        """메타데이터 수집 여부 확인"""

        return self.progress.get("metadata_collected", False)

    def add_ticker(
        self,
        ticker: str,
        market: str,
        listing_date: str | None = None,
        delisting_date: str | None = None,
    ):
        """티커 추가"""

        if "tickers" not in self.progress:
            self.progress["tickers"] = {}

        self.progress["tickers"][ticker] = {
            "market": market,
            "listing_date": listing_date,
            "delisting_date": delisting_date,
            "collected": False,
            "last_collected_date": None,
            "error": None,
        }
        self.progress["stats"]["total_tickers"] = len(self.progress["tickers"])
        self.save_progress()

    def mark_ticker_completed(self, ticker: str, last_date: str | None = None):
        """티커 수집 완료 표시"""

        if ticker in self.progress.get("tickers", {}):
            self.progress["tickers"][ticker]["collected"] = True
            if last_date:
                self.progress["tickers"][ticker]["last_collected_date"] = last_date
            self.progress["stats"]["completed_tickers"] = sum(
                1 for t in self.progress["tickers"].values() if t.get("collected", False)
            )
            self.save_progress()

    def mark_ticker_failed(self, ticker: str, error: str):
        """티커 수집 실패 표시"""

        if ticker in self.progress.get("tickers", {}):
            self.progress["tickers"][ticker]["error"] = str(error)
            self.progress["stats"]["failed_tickers"] = sum(
                1 for t in self.progress["tickers"].values() if t.get("error") is not None
            )
            self.save_progress()

    def is_ticker_collected(self, ticker: str) -> bool:
        """티커 수집 여부 확인"""

        return self.progress.get("tickers", {}).get(ticker, {}).get("collected", False)

    def get_ticker_info(self, ticker: str) -> dict | None:
        """티커 정보 조회"""

        return self.progress.get("tickers", {}).get(ticker)

    def get_pending_tickers(self) -> list[str]:
        """수집 대기 중인 티커 리스트"""

        return [
            ticker
            for ticker, info in self.progress.get("tickers", {}).items()
            if not info.get("collected", False) and info.get("error") is None
        ]

    def get_stats(self) -> dict:
        """통계 정보 조회"""

        return self.progress.get("stats", {})

    def reset_ticker(self, ticker: str):
        """티커 수집 상태 초기화 (재수집용)"""

        if ticker in self.progress.get("tickers", {}):
            self.progress["tickers"][ticker]["collected"] = False
            self.progress["tickers"][ticker]["error"] = None
            self.progress["tickers"][ticker]["last_collected_date"] = None
            self.save_progress()

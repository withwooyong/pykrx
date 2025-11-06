"""
백테스팅 데이터 수집 메인 스크립트
"""

import argparse
import sys

from .config import Config
from .metadata_collector import MetadataCollector
from .ohlcv_collector import OHLCVCollector
from .progress_tracker import ProgressTracker
from .storage import StorageManager


def collect_backtest_data(
    skip_metadata: bool = False,
    skip_ohlcv: bool = False,
    use_multiprocessing: bool = True,
    reset_progress: bool = False,
):
    """백테스팅 데이터 수집 메인 함수

    Args:
        skip_metadata: 메타데이터 수집 스킵
        skip_ohlcv: OHLCV 데이터 수집 스킵
        use_multiprocessing: 멀티프로세싱 사용 여부
        reset_progress: 진행 상황 초기화
    """

    print("=" * 60)
    print("🚀 백테스팅 데이터 수집 시작")
    print("=" * 60)
    print(f"📁 데이터 저장 경로: {Config.BASE_DIR}")
    print(f"📅 수집 기간: {Config.START_DATE} ~ {Config.END_DATE}")
    print(f"🏢 수집 시장: {', '.join(Config.MARKETS)}")
    print(f"📊 수정주가: {'사용' if Config.ADJUSTED else '미사용'}")
    print("=" * 60)

    # 디렉토리 설정
    Config.setup_directories()

    # 진행 상황 추적 초기화
    progress_tracker = ProgressTracker()

    if reset_progress:
        print("\n⚠️  진행 상황을 초기화합니다.")
        progress_file = progress_tracker.progress_file
        if progress_file.exists():
            progress_file.unlink()
        progress_tracker = ProgressTracker()

    # StorageManager 초기화
    storage = StorageManager()

    try:
        # Phase 1: 메타데이터 수집
        if not skip_metadata:
            if progress_tracker.is_metadata_collected():
                print("\n✅ 메타데이터가 이미 수집되어 있습니다. 스킵합니다.")
            else:
                metadata_collector = MetadataCollector(progress_tracker, storage)
                metadata_df = metadata_collector.collect_all_tickers()

                if metadata_df.empty:
                    print("\n❌ 메타데이터 수집 실패. 종료합니다.")
                    return
        else:
            print("\n⏭️  메타데이터 수집을 스킵합니다.")

        # Phase 2: OHLCV 데이터 수집
        if not skip_ohlcv:
            ohlcv_collector = OHLCVCollector(progress_tracker, storage)
            ohlcv_collector.collect_all_ohlcv(use_multiprocessing=use_multiprocessing)
        else:
            print("\n⏭️  OHLCV 데이터 수집을 스킵합니다.")

        # 최종 통계
        stats = progress_tracker.get_stats()
        print("\n" + "=" * 60)
        print("📊 최종 통계")
        print("=" * 60)
        print(f"  전체 티커: {stats.get('total_tickers', 0)}개")
        print(f"  완료: {stats.get('completed_tickers', 0)}개")
        print(f"  실패: {stats.get('failed_tickers', 0)}개")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        print("진행 상황이 저장되었습니다. 나중에 다시 실행하면 이어서 진행됩니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        storage.close()


def main():
    """CLI 진입점"""

    parser = argparse.ArgumentParser(description="백테스팅 데이터 수집 크롤러")
    parser.add_argument(
        "--skip-metadata",
        action="store_true",
        help="메타데이터 수집 스킵",
    )
    parser.add_argument(
        "--skip-ohlcv",
        action="store_true",
        help="OHLCV 데이터 수집 스킵",
    )
    parser.add_argument(
        "--no-multiprocessing",
        action="store_true",
        help="멀티프로세싱 비활성화",
    )
    parser.add_argument(
        "--reset-progress",
        action="store_true",
        help="진행 상황 초기화",
    )

    args = parser.parse_args()

    collect_backtest_data(
        skip_metadata=args.skip_metadata,
        skip_ohlcv=args.skip_ohlcv,
        use_multiprocessing=not args.no_multiprocessing,
        reset_progress=args.reset_progress,
    )


if __name__ == "__main__":
    main()

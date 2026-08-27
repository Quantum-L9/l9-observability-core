from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from l9_observability_core import elapsed_milliseconds


def test_elapsed_milliseconds_floors_sub_millisecond_remainder() -> None:
    start = datetime(2026, 8, 23, 21, 0, 0, 0, tzinfo=UTC)
    end = datetime(2026, 8, 23, 21, 0, 0, 1999, tzinfo=UTC)
    assert elapsed_milliseconds(start, end) == 1


def test_elapsed_milliseconds_uses_absolute_time_across_dst_fold() -> None:
    zone = ZoneInfo("America/New_York")
    start = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=0)
    end = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=1)
    assert elapsed_milliseconds(start, end) == 3_600_000

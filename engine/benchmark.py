# engine/benchmark.py
"""
Đo thời gian thực thi của tất cả algorithm cho 3 Scenario.

Nguyên tắc đo:
    - Dùng time.perf_counter() — độ phân giải nano-second, đủ cho O(1) lookup.
    - Lặp REPEAT lần, lấy trung bình — loại bỏ nhiễu OS scheduler.
    - _avg_ms trả về CẢ kết quả lần chạy cuối → không phải gọi hàm thêm 1 lần
      chỉ để lấy result.

Mỗi hàm trả về dict chuẩn để frontend render —
không có bất kỳ logic in ấn nào ở đây (Separation of Concerns).
"""

import time

from engine.search import (
    linear_search,
    binary_search,
    linear_filter_dept_gpa,
    linear_filter_gpa,
    binary_filter_dept_gpa,
    binary_filter_gpa,
    sort_by_id,
    sort_by_gpa,
)
from engine.fuzzy_search import fuzzy_linear_search


REPEAT = 10


# ══════════════════════════════════════════════════════════════════
#  Helper chung
# ══════════════════════════════════════════════════════════════════

def _avg_ms(fn, repeat: int = REPEAT) -> tuple:
    """Chạy fn() `repeat` lần, trả về (avg_ms, last_result)."""
    total  = 0.0
    result = None
    for _ in range(repeat):
        start  = time.perf_counter()
        result = fn()
        total += time.perf_counter() - start
    return (total / repeat) * 1000, result


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 1 — Tra cứu theo MSSV
# ══════════════════════════════════════════════════════════════════

def bench_s1_chain(ht_chain, target_id: str) -> dict:
    ms, found = _avg_ms(lambda: ht_chain.search(target_id))
    return {"algo": "Hash Chaining", "ms": ms, "sort_ms": None, "found": found, "failed": False}


def bench_s1_open(ht_open, target_id: str) -> dict:
    ms, found = _avg_ms(lambda: ht_open.search(target_id))
    return {"algo": "Hash Open Addr.", "ms": ms, "sort_ms": None, "found": found, "failed": False}


def bench_s1_linear(records: list, target_id: str) -> dict:
    ms, found = _avg_ms(lambda: linear_search(records, target_id))
    return {"algo": "Linear Search", "ms": ms, "sort_ms": None, "found": found, "failed": False}


def bench_s1_binary(records: list, target_id: str) -> dict:
    sort_start     = time.perf_counter()
    sorted_records = sort_by_id(records)
    sort_ms        = (time.perf_counter() - sort_start) * 1000

    ms, found = _avg_ms(lambda: binary_search(sorted_records, target_id))
    return {"algo": "Binary Search", "ms": ms, "sort_ms": sort_ms, "found": found, "failed": False}


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 2A — Lọc GPA + Department
# ══════════════════════════════════════════════════════════════════

def bench_s2a_chain(ht_chain_dept, department: str, min_gpa: float, max_gpa: float) -> dict:
    def _filter():
        bucket = ht_chain_dept.search(department)
        return [r for r in bucket if min_gpa <= r["gpa"] <= max_gpa]

    ms, matches = _avg_ms(_filter)
    return {"algo": "Hash Chaining", "ms": ms, "sort_ms": None, "match_count": len(matches), "matches": matches, "failed": False}

def bench_s2a_open(ht_open_dept, department: str, min_gpa: float, max_gpa: float) -> dict:
    def _filter():
        bucket = ht_open_dept.search(department)
        return [r for r in bucket if min_gpa <= r["gpa"] <= max_gpa]

    ms, matches = _avg_ms(_filter)
    return {"algo": "Open Addr. Hash", "ms": ms, "sort_ms": None, "match_count": len(matches), "matches": matches, "failed": False}


def bench_s2a_linear(records: list, department: str, min_gpa: float, max_gpa: float) -> dict:
    ms, matches = _avg_ms(lambda: linear_filter_dept_gpa(records, department, min_gpa, max_gpa))
    return {"algo": "Linear Scan", "ms": ms, "sort_ms": None, "match_count": len(matches), "matches": matches, "failed": False}


def bench_s2a_binary(records, department, min_gpa, max_gpa):
    sort_start              = time.perf_counter()
    sorted_by_gpa, gpa_keys = sort_by_gpa(records)
    sort_ms                 = (time.perf_counter() - sort_start) * 1000

    ms, matches = _avg_ms(lambda: binary_filter_dept_gpa(sorted_by_gpa, gpa_keys, department, min_gpa, max_gpa))
    return {"algo": "Binary Filter", "ms": ms, "sort_ms": sort_ms, "match_count": len(matches), "matches": matches, "failed": False}


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 2B — Lọc khoảng GPA thuần
# ══════════════════════════════════════════════════════════════════

def bench_s2b_hash(min_gpa: float, max_gpa: float) -> dict:
    return {"algo": "Hash lookup", "ms": None, "sort_ms": None, "match_count": 0, "matches": [], "failed": True}


def bench_s2b_linear(records: list, min_gpa: float, max_gpa: float) -> dict:
    ms, matches = _avg_ms(lambda: linear_filter_gpa(records, min_gpa, max_gpa))
    return {"algo": "Linear Scan", "ms": ms, "sort_ms": None, "match_count": len(matches), "matches": matches, "failed": False}


def bench_s2b_binary(records, min_gpa, max_gpa):
    sort_start              = time.perf_counter()
    sorted_by_gpa, gpa_keys = sort_by_gpa(records)
    sort_ms                 = (time.perf_counter() - sort_start) * 1000

    ms, matches = _avg_ms(lambda: binary_filter_gpa(sorted_by_gpa, gpa_keys, min_gpa, max_gpa))
    return {"algo": "Binary Filter", "ms": ms, "sort_ms": sort_ms, "match_count": len(matches), "matches": matches, "failed": False}

# ══════════════════════════════════════════════════════════════════
#  SCENARIO 3 — Tìm tên mờ
# ══════════════════════════════════════════════════════════════════

def bench_s3_fuzzy(records: list, query: str) -> dict:
    ms, matches = _avg_ms(lambda: fuzzy_linear_search(records, query))
    return {"algo": "Fuzzy Linear Search", "ms": ms, "match_count": len(matches), "matches": matches, "failed": False}


def bench_s3_inverted(inv_index, query: str) -> dict:
    ms, matches = _avg_ms(lambda: inv_index.search(query))
    return {
        "algo": "Inverted Index",
        "ms": ms,
        "match_count": len(matches),
        "matches": matches,
        "failed": False
    }
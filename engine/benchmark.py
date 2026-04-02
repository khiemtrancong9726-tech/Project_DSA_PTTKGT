# engine/benchmark.py
"""
Đo thời gian thực thi của tất cả algorithm cho 3 Scenario.

Nguyên tắc đo:
    - Dùng time.perf_counter() — độ phân giải nano-second, đủ cho O(1) lookup.
    - Lặp REPEAT lần, lấy trung bình — loại bỏ nhiễu OS scheduler.
    - Không dùng time.time() — độ phân giải ms, không đủ cho Hash lookup.

Mỗi hàm trả về dict chuẩn để display.py render —
không có bất kỳ logic in ấn nào ở đây (Separation of Concerns).
"""

import time
import bisect

from engine.search import (
    linear_search,
    sort_by_id,
    sort_by_gpa,
    binary_search,
)
from engine.fuzzy_search import measure_fuzzy, hash_lookup_by_name


REPEAT = 100   # số lần lặp để lấy trung bình — loại nhiễu


# ══════════════════════════════════════════════════════════════════
#  Helper chung
# ══════════════════════════════════════════════════════════════════

def _avg_ms(fn, repeat: int = REPEAT) -> float:
    total = 0.0
    for _ in range(repeat):
        start  = time.perf_counter()
        fn()
        total += time.perf_counter() - start
    return (total / repeat) * 1000


def _build_dept_index(records: list) -> dict:
    index = {}
    for r in records:
        dept = r["department_code"]
        if dept not in index:
            index[dept] = []
        index[dept].append(r)
    return index


def _composite_filter(dept_index: dict, department: str, min_gpa: float, max_gpa: float) -> list:
    bucket = dept_index.get(department, [])
    return [r for r in bucket if min_gpa <= r["gpa"] <= max_gpa]


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 1 — Tra cứu theo MSSV — từng thuật toán riêng
# ══════════════════════════════════════════════════════════════════

def bench_s1_chain(ht_chain, target_id: str) -> dict:
    """Hash Chaining — tìm 1 sinh viên theo MSSV."""
    ms    = _avg_ms(lambda: ht_chain.search(target_id))
    found = ht_chain.search(target_id)
    return {
        "algo":     "Hash Chaining",
        "ms":       ms,
        "sort_ms":  None,
        "found":    found,
        "failed":   False,
    }


def bench_s1_open(ht_open, target_id: str) -> dict:
    """Hash Open Addressing — tìm 1 sinh viên theo MSSV."""
    ms    = _avg_ms(lambda: ht_open.search(target_id))
    found = ht_open.search(target_id)
    return {
        "algo":     "Hash Open Addr.",
        "ms":       ms,
        "sort_ms":  None,
        "found":    found,
        "failed":   False,
    }


def bench_s1_linear(records: list, target_id: str) -> dict:
    """Linear Search — tìm 1 sinh viên theo MSSV."""
    ms       = _avg_ms(lambda: linear_search(records, target_id))
    found, _ = linear_search(records, target_id)
    return {
        "algo":     "Linear Search",
        "ms":       ms,
        "sort_ms":  None,
        "found":    found,
        "failed":   False,
    }


def bench_s1_binary(records: list, target_id: str) -> dict:
    """Binary Search — sort 1 lần, đo search riêng."""
    sorted_records, sort_ms = sort_by_id(records)
    ms       = _avg_ms(lambda: binary_search(sorted_records, target_id))
    found, _ = binary_search(sorted_records, target_id)
    return {
        "algo":     "Binary Search",
        "ms":       ms,
        "sort_ms":  sort_ms,
        "found":    found,
        "failed":   False,
    }


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 2A — Lọc GPA + Department — từng thuật toán riêng
# ══════════════════════════════════════════════════════════════════

def bench_s2a_hash(records: list, department: str, min_gpa: float, max_gpa: float) -> dict:
    """Composite Hash — bucket theo department, filter khoảng GPA trong bucket."""
    dept_index = _build_dept_index(records)
    def _filter(): return _composite_filter(dept_index, department, min_gpa, max_gpa)
    ms      = _avg_ms(_filter)
    matches = _filter()
    return {
        "algo":        "Composite Hash",
        "ms":          ms,
        "sort_ms":     None,
        "match_count": len(matches),
        "matches":     matches,
        "failed":      False,
    }


def bench_s2a_linear(records: list, department: str, min_gpa: float, max_gpa: float) -> dict:
    """Linear Scan — duyệt toàn bộ, check khoảng GPA và department."""
    def _filter(): return [r for r in records if r["department_code"] == department and min_gpa <= r["gpa"] <= max_gpa]
    ms      = _avg_ms(_filter)
    matches = _filter()
    return {
        "algo":        "Linear Scan",
        "ms":          ms,
        "sort_ms":     None,
        "match_count": len(matches),
        "matches":     matches,
        "failed":      False,
    }


def bench_s2a_binary(records: list, department: str, min_gpa: float, max_gpa: float) -> dict:
    """Binary Filter — sort theo GPA, bisect tìm khoảng [min, max], filter department."""
    sorted_by_gpa, sort_ms = sort_by_gpa(records)

    def _filter():
        gpa_keys = [r["gpa"] for r in sorted_by_gpa]
        lo = bisect.bisect_left(gpa_keys, min_gpa)
        hi = bisect.bisect_right(gpa_keys, max_gpa)
        return [r for r in sorted_by_gpa[lo:hi] if r["department_code"] == department]

    ms      = _avg_ms(_filter)
    matches = _filter()
    return {
        "algo":        "Binary Filter",
        "ms":          ms,
        "sort_ms":     sort_ms,
        "match_count": len(matches),
        "matches":     matches,
        "failed":      False,
    }


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 2B — Lọc khoảng GPA — từng thuật toán riêng
# ══════════════════════════════════════════════════════════════════

def bench_s2b_hash(min_gpa: float, max_gpa: float) -> dict:
    """Hash — FAILED: không có khái niệm khoảng."""
    return {
        "algo":        "Hash lookup",
        "ms":          None,
        "sort_ms":     None,
        "match_count": 0,
        "matches":     [],
        "failed":      True,
    }


def bench_s2b_linear(records: list, min_gpa: float, max_gpa: float) -> dict:
    """Linear Scan — duyệt toàn bộ, check khoảng GPA."""
    def _filter():
        return [r for r in records if min_gpa <= r["gpa"] <= max_gpa]
    ms      = _avg_ms(_filter)
    matches = _filter()
    return {
        "algo":        "Linear Scan",
        "ms":          ms,
        "sort_ms":     None,
        "match_count": len(matches),
        "matches":     matches,
        "failed":      False,
    }


def bench_s2b_binary(records: list, min_gpa: float, max_gpa: float) -> dict:
    """Binary Filter — sort theo GPA, bisect tìm khoảng [min, max]."""
    sorted_by_gpa, sort_ms = sort_by_gpa(records)

    def _filter():
        gpa_keys = [r["gpa"] for r in sorted_by_gpa]
        lo = bisect.bisect_left(gpa_keys, min_gpa)
        hi = bisect.bisect_right(gpa_keys, max_gpa)
        return sorted_by_gpa[lo:hi]

    ms      = _avg_ms(_filter)
    matches = _filter()
    return {
        "algo":        "Binary Filter",
        "ms":          ms,
        "sort_ms":     sort_ms,
        "match_count": len(matches),
        "matches":     matches,
        "failed":      False,
    }


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 3 — Tìm tên mờ — từng thuật toán riêng
# ══════════════════════════════════════════════════════════════════

def bench_s3_hash(ht_chain, query: str) -> dict:
    """Hash — FAILED: không tìm được theo tên."""
    hash_lookup_by_name(ht_chain, query)   # luôn None
    return {
        "algo":        "Hash lookup",
        "ms":          None,
        "match_count": 0,
        "matches":     [],
        "failed":      True,
    }


def bench_s3_fuzzy(records: list, query: str) -> dict:
    """Fuzzy Linear Search — normalize + substring match."""
    ms         = _avg_ms(lambda: measure_fuzzy(records, query))
    matches, _ = measure_fuzzy(records, query)
    return {
        "algo":        "Fuzzy Linear Search",
        "ms":          ms,
        "match_count": len(matches),
        "matches":     matches,
        "failed":      False,
    }
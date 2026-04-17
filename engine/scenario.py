# engine/scenario.py
"""
Scenario Layer — ráp logic đầy đủ từng thuật toán trong từng scenario.

Nhiệm vụ:
    - Kết hợp primitive (linear, binary, hash) thành logic hoàn chỉnh
    - Gọi benchmark._avg_ms / _once_ms để đo thời gian
    - Trả về dict chuẩn để web.py chuyển lên client

Không biết request đến từ đâu — đó là việc của web.py.
Không implement thuật toán — đó là việc của linear.py, binary.py, collision/.
Không tự đo thời gian — đó là việc của benchmark.py.
"""

from engine.benchmark import _avg_ms, _once_ms
from engine.linear import (
    linear_search,
    linear_filter_dept_gpa,
    linear_filter_gpa,
)
from engine.binary import (
    binary_search,
    binary_filter_dept_gpa,
    binary_filter_gpa,
    sort_by_id,
    sort_by_gpa,
)
from engine.fuzzy_search import fuzzy_linear_search


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 1 — Tra cứu theo MSSV
# ══════════════════════════════════════════════════════════════════

def bench_s1_chain(ht, target_id: str) -> dict:
    ms, found = _avg_ms(lambda: ht.search(target_id))
    return {"algo": "Hash Chaining", "ms": ms, "sort_ms": None, "found": found, "failed": False}


def bench_s1_open(ht, target_id: str) -> dict:
    ms, found = _avg_ms(lambda: ht.search(target_id))
    return {"algo": "Hash Open Addr.", "ms": ms, "sort_ms": None, "found": found, "failed": False}


def bench_s1_linear(records: list, target_id: str) -> dict:
    ms, found = _avg_ms(lambda: linear_search(records, target_id))
    return {"algo": "Linear Search", "ms": ms, "sort_ms": None, "found": found, "failed": False}


def bench_s1_binary(records: list, target_id: str) -> dict:
    sort_ms, sorted_records = _once_ms(lambda: sort_by_id(records))

    ms, found = _avg_ms(lambda: binary_search(sorted_records, target_id))
    return {"algo": "Binary Search", "ms": ms, "sort_ms": sort_ms, "found": found, "failed": False}


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 2A — Lọc GPA + Department
# ══════════════════════════════════════════════════════════════════

def bench_s2a_chain(ht, department: str, min_gpa: float, max_gpa: float) -> dict:
    def _run():
        bucket = ht.search(department)
        return [r for r in bucket if min_gpa <= r["gpa"] <= max_gpa]

    ms, matches = _avg_ms(_run)
    return {"algo": "Hash Chaining", "ms": ms, "sort_ms": None, "match_count": len(matches), "matches": matches, "failed": False}


def bench_s2a_open(ht, department: str, min_gpa: float, max_gpa: float) -> dict:
    def _run():
        bucket = ht.search(department)
        return [r for r in bucket if min_gpa <= r["gpa"] <= max_gpa]

    ms, matches = _avg_ms(_run)
    return {"algo": "Open Addr. Hash", "ms": ms, "sort_ms": None, "match_count": len(matches), "matches": matches, "failed": False}


def bench_s2a_linear(records: list, department: str, min_gpa: float, max_gpa: float) -> dict:
    ms, matches = _avg_ms(lambda: linear_filter_dept_gpa(records, department, min_gpa, max_gpa))
    return {"algo": "Linear Scan", "ms": ms, "sort_ms": None, "match_count": len(matches), "matches": matches, "failed": False}


def bench_s2a_binary(records: list, department: str, min_gpa: float, max_gpa: float) -> dict:
    sort_ms, (sorted_by_gpa, gpa_keys) = _once_ms(lambda: sort_by_gpa(records))

    ms, matches = _avg_ms(lambda: binary_filter_dept_gpa(sorted_by_gpa, gpa_keys, department, min_gpa, max_gpa))
    return {"algo": "Binary Filter", "ms": ms, "sort_ms": sort_ms, "match_count": len(matches), "matches": matches, "failed": False}


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 2B — Lọc khoảng GPA thuần
# ══════════════════════════════════════════════════════════════════

def bench_s2b_chain(ht, min_gpa: float, max_gpa: float) -> dict:
    def _run():
        results = []
        for gpa_int in range(int(round(min_gpa * 100)), int(round(max_gpa * 100)) + 1):
            results.extend(ht.search(str(round(gpa_int / 100, 2))))
        return results

    ms, matches = _avg_ms(_run)
    return {"algo": "Hash Chaining", "ms": ms, "sort_ms": None, "match_count": len(matches), "matches": matches, "failed": False}


def bench_s2b_open(ht, min_gpa: float, max_gpa: float) -> dict:
    def _run():
        results = []
        for gpa_int in range(int(round(min_gpa * 100)), int(round(max_gpa * 100)) + 1):
            results.extend(ht.search(str(round(gpa_int / 100, 2))))
        return results

    ms, matches = _avg_ms(_run)
    return {"algo": "Open Addr. Hash", "ms": ms, "sort_ms": None, "match_count": len(matches), "matches": matches, "failed": False}


def bench_s2b_linear(records: list, min_gpa: float, max_gpa: float) -> dict:
    ms, matches = _avg_ms(lambda: linear_filter_gpa(records, min_gpa, max_gpa))
    return {"algo": "Linear Scan", "ms": ms, "sort_ms": None, "match_count": len(matches), "matches": matches, "failed": False}


def bench_s2b_binary(records: list, min_gpa: float, max_gpa: float) -> dict:
    sort_ms, (sorted_by_gpa, gpa_keys) = _once_ms(lambda: sort_by_gpa(records))

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
    return {"algo": "Inverted Index", "ms": ms, "match_count": len(matches), "matches": matches, "failed": False}
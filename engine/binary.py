# engine/binary.py
"""
Các thuật toán Binary Search — primitive rời rạc, thuần tính toán.
Bao gồm bisect helpers và sort helpers phục vụ binary search.
Không đo thời gian, không gọi nhau theo scenario.
"""


# ══════════════════════════════════════════════════════════════════
#  Bisect helpers
# ══════════════════════════════════════════════════════════════════

def _bisect_left(keys: list, target: float) -> int:
    """
    Tìm index ĐẦU TIÊN có keys[i] >= target.
    → Pattern B: first True với condition = (keys[mid] >= target)
    Complexity: O(log n)
    """
    left, right = 0, len(keys) - 1
    while left <= right:
        mid = (left + right) // 2
        if keys[mid] >= target:
            right = mid - 1
        else:
            left = mid + 1
    return left


def _bisect_right(keys: list, target: float) -> int:
    """
    Tìm index CUỐI CÙNG có keys[i] <= target, trả về right + 1.
    → Pattern C: last True với condition = (keys[mid] <= target)
    Complexity: O(log n)
    """
    left, right = 0, len(keys) - 1
    while left <= right:
        mid = (left + right) // 2
        if keys[mid] <= target:
            left = mid + 1
        else:
            right = mid - 1
    return right + 1


# ══════════════════════════════════════════════════════════════════
#  Sort helpers
# ══════════════════════════════════════════════════════════════════

def sort_by_id(records: list) -> list:
    """Sắp xếp theo student_id — chuẩn bị cho Binary Search S1. O(n log n)."""
    return sorted(records, key=lambda r: r["student_id"])


def sort_by_gpa(records: list) -> tuple:
    """Sắp xếp theo GPA, trả về (sorted_records, gpa_keys) — keys precomputed cùng lúc sort."""
    s = sorted(records, key=lambda r: r["gpa"])
    return s, [r["gpa"] for r in s]


# ══════════════════════════════════════════════════════════════════
#  S1 — Tìm 1 record theo student_id
# ══════════════════════════════════════════════════════════════════

def binary_search(sorted_records: list, target_id: str):
    """
    Tìm kiếm nhị phân trên danh sách ĐÃ SORT theo student_id.
    Complexity: O(log n) — không bao gồm sort.
    """
    lo, hi = 0, len(sorted_records) - 1
    while lo <= hi:
        mid    = (lo + hi) // 2
        mid_id = sorted_records[mid]["student_id"]
        if mid_id == target_id:
            return sorted_records[mid]
        elif mid_id < target_id:
            lo = mid + 1
        else:
            hi = mid - 1
    return None


# ══════════════════════════════════════════════════════════════════
#  S2 — Lọc theo khoảng GPA
# ══════════════════════════════════════════════════════════════════

def binary_filter_dept_gpa(sorted_by_gpa: list, gpa_keys: list, department: str, min_gpa: float, max_gpa: float) -> list:
    """Bisect lấy range GPA, lọc thêm theo department. Complexity: O(log n + k)."""
    lo = _bisect_left(gpa_keys, min_gpa)
    hi = _bisect_right(gpa_keys, max_gpa)
    return [r for r in sorted_by_gpa[lo:hi] if r["department_code"] == department]


def binary_filter_gpa(sorted_by_gpa: list, gpa_keys: list, min_gpa: float, max_gpa: float) -> list:
    """Bisect lấy range GPA thuần. Complexity: O(log n + k)."""
    lo = _bisect_left(gpa_keys, min_gpa)
    hi = _bisect_right(gpa_keys, max_gpa)
    return sorted_by_gpa[lo:hi]

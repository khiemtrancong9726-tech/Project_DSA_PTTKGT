# engine/search.py
"""
Linear Search, Binary Search và Filter — thuần thuật toán.

Nguyên tắc thiết kế:
- Mỗi hàm CHỈ làm 1 việc: tìm kiếm / sắp xếp / lọc.
- Không đo thời gian ở đây — đó là việc của benchmark.py.
- Trả về kết quả thuần, không trả tuple (result, elapsed).
"""

import bisect


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 1 — Tra cứu 1 sinh viên theo MSSV
# ══════════════════════════════════════════════════════════════════

def linear_search(records: list, target_id: str):
    """
    Duyệt tuần tự, so sánh từng student_id.

    Complexity : O(n)
    Không cần chuẩn bị trước (unsorted list OK).
    """
    for record in records:
        if record["student_id"] == target_id:
            return record
    return None


def binary_search(sorted_records: list, target_id: str):
    """
    Tìm kiếm nhị phân trên danh sách ĐÃ SORT theo student_id.

    Complexity : O(log n) — không bao gồm sort.
    Caller phải đảm bảo sorted_records đã được sort theo student_id.
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
#  SCENARIO 2 — Lọc theo GPA / Department
# ══════════════════════════════════════════════════════════════════

def linear_filter_dept_gpa(records: list, department: str, min_gpa: float, max_gpa: float) -> list:
    """Duyệt toàn bộ, lọc theo department và khoảng GPA. Complexity: O(n)."""
    return [
        r for r in records
        if r["department_code"] == department and min_gpa <= r["gpa"] <= max_gpa
    ]


def linear_filter_gpa(records: list, min_gpa: float, max_gpa: float) -> list:
    """Duyệt toàn bộ, lọc theo khoảng GPA. Complexity: O(n)."""
    return [r for r in records if min_gpa <= r["gpa"] <= max_gpa]


def binary_filter_dept_gpa(sorted_by_gpa: list, department: str, min_gpa: float, max_gpa: float) -> list:
    """
    Dùng bisect tìm khoảng [min_gpa, max_gpa] trên list ĐÃ SORT theo GPA,
    sau đó lọc thêm theo department. Complexity: O(log n + k).
    """
    gpa_keys = [r["gpa"] for r in sorted_by_gpa]
    lo = bisect.bisect_left(gpa_keys, min_gpa)
    hi = bisect.bisect_right(gpa_keys, max_gpa)
    return [r for r in sorted_by_gpa[lo:hi] if r["department_code"] == department]


def binary_filter_gpa(sorted_by_gpa: list, min_gpa: float, max_gpa: float) -> list:
    """
    Dùng bisect tìm khoảng [min_gpa, max_gpa] trên list ĐÃ SORT theo GPA.
    Complexity: O(log n + k).
    """
    gpa_keys = [r["gpa"] for r in sorted_by_gpa]
    lo = bisect.bisect_left(gpa_keys, min_gpa)
    hi = bisect.bisect_right(gpa_keys, max_gpa)
    return sorted_by_gpa[lo:hi]


# ══════════════════════════════════════════════════════════════════
#  Sort helpers
# ══════════════════════════════════════════════════════════════════

def sort_by_id(records: list) -> list:
    """Sắp xếp theo student_id — chuẩn bị cho Binary Search. O(n log n)."""
    return sorted(records, key=lambda r: r["student_id"])


def sort_by_gpa(records: list) -> list:
    """Sắp xếp theo GPA tăng dần — chuẩn bị cho Binary Filter. O(n log n)."""
    return sorted(records, key=lambda r: r["gpa"])
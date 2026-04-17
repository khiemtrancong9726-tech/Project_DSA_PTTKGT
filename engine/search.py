# engine/search.py
"""
Linear Search, Binary Search và Filter — thuần thuật toán.

Nguyên tắc thiết kế:
- Mỗi hàm CHỈ làm 1 việc: tìm kiếm / sắp xếp / lọc.
- Không đo thời gian ở đây — đó là việc của benchmark.py.
- Trả về kết quả thuần, không trả tuple (result, elapsed).
"""

# ══════════════════════════════════════════════════════════════════
#  Binary search helpers — thay thế định nghĩa bisect_left / bisect_right
#  Viết theo 3 pattern chuẩn
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

        if keys[mid] >= target:   # condition True → còn tìm tiếp bên trái
            right = mid - 1
        else:
            left = mid + 1

    return left   # vị trí đầu tiên thỏa condition


def _bisect_right(keys: list, target: float) -> int:
    """
    Tìm index CUỐI CÙNG có keys[i] <= target, rồi trả về right + 1.
    → Pattern C: last True với condition = (keys[mid] <= target)

    Slice [bisect_left : bisect_right] cho đúng range [min_gpa, max_gpa] inclusive.

    Complexity: O(log n)
    """
    left, right = 0, len(keys) - 1

    while left <= right:
        mid = (left + right) // 2

        if keys[mid] <= target:   # condition True → còn tìm tiếp bên phải
            left = mid + 1
        else:
            right = mid - 1

    return right + 1   # right = index cuối cùng thỏa condition → +1 để làm exclusive bound


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


def binary_filter_dept_gpa(sorted_by_gpa: list, gpa_keys: list, department: str, min_gpa: float, max_gpa: float) -> list:
    lo = _bisect_left(gpa_keys, min_gpa)
    hi = _bisect_right(gpa_keys, max_gpa)
    return [r for r in sorted_by_gpa[lo:hi] if r["department_code"] == department]


def binary_filter_gpa(sorted_by_gpa: list, gpa_keys: list, min_gpa: float, max_gpa: float) -> list:
    lo = _bisect_left(gpa_keys, min_gpa)
    hi = _bisect_right(gpa_keys, max_gpa)
    return sorted_by_gpa[lo:hi]


# ══════════════════════════════════════════════════════════════════
#  Sort helpers
# ══════════════════════════════════════════════════════════════════

def sort_by_id(records: list) -> list:
    """Sắp xếp theo student_id — chuẩn bị cho Binary Search. O(n log n)."""
    return sorted(records, key=lambda r: r["student_id"])


def sort_by_gpa(records: list) -> tuple:
    """Sắp xếp theo GPA, trả về (sorted_records, gpa_keys) — keys precomputed cùng lúc sort."""
    s = sorted(records, key=lambda r: r["gpa"])
    return s, [r["gpa"] for r in s]
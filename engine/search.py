# engine/search.py
"""
Cung cấp Linear Search và Binary Search để benchmark.py so sánh với Hash Table.

Nguyên tắc thiết kế:
- Mỗi hàm trả về (kết_quả, elapsed_ms) — caller không cần tự đo thời gian.
- Sort time được tách riêng, KHÔNG gộp vào search time ngầm.
  → benchmark.py có thể in "sort: Xms + search: Yms = tổng Zms" một cách minh bạch.
- Đây là chi phí ẩn mà nhiều người bỏ qua khi nói "Binary Search O(log n)".
"""

import time
import bisect


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 1 — Tra cứu 1 sinh viên theo MSSV
# ══════════════════════════════════════════════════════════════════

def linear_search(records: list, target_id: str) -> tuple:
    """
    Duyệt tuần tự từ đầu đến cuối danh sách, so sánh từng student_id.

    Complexity : O(n)
    Không cần chuẩn bị trước (unsorted list OK).

    Args:
        records   : list[dict] — danh sách sinh viên chưa sort
        target_id : str        — MSSV cần tìm

    Returns:
        (record | None, elapsed_ms)
        record     — dict sinh viên nếu tìm thấy, None nếu không có
        elapsed_ms — thời gian tìm kiếm (không tính thời gian chuẩn bị)
    """
    start = time.perf_counter()

    result = None
    for record in records:
        if record["student_id"] == target_id:
            result = record
            break

    elapsed = (time.perf_counter() - start) * 1000
    return result, elapsed


def sort_by_id(records: list) -> tuple:
    """
    Sắp xếp danh sách theo student_id — bước bắt buộc trước Binary Search.

    Complexity : O(n log n) — Python dùng Timsort
    Trả list MỚI, không sort in-place — giữ nguyên records gốc cho các lần đo tiếp theo.

    Args:
        records : list[dict] — danh sách gốc chưa sort

    Returns:
        (sorted_records, sort_ms)
        sorted_records — list mới đã sort theo student_id
        sort_ms        — thời gian sort (phải tính vào tổng chi phí Binary Search)
    """
    start = time.perf_counter()

    sorted_records = sorted(records, key=lambda r: r["student_id"])

    sort_ms = (time.perf_counter() - start) * 1000
    return sorted_records, sort_ms


def binary_search(sorted_records: list, target_id: str) -> tuple:
    """
    Tìm kiếm nhị phân trên danh sách ĐÃ SORT theo student_id.

    Complexity : O(log n) — chỉ tính bước tìm kiếm, KHÔNG bao gồm sort.
    Để có tổng chi phí thực tế: cộng thêm sort_ms từ sort_by_id().

    Args:
        sorted_records : list[dict] — danh sách ĐÃ sort theo student_id
        target_id      : str        — MSSV cần tìm

    Returns:
        (record | None, search_ms)
        record    — dict sinh viên nếu tìm thấy, None nếu không có
        search_ms — thời gian tìm kiếm thuần (chưa bao gồm sort)
    """
    start = time.perf_counter()

    lo, hi = 0, len(sorted_records) - 1
    result = None

    while lo <= hi:
        mid = (lo + hi) // 2
        mid_id = sorted_records[mid]["student_id"]

        if mid_id == target_id:
            result = sorted_records[mid]
            break
        elif mid_id < target_id:
            lo = mid + 1
        else:
            hi = mid - 1

    search_ms = (time.perf_counter() - start) * 1000
    return result, search_ms


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 2 — Lọc đa điều kiện (department + GPA)
# ══════════════════════════════════════════════════════════════════

def sort_by_gpa(records: list) -> tuple:
    """
    Sắp xếp danh sách theo GPA tăng dần — bước chuẩn bị cho binary filter.

    Returns:
        (sorted_records, sort_ms)
    """
    start = time.perf_counter()

    sorted_records = sorted(records, key=lambda r: r["gpa"])

    sort_ms = (time.perf_counter() - start) * 1000
    return sorted_records, sort_ms
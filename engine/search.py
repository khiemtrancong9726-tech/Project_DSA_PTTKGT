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

    Cơ chế:
        So sánh target_id với phần tử giữa.
        Nếu target < mid → tìm nửa trái.
        Nếu target > mid → tìm nửa phải.
        Lặp đến khi tìm thấy hoặc khoảng rỗng.

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


def binary_search_full(records: list, target_id: str) -> tuple:
    """
    Gộp sort + binary search — đo tổng chi phí thực tế.

    Đây là hàm benchmark.py dùng để in ra con số "honest":
    Binary Search thực tế tốn bao nhiêu nếu data chưa sort sẵn.

    Args:
        records   : list[dict] — danh sách gốc (chưa sort)
        target_id : str        — MSSV cần tìm

    Returns:
        (record | None, sort_ms, search_ms)
        sort_ms + search_ms = tổng chi phí thực tế
    """
    sorted_records, sort_ms   = sort_by_id(records)
    result,         search_ms = binary_search(sorted_records, target_id)
    return result, sort_ms, search_ms


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 2 — Lọc đa điều kiện (department + min_gpa)
# ══════════════════════════════════════════════════════════════════

def linear_filter(records: list, department: str, min_gpa: float) -> tuple:
    """
    Duyệt toàn bộ danh sách, giữ lại record thỏa mãn CẢ HAI điều kiện.

    Complexity : O(n) — không tránh khỏi, phải xem qua từng record.

    Args:
        records    : list[dict] — danh sách gốc
        department : str        — mã khoa cần lọc (vd: "CNTT")
        min_gpa    : float      — ngưỡng GPA tối thiểu (vd: 3.5)

    Returns:
        (matches, elapsed_ms)
        matches    — list[dict] các sinh viên thỏa mãn điều kiện
        elapsed_ms — thời gian thực thi
    """
    start = time.perf_counter()

    matches = [
        r for r in records
        if r["department_code"] == department and r["gpa"] >= min_gpa
    ]

    elapsed = (time.perf_counter() - start) * 1000
    return matches, elapsed


def sort_by_gpa(records: list) -> tuple:
    """
    Sắp xếp danh sách theo GPA tăng dần — bước chuẩn bị cho binary_filter.

    Returns:
        (sorted_records, sort_ms)
    """
    start = time.perf_counter()

    sorted_records = sorted(records, key=lambda r: r["gpa"])

    sort_ms = (time.perf_counter() - start) * 1000
    return sorted_records, sort_ms


def binary_filter(records: list, department: str, min_gpa: float) -> tuple:
    """
    Sort theo GPA → dùng bisect tìm điểm bắt đầu ≥ min_gpa → scan từ đó,
    filter thêm theo department.

    Insight:
        Không O(1) — nhưng không cần scan toàn bộ n records.
        Bắt đầu scan từ vị trí bisect → chỉ duyệt phần đuôi GPA cao.
        Hiệu quả hơn linear_filter khi min_gpa cắt bỏ nhiều record.

    Args:
        records    : list[dict] — danh sách gốc (chưa sort)
        department : str        — mã khoa cần lọc
        min_gpa    : float      — ngưỡng GPA tối thiểu

    Returns:
        (matches, sort_ms, search_ms)
        sort_ms + search_ms = tổng chi phí thực tế
    """
    # Bước 1: sort theo GPA
    sorted_by_gpa, sort_ms = sort_by_gpa(records)

    # Bước 2: dùng bisect tìm chỉ số đầu tiên có GPA >= min_gpa
    start = time.perf_counter()

    gpa_keys   = [r["gpa"] for r in sorted_by_gpa]
    start_idx  = bisect.bisect_left(gpa_keys, min_gpa)

    # Bước 3: scan từ start_idx đến cuối, filter thêm department
    matches = [
        r for r in sorted_by_gpa[start_idx:]
        if r["department_code"] == department
    ]

    search_ms = (time.perf_counter() - start) * 1000
    return matches, sort_ms, search_ms
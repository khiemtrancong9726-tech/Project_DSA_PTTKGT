# engine/fuzzy_search.py
"""
Tìm kiếm theo tên mơ hồ — Scenario 4.

Bài toán: Giảng viên nhớ mang máng "thằng sinh viên tên An, học CNTT"
          nhưng không có MSSV → Hash Table vô dụng hoàn toàn.

Hash Table chỉ match chính xác theo key (student_id).
Tên thì không unique, không chính xác, còn có dấu tiếng Việt.
→ Giải pháp duy nhất khả thi: fuzzy linear search O(n).

Điểm kỹ thuật cốt lõi:
    normalize() — bỏ dấu tiếng Việt trước khi so sánh.
    "Văn An" và "van an" phải match nhau — không thì miss toàn bộ.
"""

import time
import unicodedata


# ══════════════════════════════════════════════════════════════════
#  Normalize — xử lý dấu tiếng Việt
# ══════════════════════════════════════════════════════════════════

def normalize(text: str) -> str:
    """
    Lowercase + bỏ dấu tiếng Việt để so sánh không phân biệt dấu.

    Cơ chế:
        NFKD decomposition tách ký tự có dấu thành 2 phần:
            ký tự gốc  +  combining diacritic (dấu)
        Sau đó lọc bỏ toàn bộ combining character → chỉ giữ ký tự gốc.

    Ví dụ:
        "Nguyễn Văn An" → "nguyen van an"
        "Thị"           → "thi"
        "Đức"           → "duc"

    Lý do cần normalize:
        Trong Python, "An" != "an" != "ân" vì chúng khác nhau về byte.
        Người dùng gõ "van an" nhưng data lưu "Văn An" → không normalize thì miss.

    Args:
        text : str — chuỗi bất kỳ (có hoặc không có dấu)

    Returns:
        str — chuỗi đã lowercase và bỏ dấu
    """
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# ══════════════════════════════════════════════════════════════════
#  Fuzzy linear search
# ══════════════════════════════════════════════════════════════════

def fuzzy_linear_search(records: list, query: str) -> list:
    """
    Tìm tất cả sinh viên có query xuất hiện trong name (substring match).
    Không phân biệt dấu, không phân biệt hoa thường.

    Cơ chế:
        normalize(query) ⊆ normalize(record["name"])
        → dùng Python `in` operator — O(m) mỗi lần, m = len(query)
        → tổng O(n × m) — n records, m độ dài query

    Trong thực tế m rất nhỏ (≤ 20 ký tự) → coi gần như O(n).

    Args:
        records : list[dict] — danh sách sinh viên
        query   : str        — chuỗi tìm kiếm (có thể có dấu hoặc không)

    Returns:
        list[dict] — các record có name chứa query (sau normalize)
                     list rỗng nếu không tìm thấy
    """
    q = normalize(query)
    return [r for r in records if q in normalize(r["name"])]


def measure_fuzzy(records: list, query: str) -> tuple:
    """
    Chạy fuzzy_linear_search và đo thời gian thực thi.

    Args:
        records : list[dict]
        query   : str

    Returns:
        (matches, elapsed_ms)
        matches    — list[dict] các record tìm được
        elapsed_ms — thời gian thực thi tính bằng millisecond
    """
    start   = time.perf_counter()
    matches = fuzzy_linear_search(records, query)
    elapsed = (time.perf_counter() - start) * 1000
    return matches, elapsed


# ══════════════════════════════════════════════════════════════════
#  Demo Hash Table thất bại — dùng trong Scenario 4 CLI
# ══════════════════════════════════════════════════════════════════

def hash_lookup_by_name(hash_table, query: str):
    """
    Thử dùng Hash Table để tìm theo tên — luôn trả về None.

    Hash Table chỉ lookup được bằng student_id (key chính xác).
    Truyền tên vào → hash function tính ra index → bucket đó không có gì
    hoặc có record khác → miss hoàn toàn.

    Hàm này tồn tại để CLI in dòng FAILED cạnh kết quả fuzzy search —
    không phải để dùng thực tế.

    Args:
        hash_table : HashTable — bảng đã load dữ liệu (key = student_id)
        query      : str       — tên cần tìm (không phải MSSV)

    Returns:
        None — luôn luôn
    """
    return hash_table.search(query)   # → None, key không khớp với student_id


# ══════════════════════════════════════════════════════════════════
#  Filter bổ sung sau fuzzy search
# ══════════════════════════════════════════════════════════════════

def fuzzy_search_with_filter(
    records:    list,
    query:      str,
    department: str   = None,
    min_gpa:    float = None,
) -> tuple:
    """
    Fuzzy search theo tên, sau đó filter thêm theo department và/hoặc GPA.

    Phục vụ trường hợp thực tế:
        "thằng sinh viên tên An, học CNTT, GPA thấp lắm"
        → query="An", department="CNTT", min_gpa=None (hoặc max_gpa)

    Thứ tự thực hiện:
        1. fuzzy_linear_search → thu hẹp theo tên    (O(n))
        2. filter department   → thu hẹp theo khoa   (O(k), k << n)
        3. filter min_gpa      → thu hẹp theo GPA    (O(k))

    Bước 1 luôn chạy trước — giảm k xuống nhỏ trước khi filter thêm.

    Args:
        records    : list[dict]
        query      : str        — chuỗi tên cần tìm
        department : str | None — mã khoa (None = không filter)
        min_gpa    : float|None — ngưỡng GPA tối thiểu (None = không filter)

    Returns:
        (matches, elapsed_ms)
        matches    — list[dict] sau tất cả các bước filter
        elapsed_ms — tổng thời gian thực thi
    """
    start = time.perf_counter()

    # Bước 1: fuzzy match theo tên
    matches = fuzzy_linear_search(records, query)

    # Bước 2: filter department nếu có
    if department is not None:
        matches = [r for r in matches if r["department_code"] == department]

    # Bước 3: filter GPA nếu có
    if min_gpa is not None:
        matches = [r for r in matches if r["gpa"] >= min_gpa]

    elapsed = (time.perf_counter() - start) * 1000
    return matches, elapsed
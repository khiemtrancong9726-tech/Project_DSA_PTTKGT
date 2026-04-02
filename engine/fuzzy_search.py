# engine/fuzzy_search.py
"""
Tìm kiếm theo tên mơ hồ — Scenario 3.

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

    Complexity : O(n × m) — n records, m độ dài query.
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
#  Demo Hash Table thất bại — dùng trong Scenario 3 CLI
# ══════════════════════════════════════════════════════════════════

def hash_lookup_by_name(hash_table, query: str):
    """
    Thử dùng Hash Table để tìm theo tên — luôn trả về None.

    Hash Table chỉ lookup được bằng student_id (key chính xác).
    Truyền tên vào → hash function tính ra index → miss hoàn toàn.

    Hàm này tồn tại để CLI in dòng FAILED cạnh kết quả fuzzy search —
    không phải để dùng thực tế.

    Args:
        hash_table : HashTable — bảng đã load dữ liệu (key = student_id)
        query      : str       — tên cần tìm (không phải MSSV)

    Returns:
        None — luôn luôn
    """
    return hash_table.search(query)   # → None, key không khớp với student_id
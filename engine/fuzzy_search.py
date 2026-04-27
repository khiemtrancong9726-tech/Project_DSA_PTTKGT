# engine/fuzzy_search.py
"""
Tìm kiếm theo tên mơ hồ — Scenario 3.

Hash Table chỉ match chính xác theo key (student_id).
Tên thì không unique, không chính xác.
→ Giải pháp duy nhất khả thi: fuzzy linear search O(n).

Điểm kỹ thuật cốt lõi:
    normalize() — bỏ dấu tiếng Việt trước khi so sánh.
    "Văn An" và "van an" phải match nhau — không thì miss toàn bộ.
"""


# ══════════════════════════════════════════════════════════════════
#  Normalize — chỉ lowercase, không bỏ dấu
# ══════════════════════════════════════════════════════════════════

def normalize(text: str) -> str:
    return text.lower()   # chỉ lowercase


# ══════════════════════════════════════════════════════════════════
#  Fuzzy linear search
# ══════════════════════════════════════════════════════════════════

def fuzzy_linear_search(records: list, query: str) -> list:
    tokens = normalize(query).split()   # ["an", "văn"]

    def match(name: str) -> bool:
        name_tokens = set(normalize(name).split())  # {"phan", "văn", "an"}
        return all(t in name_tokens for t in tokens)

    return [r for r in records if match(r["name"])]
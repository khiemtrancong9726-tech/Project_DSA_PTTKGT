# engine/linear.py
"""
Các thuật toán Linear — primitive rời rạc, thuần tính toán.
Không đo thời gian, không gọi nhau theo scenario.
"""


# ══════════════════════════════════════════════════════════════════
#  S1 — Tìm 1 record theo student_id
# ══════════════════════════════════════════════════════════════════

def linear_search(records: list, target_id: str):
    """Duyệt tuần tự so sánh student_id. Complexity: O(n)."""
    for record in records:
        if record["student_id"] == target_id:
            return record
    return None


# ══════════════════════════════════════════════════════════════════
#  S2 — Lọc theo điều kiện
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

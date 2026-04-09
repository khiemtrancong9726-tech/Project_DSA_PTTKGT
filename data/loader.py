# data/loader.py
"""
Layer 1 — chuẩn bị dữ liệu cho engine.

Gồm 3 nhóm chức năng:
    1. load_xlsx         — đọc file xlsx, trả về list[dict]
    2. build_hash_tables — khởi tạo Chaining và Open Addressing từ records
    3. sample_id         — lấy student_id mẫu để benchmark reproducible

Schema đọc ra — 7 cột:
    student_id      : str   (giữ nguyên string — leading zero quan trọng)
    name            : str
    gpa             : float
    department_code : str
    province_name   : str
    gender          : str
    birth_year      : int
"""

import pandas as pd
from pathlib import Path


# ══════════════════════════════════════════════════════════════════
#  1. Load file xlsx → list[dict]
# ══════════════════════════════════════════════════════════════════

def load_xlsx(filepath: str | Path) -> list:
    """
    Đọc file xlsx, trả về list[dict] — mỗi dict là 1 sinh viên.

    student_id đọc ra kiểu str — KHÔNG để pandas tự convert sang int
    vì CCCD có leading zero (079...) sẽ bị mất.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {path}")

    df = pd.read_excel(
        path,
        dtype={"student_id": str},  # giữ leading zero
        engine="openpyxl",
    )

    _validate_columns(df, path)

    df["gpa"]        = df["gpa"].astype(float).round(2)
    df["birth_year"] = df["birth_year"].astype(int)

    return df.to_dict(orient="records")


def _validate_columns(df: "pd.DataFrame", path: Path):
    required = {
        "student_id", "name", "gpa",
        "department_code", "province_name", "gender", "birth_year",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"File {path.name} thiếu cột: {', '.join(sorted(missing))}"
        )


# ══════════════════════════════════════════════════════════════════
#  2. Build hash tables từ records
# ══════════════════════════════════════════════════════════════════

def build_hash_tables(records: list, load_factor: float = 0.5) -> tuple:
    from engine.collision.chaining        import ChainingHashTable
    from engine.collision.open_addressing import OpenAddressingHashTable

    size     = _next_prime(int(len(records) / load_factor))
    ht_chain = ChainingHashTable(size=size)
    ht_open  = OpenAddressingHashTable(size=size)

    for r in records:
        key = r["student_id"]
        ht_chain.insert(key, r)
        ht_open.insert(key, r)

    return ht_chain, ht_open


def _next_prime(n: int) -> int:
    def is_prime(x):
        if x < 2:
            return False
        for i in range(2, int(x**0.5) + 1):
            if x % i == 0:
                return False
        return True

    while not is_prime(n):
        n += 1
    return n


# ══════════════════════════════════════════════════════════════════
#  3. Tiện ích benchmark
# ══════════════════════════════════════════════════════════════════

def sample_id(records: list, index: int = 500) -> str:
    """Lấy student_id tại vị trí index — reproducible, tránh best-case (index=0)."""
    return records[min(index, len(records) - 1)]["student_id"]
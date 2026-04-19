# data/loader.py
"""
Layer 1 — chuẩn bị dữ liệu cho engine.

Gồm 3 nhóm chức năng:
    1. load_xlsx         — đọc file xlsx, trả về list[dict]
    2. build_hash_tables — khởi tạo Chaining, Open Addressing và Dept Index từ records
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

    _validate_columns(df, path)  # check đọc đủ các cột trong file xlsx

    df["gpa"]        = df["gpa"].astype(float).round(2)
    df["birth_year"] = df["birth_year"].astype(int)

    return df.to_dict(orient="records")


# Hàm check đọc đủ các cột trong file xlsx:
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
    from engine.collision.chaining                   import ChainingHashTable
    from engine.collision.open_addressing            import OpenAddressingHashTable
    from engine.collision.chaining_multi             import ChainingMultiHashTable
    from engine.collision.open_addressing_multi      import OpenAddressingMultiHashTable
    from engine.inverted_index                       import InvertedIndex  # thêm

    # S1 — hash theo student_id
    size_s1     = _next_prime(int(len(records) / load_factor))
    ht_chain_s1 = ChainingHashTable(size=size_s1)
    ht_open_s1  = OpenAddressingHashTable(size=size_s1)

    # S2A — hash theo department_code (5 khoa cố định → size nhỏ)
    ht_chain_s2a  = ChainingMultiHashTable(size=11)
    ht_open_s2a   = OpenAddressingMultiHashTable(size=11)

    # S2B — hash theo gpa thuần
    ht_chain_s2b = ChainingMultiHashTable(size=809)   # next_prime(401 * 2) — 401 GPA unique cố định
    ht_open_s2b  = OpenAddressingMultiHashTable(size=809)

    for r in records:
        ht_chain_s1.insert(r["student_id"], r)
        ht_open_s1.insert(r["student_id"], r)

        ht_chain_s2a.insert(r["department_code"], r)
        ht_open_s2a.insert(r["department_code"], r)

        ht_chain_s2b.insert(str(r['gpa']), r)
        ht_open_s2b.insert(str(r['gpa']), r)
    
    # S3 — inverted index
    inv_index_s3 = InvertedIndex(size=97)             # next_prime(48 * 2)  — 48 token unique cố định
    inv_index_s3.build(records)  # thêm — build sau khi load xong

    return ht_chain_s1, ht_open_s1, ht_chain_s2a, ht_open_s2a, ht_chain_s2b, ht_open_s2b, inv_index_s3


# Hàm lấy số nguyên tố gần nhất:
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

# data/loader.py
"""
Layer 1 — đọc file xlsx, trả về list[dict] chuẩn cho engine dùng.

Nhiệm vụ duy nhất: I/O và type conversion.
Không có logic thuật toán ở đây — đúng Separation of Concerns.

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
#  Load file xlsx → list[dict]
# ══════════════════════════════════════════════════════════════════

def load_xlsx(filepath: str | Path) -> list:
    """
    Đọc file xlsx, trả về list[dict] — mỗi dict là 1 sinh viên.

    student_id đọc ra kiểu str — KHÔNG để pandas tự convert sang int
    vì CCCD có leading zero (079...) sẽ bị mất.

    Args:
        filepath : str | Path — đường dẫn đến file xlsx

    Returns:
        list[dict] — mỗi dict có đúng 7 key theo schema ở trên

    Raises:
        FileNotFoundError — nếu file không tồn tại
        ValueError        — nếu file thiếu cột bắt buộc
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {path}")

    # dtype=str cho student_id — giữ leading zero
    df = pd.read_excel(
        path,
        dtype={"student_id": str},
        engine="openpyxl",
    )

    _validate_columns(df, path)

    # Ép kiểu rõ ràng — không tin pandas tự infer
    df["gpa"]        = df["gpa"].astype(float).round(2)
    df["birth_year"] = df["birth_year"].astype(int)

    return df.to_dict(orient="records")


def _validate_columns(df: "pd.DataFrame", path: Path):
    """Kiểm tra đủ 7 cột bắt buộc — raise ValueError nếu thiếu."""
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
#  Load nhiều file cùng lúc
# ══════════════════════════════════════════════════════════════════

def load_all(data_dir: str | Path = "data") -> dict:
    """
    Load cả 3 file dataset, trả về dict theo key kích thước.

    Args:
        data_dir : str | Path — thư mục chứa file xlsx

    Returns:
        dict:
            "1K"  → list[dict] — 1,000 records
            "5K"  → list[dict] — 5,000 records
            "10K" → list[dict] — 10,000 records

    Bỏ qua file nào không tìm thấy — không raise error,
    chỉ in cảnh báo để không crash khi chạy với subset file.
    """
    base = Path(data_dir)
    targets = {
        "1K":  base / "students_1K.xlsx",
        "5K":  base / "students_5K.xlsx",
        "10K": base / "students_10K.xlsx",
    }

    result = {}
    for label, path in targets.items():
        try:
            result[label] = load_xlsx(path)
            print(f"✅ Loaded {label}: {len(result[label]):,} records ← {path.name}")
        except FileNotFoundError:
            print(f"⚠️  Không tìm thấy {path.name} — bỏ qua.")

    return result


# ══════════════════════════════════════════════════════════════════
#  Build hash tables từ records
# ══════════════════════════════════════════════════════════════════

def build_hash_tables(records: list, load_factor: float = 0.5) -> tuple:
    """
    Build ChainingHashTable và OpenAddressingHashTable từ records.

    Table size = n / load_factor → đảm bảo α ≈ load_factor sau khi insert.
    Dùng số nguyên tố gần nhất để giảm collision.

    Args:
        records     : list[dict]
        load_factor : float — load factor mục tiêu (default 0.5)

    Returns:
        (ChainingHashTable, OpenAddressingHashTable)
    """
    from engine.collision.chaining        import ChainingHashTable
    from engine.collision.open_addressing import OpenAddressingHashTable

    n    = len(records)
    size = _next_prime(int(n / load_factor))

    ht_chain = ChainingHashTable(size=size)
    ht_open  = OpenAddressingHashTable(size=size)

    for r in records:
        key = r["student_id"]
        ht_chain.insert(key, r)
        ht_open.insert(key, r)

    return ht_chain, ht_open


def _next_prime(n: int) -> int:
    """Số nguyên tố nhỏ nhất >= n."""
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
#  Tiện ích — lấy 1 student_id ngẫu nhiên để benchmark
# ══════════════════════════════════════════════════════════════════

def sample_id(records: list, index: int = 500) -> str:
    """
    Lấy student_id tại vị trí index — dùng làm target_id cho benchmark.

    Không random để benchmark reproducible giữa các lần chạy.
    Default index=500 → lấy record giữa danh sách, tránh best-case (index=0).

    Args:
        records : list[dict]
        index   : int — vị trí lấy (default 500)

    Returns:
        str — student_id
    """
    idx = min(index, len(records) - 1)
    return records[idx]["student_id"]
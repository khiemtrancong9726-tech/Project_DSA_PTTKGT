# data/generator.py
"""
Sinh dataset sinh viên giả — lưu vào thư mục data/ dưới dạng xlsx.

Cấu trúc CCCD:
    079  2  04  000001
     │   │   │     └── 6 số định danh (unique)
     │   │   └──────── năm sinh (04 → 2004)
     │   └──────────── giới tính (2 = Nam, 3 = Nữ)
     └──────────────── mã tỉnh (079 = TP.HCM)

province_name, gender, birth_year luôn nhất quán với student_id
vì được đọc ngược ra từ chính ID — không thể sai lệch.
"""

import pandas as pd
import random
from pathlib import Path

# ── Output dir — tạo nếu chưa có ──
OUTPUT_DIR = Path(__file__).parent   # cùng thư mục data/
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════════
#  Danh sách tên Việt Nam
# ══════════════════════════════════════════════════════════════════

HO = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh",
    "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô",
]

TEN_DEM = [
    "Văn", "Thị", "Hữu", "Đức", "Minh", "Quốc",
    "Thành", "Bảo", "Xuân", "Thu", "Ngọc", "Kim",
]

TEN = [
    "An", "Bình", "Chi", "Dung", "Phúc",
    "Giang", "Hà", "Hùng", "Khoa", "Lan", "Long",
    "Mai", "Nam", "Oanh", "Phương", "Quân", "Sơn",
    "Tâm", "Thảo", "Uyên", "Vinh", "Yến",
]


def gen_name() -> str:
    """Sinh họ tên ngẫu nhiên theo format: Họ + Tên đệm + Tên."""
    return f"{random.choice(HO)} {random.choice(TEN_DEM)} {random.choice(TEN)}"


# ══════════════════════════════════════════════════════════════════
#  Bảng mã tỉnh và khoa
# ══════════════════════════════════════════════════════════════════

PROVINCE_CODES = {
    "079": "TP. Hồ Chí Minh",
    "080": "Long An",
    "048": "Đà Nẵng",
    "040": "Nghệ An",
    "075": "Đồng Nai",
}

DEPARTMENT_CODES = ["CNTT", "KHDL", "HTTT", "ATTT", "KHMT"]
PROVINCE_LIST    = list(PROVINCE_CODES.keys())


# ══════════════════════════════════════════════════════════════════
#  Sinh và parse CCCD
# ══════════════════════════════════════════════════════════════════

def gen_cccd(so_dinh_danh: int) -> str:
    """
    Sinh mã CCCD 11 ký tự theo cấu trúc:
        [3 mã tỉnh][1 giới tính][2 năm sinh][6 định danh]
    """
    ma_tinh   = random.choice(PROVINCE_LIST)
    gioi_tinh = random.choice(["2", "3"])       # 2 = Nam, 3 = Nữ
    nam_sinh  = str(random.randint(4, 7)).zfill(2)  # 2004 – 2007
    return f"{ma_tinh}{gioi_tinh}{nam_sinh}{str(so_dinh_danh).zfill(6)}"


def parse_cccd(student_id: str) -> dict:
    """
    Đọc ngược cấu trúc CCCD ra các trường riêng.
    Đảm bảo province_name / gender / birth_year luôn nhất quán với student_id.
    """
    province_code = student_id[:3]
    gender_digit  = student_id[3]
    year_suffix   = student_id[4:6]
    return {
        "province_name": PROVINCE_CODES.get(province_code, "Khác"),
        "gender":        "Nam" if gender_digit == "2" else "Nữ",
        "birth_year":    int("20" + year_suffix),
    }


# ══════════════════════════════════════════════════════════════════
#  Sinh dataset
# ══════════════════════════════════════════════════════════════════

def gen_dataset(n: int) -> pd.DataFrame:
    """
    Sinh n bản ghi sinh viên với student_id unique.

    GPA range: [2.0, 4.0].
    student_id: lấy từ pool n số unique trong [0, 999999] → không trùng.

    Args:
        n : int — số bản ghi cần sinh

    Returns:
        pd.DataFrame — n dòng, 7 cột theo schema chuẩn
    """
    pool = random.sample(range(1_000_000), n)   # n số unique
    rows = []

    for _ in range(n):
        sid = gen_cccd(pool.pop())
        rows.append({
            "student_id":      sid,
            "name":            gen_name(),
            "gpa":             round(random.uniform(2.0, 4.0), 2),  # [2.0, 4.0]
            "department_code": random.choice(DEPARTMENT_CODES),
            **parse_cccd(sid),
        })

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════
#  Xuất file
# ══════════════════════════════════════════════════════════════════

TARGETS = [
    (1_000,  "students_1K.xlsx"),
    (5_000,  "students_5K.xlsx"),
    (10_000, "students_10K.xlsx"),
]

if __name__ == "__main__":
    for n, filename in TARGETS:
        df   = gen_dataset(n)
        path = OUTPUT_DIR / filename
        df.to_excel(path, index=False)

        is_unique = df["student_id"].nunique() == len(df)
        status    = "✅" if is_unique else "⚠️  DUPLICATE DETECTED"
        print(f"{status}  {filename} — {len(df):,} dòng — unique IDs: {is_unique}")

    print(f"\n📁 Files saved to: {OUTPUT_DIR.resolve()}")
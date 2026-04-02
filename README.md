# Project_DSA_PTTKGT — Hệ Thống Quản Lý Sinh Viên

So sánh hiệu năng các thuật toán tìm kiếm (Hash Table, Linear Search, Binary Search) trên dataset sinh viên giả lập.

## Tính năng

- **Scenario 1:** Tra cứu sinh viên theo MSSV
- **Scenario 2:** Lọc theo GPA và mã khoa
- **Scenario 3:** Tìm kiếm tên mờ (fuzzy search)
- Dataset: 1K / 5K / 10K records sinh viên

## Cài đặt

### 1. Clone repo
```bash
git clone https://github.com/khiemtrancong9726-tech/Project_DSA_PTTKGT.git
cd Project_DSA_PTTKGT
```

### 2. Tạo môi trường ảo
```bash
python -m venv venv
```

### 3. Kích hoạt môi trường ảo

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Cài thư viện
```bash
pip install -r requirements.txt
```

## Chạy chương trình

### Bước 1 — Sinh dataset
```bash
python data/generator.py
```

### Bước 2 — Chạy chương trình chính
```bash
python main.py
```

## Cấu trúc project
```
Project_DSA_PTTKGT/
├── data/
│   ├── generator.py      # Sinh dataset giả
│   └── loader.py         # Đọc file xlsx, build hash tables
├── engine/
│   ├── hash_table.py     # Base class Hash Table
│   ├── benchmark.py      # Đo thời gian thực thi
│   ├── search.py         # Linear & Binary Search
│   ├── fuzzy_search.py   # Tìm kiếm tên mờ
│   └── collision/
│       ├── chaining.py         # Hash Chaining
│       └── open_addressing.py  # Open Addressing
├── interface/
│   ├── cli.py            # Giao diện dòng lệnh
│   └── display.py        # Render kết quả ra terminal
├── requirements.txt
└── main.py
```

## Công nghệ sử dụng

- Python 3.11
- pandas, openpyxl — xử lý dữ liệu
- rich — giao diện terminal
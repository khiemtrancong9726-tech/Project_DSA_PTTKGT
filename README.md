# Project_DSA_PTTKGT — Hệ Thống Quản Lý Sinh Viên

So sánh hiệu năng các thuật toán tìm kiếm (Hash Table, Linear Search, Binary Search) trên dataset sinh viên giả lập.

## Tính năng

- **Scenario 1:** Tra cứu sinh viên theo MSSV
- **Scenario 2:** Lọc theo GPA và mã khoa
- **Scenario 3:** Tìm kiếm tên mờ (fuzzy search)
- Dataset: 1K / 5K / 10K records sinh viên
- **Hai giao diện:** Terminal (CLI) và Web UI chạy local

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

### Bước 1 — Sinh dataset (bắt buộc trước khi chạy)
```bash
python data/generator.py
```

---

### Giao diện 1 — Terminal (CLI)
```bash
python main.py
```
Giao diện dòng lệnh với rich terminal, chọn scenario và thuật toán bằng phím số.

---

### Giao diện 2 — Web UI (chạy local)
```bash
python web.py
```
Sau đó mở trình duyệt và truy cập:
```
http://localhost:8000
```

**Tính năng Web UI:**
- Chọn dataset và load bằng nút bấm
- Chạy từng thuật toán, xem thời gian thực thi ngay trên giao diện
- Scenario 2 & 3: hiển thị toàn bộ kết quả dưới dạng bảng có thể cuộn
- Bảng điều khiển hệ thống (terminal log) theo dõi từng thao tác

> Web UI chỉ chạy local (`localhost`) — không cần HTTPS, không expose ra ngoài internet.

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
├── web/
│   ├── index.html        # Giao diện Web UI
│   ├── script.js         # Logic frontend
│   └── style.css         # Stylesheet
├── web.py                # FastAPI server — chạy Web UI
├── main.py               # Entry point CLI
└── requirements.txt
```

## Công nghệ sử dụng

- Python 3.11
- pandas, openpyxl — xử lý dữ liệu
- rich — giao diện terminal
- FastAPI, uvicorn — Web UI server
- HTML / CSS / JavaScript — frontend
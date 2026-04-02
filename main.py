# main.py — chạy từ thư mục gốc project
# Lệnh: python main.py

import sys
from pathlib import Path

# Đảm bảo project root luôn nằm trong sys.path
# Dù chạy từ đâu, import "data.loader", "engine.*", "interface.*" đều hoạt động
sys.path.insert(0, str(Path(__file__).parent))

from interface.cli import main

if __name__ == "__main__":
    main()
# engine/benchmark.py
"""
Measurement Layer — đo thời gian thực thi thuần túy.

Chỉ có 1 nhiệm vụ duy nhất: đo.
Không biết scenario là gì, không gọi thuật toán trực tiếp.
"""

import time

REPEAT = 10


def _avg_ms(fn, repeat: int = REPEAT) -> tuple:
    """
    Chạy fn() `repeat` lần, trả về (avg_ms, last_result).

    Dùng perf_counter() — độ phân giải nano-second.
    Lấy trung bình để loại bỏ nhiễu OS scheduler.
    """
    total  = 0.0
    result = None
    for _ in range(repeat):
        start  = time.perf_counter()
        result = fn()
        total += time.perf_counter() - start
    return (total / repeat) * 1000, result

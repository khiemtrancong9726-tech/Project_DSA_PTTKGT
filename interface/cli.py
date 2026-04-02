# interface/cli.py
"""
Layer 3 — Entry point của toàn bộ project.

Luồng thực thi:
    1. Load dataset từ file xlsx (Layer 1 — loader.py)
    2. Cho user chọn dataset size (1K / 5K / 10K)
    3. Chọn scenario → chọn thuật toán → xem kết quả từng bước
    4. Render kết quả ra terminal (Layer 3 — display.py)
"""

import sys
from pathlib import Path
from contextlib import contextmanager

from rich.console  import Console
from rich.prompt   import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

# Layer 1
from data.loader import load_xlsx, build_hash_tables, sample_id

# Layer 2
from engine.benchmark import (
    bench_s1_chain, bench_s1_open, bench_s1_linear, bench_s1_binary,
    bench_s2a_hash, bench_s2a_linear, bench_s2a_binary,
    bench_s2b_hash, bench_s2b_linear, bench_s2b_binary,
    bench_s3_hash, bench_s3_fuzzy,
)

# Layer 3
from interface.display import (
    display_banner,
    display_s1_single,
    display_s2_single,
    display_s3_single,
    fmt_ms,
)

console = Console()

DATA_DIR = Path(__file__).parent.parent / "data"

DATASET_FILES = {
    "1": DATA_DIR / "students_1K.xlsx",
    "2": DATA_DIR / "students_5K.xlsx",
    "3": DATA_DIR / "students_10K.xlsx",
}
DATASET_LABELS = {
    "1": "1,000 records  (warm-up)",
    "2": "5,000 records  (so sánh rõ)",
    "3": "10,000 records (stress test)",
}

DEFAULT_DEPARTMENT = "CNTT"
DEFAULT_MIN_GPA    = 3.5
DEFAULT_QUERY      = "Văn An"


# ══════════════════════════════════════════════════════════════════
#  Helper
# ══════════════════════════════════════════════════════════════════

@contextmanager
def _spinner(msg: str):
    with Progress(
        SpinnerColumn(),
        TextColumn(f"  {msg}..."),
        transient=True,
        console=console,
    ) as p:
        p.add_task("", total=None)
        yield


def _tag(result: dict) -> str:
    """Tạo nhãn hiển thị bên cạnh tên thuật toán trong menu."""
    if result is None:
        return ""
    if result["failed"]:
        return "[red]❌ FAILED[/red]"
    return f"[green]✅ {fmt_ms(result['ms'])}[/green]"


# ══════════════════════════════════════════════════════════════════
#  Load dataset
# ══════════════════════════════════════════════════════════════════

def _pick_dataset() -> list:
    console.print("\n  [bold cyan]Chọn dataset:[/bold cyan]")
    for key, label in DATASET_LABELS.items():
        console.print(f"    [{key}] {label}")

    choice   = Prompt.ask("\n  Nhập lựa chọn", choices=["1", "2", "3"], default="1")
    filepath = DATASET_FILES[choice]
    label    = DATASET_LABELS[choice]

    with _spinner(f"Đang load [cyan]{label}[/cyan]"):
        records = load_xlsx(filepath)

    console.print(f"  ✅ Đã load [green]{len(records):,}[/green] records từ [dim]{filepath.name}[/dim]")
    return records


# ══════════════════════════════════════════════════════════════════
#  Chọn scenario
# ══════════════════════════════════════════════════════════════════

def _pick_scenario() -> str:
    console.print("\n  [bold cyan]Chọn scenario:[/bold cyan]")
    console.print("    [1] Scenario 1 — Tra cứu theo MSSV        (Hash wins)")
    console.print("    [2] Scenario 2 — Lọc đa điều kiện         (Hash wins / loses)")
    console.print("    [3] Scenario 3 — Tìm tên mơ hồ            (Hash loses hoàn toàn)")
    console.print("    [0] Thoát chương trình")
    return Prompt.ask("\n  Nhập lựa chọn", choices=["0", "1", "2", "3"])


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 1
# ══════════════════════════════════════════════════════════════════

def _run_scenario1(records: list, ht_chain, ht_open):
    suggest_id = sample_id(records, index=500)
    console.print(f"\n  [dim]Gợi ý MSSV có trong dataset: {suggest_id}[/dim]")
    raw       = Prompt.ask("  Nhập MSSV cần tra cứu (Enter để dùng gợi ý)").strip()
    target_id = raw if raw else suggest_id

    if not any(r["student_id"] == target_id for r in records):
        console.print(f"  [red]MSSV không tồn tại — dùng gợi ý thay thế.[/red]")
        target_id = suggest_id

    n = len(records)
    # collected: lưu kết quả từng thuật toán đã chạy
    collected = {"chain": None, "open": None, "linear": None, "binary": None}

    while True:
        console.print(f"\n  [bold cyan]SCENARIO 1 · MSSV: {target_id} · {n:,} records[/bold cyan]")
        console.print(f"  [bold cyan]Chọn thuật toán:[/bold cyan]")
        console.print(f"    [1] Hash Chaining        {_tag(collected['chain'])}")
        console.print(f"    [2] Hash Open Addressing {_tag(collected['open'])}")
        console.print(f"    [3] Linear Search        {_tag(collected['linear'])}")
        console.print(f"    [4] Binary Search        {_tag(collected['binary'])}")
        console.print(f"    [0] Quay lại")

        choice = Prompt.ask("  Nhập lựa chọn", choices=["0","1","2","3","4"])

        if choice == "0":
            break

        elif choice == "1":
            with _spinner("Đang chạy Hash Chaining (100 lần)"):
                r = bench_s1_chain(ht_chain, target_id)
            collected["chain"] = r
            display_s1_single(r, target_id)

        elif choice == "2":
            with _spinner("Đang chạy Hash Open Addressing (100 lần)"):
                r = bench_s1_open(ht_open, target_id)
            collected["open"] = r
            display_s1_single(r, target_id)

        elif choice == "3":
            with _spinner("Đang chạy Linear Search (100 lần)"):
                r = bench_s1_linear(records, target_id)
            collected["linear"] = r
            display_s1_single(r, target_id)

        elif choice == "4":
            with _spinner("Đang chạy Binary Search (100 lần)"):
                r = bench_s1_binary(records, target_id)
            collected["binary"] = r
            display_s1_single(r, target_id)


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 2
# ══════════════════════════════════════════════════════════════════

def _run_scenario2(records: list):
    n = len(records)

    # Chọn kiểu lọc
    console.print("\n  [bold cyan]SCENARIO 2 — Chọn kiểu lọc:[/bold cyan]")
    console.print("    [1] Khoảng GPA + Mã khoa       (Hash wins một phần)")
    console.print("    [2] Khoảng GPA                 (Hash FAILED, Binary wins)")
    console.print("    [0] Quay lại")

    filter_type = Prompt.ask("  Nhập lựa chọn", choices=["0","1","2"])
    if filter_type == "0":
        return

    if filter_type == "1":
        _run_scenario2a(records, n)
    else:
        _run_scenario2b(records, n)


def _run_scenario2a(records: list, n: int):
    """GPA tối thiểu + Department."""
    dept    = Prompt.ask(
        "  Mã khoa (CNTT / KHDL / HTTT / ATTT / KHMT)",
        default=DEFAULT_DEPARTMENT,
    )
    min_gpa = float(Prompt.ask("  GPA tối thiểu (vd: 3.0)", default="3.0"))
    max_gpa = float(Prompt.ask("  GPA tối đa   (vd: 4.0)", default="4.0"))

    if min_gpa > max_gpa:
        console.print("  [red]GPA tối thiểu phải nhỏ hơn tối đa.[/red]")
        return

    params    = {"department": dept, "min_gpa": min_gpa, "max_gpa": max_gpa}
    collected   = {"hash": None, "linear": None, "binary": None}

    while True:
        console.print(f"\n  [bold cyan]SCENARIO 2A · {dept} · GPA {min_gpa}→{max_gpa} · {n:,} records[/bold cyan]")
        console.print(f"  [bold cyan]Chọn thuật toán:[/bold cyan]")
        console.print(f"    [1] Composite Hash  {_tag(collected['hash'])}")
        console.print(f"    [2] Linear Scan     {_tag(collected['linear'])}")
        console.print(f"    [3] Binary Filter   {_tag(collected['binary'])}")
        console.print(f"    [0] Quay lại")

        choice = Prompt.ask("  Nhập lựa chọn", choices=["0","1","2","3"])

        if choice == "0":
            break

        elif choice == "1":
            with _spinner("Đang chạy Composite Hash (100 lần)"):
                r = bench_s2a_hash(records, dept, min_gpa, max_gpa)
            collected["hash"] = r
            display_s2_single(r, "2A", params)

        elif choice == "2":
            with _spinner("Đang chạy Linear Scan (100 lần)"):
                r = bench_s2a_linear(records, dept, min_gpa, max_gpa)
            collected["linear"] = r
            display_s2_single(r, "2A", params)

        elif choice == "3":
            with _spinner("Đang chạy Binary Filter (100 lần)"):
                r = bench_s2a_binary(records, dept, min_gpa, max_gpa)
            collected["binary"] = r
            display_s2_single(r, "2A", params)


def _run_scenario2b(records: list, n: int):
    """Khoảng GPA — Hash FAILED, Binary wins."""
    min_gpa = float(Prompt.ask("  GPA tối thiểu (vd: 3.2)", default="3.2"))
    max_gpa = float(Prompt.ask("  GPA tối đa   (vd: 3.7)", default="3.7"))

    if min_gpa > max_gpa:
        console.print("  [red]GPA tối thiểu phải nhỏ hơn tối đa.[/red]")
        return

    params    = {"min_gpa": min_gpa, "max_gpa": max_gpa}
    collected = {"hash": None, "linear": None, "binary": None}

    while True:
        console.print(f"\n  [bold cyan]SCENARIO 2B · GPA {min_gpa}→{max_gpa} · {n:,} records[/bold cyan]")
        console.print(f"  [bold cyan]Chọn thuật toán:[/bold cyan]")
        console.print(f"    [1] Hash lookup     {_tag(collected['hash'])}")
        console.print(f"    [2] Linear Scan     {_tag(collected['linear'])}")
        console.print(f"    [3] Binary Filter   {_tag(collected['binary'])}")
        console.print(f"    [0] Quay lại")

        choice = Prompt.ask("  Nhập lựa chọn", choices=["0","1","2","3"])

        if choice == "0":
            break

        elif choice == "1":
            r = bench_s2b_hash(min_gpa, max_gpa)
            collected["hash"] = r
            display_s2_single(r, "2B", params)

        elif choice == "2":
            with _spinner("Đang chạy Linear Scan (100 lần)"):
                r = bench_s2b_linear(records, min_gpa, max_gpa)
            collected["linear"] = r
            display_s2_single(r, "2B", params)

        elif choice == "3":
            with _spinner("Đang chạy Binary Filter (100 lần)"):
                r = bench_s2b_binary(records, min_gpa, max_gpa)
            collected["binary"] = r
            display_s2_single(r, "2B", params)


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 3
# ══════════════════════════════════════════════════════════════════

def _run_scenario3(records: list, ht_chain):
    n = len(records)
    console.print(f'\n  [dim]Default query: "{DEFAULT_QUERY}"[/dim]')
    query = Prompt.ask("  Nhập chuỗi tên cần tìm", default=DEFAULT_QUERY)

    collected = {"hash": None, "fuzzy": None}

    while True:
        console.print(f"\n  [bold cyan]SCENARIO 3 · Tìm tên mờ · \"{query}\" · {n:,} records[/bold cyan]")
        console.print(f"  [bold cyan]Chọn thuật toán:[/bold cyan]")
        console.print(f"    [1] Hash lookup          {_tag(collected['hash'])}")
        console.print(f"    [2] Fuzzy Linear Search  {_tag(collected['fuzzy'])}")
        console.print(f"    [0] Quay lại")

        choice = Prompt.ask("  Nhập lựa chọn", choices=["0","1","2"])

        if choice == "0":
            break

        elif choice == "1":
            r = bench_s3_hash(ht_chain, query)
            collected["hash"] = r
            display_s3_single(r, query)

        elif choice == "2":
            with _spinner(f'Đang chạy Fuzzy Search "{query}" (100 lần)'):
                r = bench_s3_fuzzy(records, query)
            collected["fuzzy"] = r
            display_s3_single(r, query)


# ══════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════

def main():
    display_banner()

    try:
        records = _pick_dataset()
    except FileNotFoundError as e:
        console.print(f"\n  [red]Lỗi:[/red] {e}")
        console.print("  [yellow]Gợi ý:[/yellow] Chạy [bold]python data/generator.py[/bold] để tạo dataset.")
        sys.exit(1)

    with _spinner("Đang build hash tables"):
        ht_chain, ht_open = build_hash_tables(records, load_factor=0.5)

    console.print(
        f"  ✅ Hash tables built — "
        f"size: [green]{ht_chain.size:,}[/green]  "
        f"load factor: [green]{ht_chain.load_factor():.2f}[/green]"
    )

    while True:
        choice = _pick_scenario()

        if choice == "0":
            console.print("\n  [yellow]Tạm biệt![/yellow]\n")
            break
        elif choice == "1":
            _run_scenario1(records, ht_chain, ht_open)
        elif choice == "2":
            _run_scenario2(records)
        elif choice == "3":
            _run_scenario3(records, ht_chain)


if __name__ == "__main__":
    main()
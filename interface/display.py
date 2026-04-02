# interface/display.py
"""
Layer 3 — Render kết quả benchmark ra terminal dùng thư viện rich.

Nguyên tắc:
    - Không có logic thuật toán ở đây — chỉ nhận dict từ benchmark.py rồi in.
    - Màu sắc nhất quán: xanh lá = WINNER, đỏ = FAILED/SLOWEST, vàng = kết luận.
    - Không dùng bar chart — kết quả số liệu đứng độc lập, rõ ràng hơn.
"""

from rich.console import Console
from rich.table   import Table
from rich.panel   import Panel
from rich.text    import Text
from rich         import box

console = Console()

C_FAILED = "bold red"


# ══════════════════════════════════════════════════════════════════
#  Helper chung
# ══════════════════════════════════════════════════════════════════

def fmt_ms(ms: float) -> str:
    if ms is None:
        return "—"
    return f"{ms:.6f} ms"


def _found_row(found: dict, target_id: str):
    """In thông tin sinh viên tìm được."""
    if found:
        console.print(f"  [bold]Sinh viên tìm được:[/bold]")
        console.print(
            f"  Tên: [green]{found['name']}[/green]  "
            f"│  Khoa: {found['department_code']}  "
            f"│  GPA: {found['gpa']}  "
            f"│  Tỉnh: {found['province_name']}"
        )
    else:
        console.print(f"  [red]Không tìm thấy MSSV {target_id}[/red]")


def _matches_table(matches: list, match_count: int):
    """In bảng kết quả lọc (tối đa 10 dòng)."""
    if not matches:
        console.print("  [red]Không tìm thấy kết quả nào.[/red]")
        return
    console.print(f"  [bold]Kết quả (hiển thị tối đa 10 / {match_count} tổng):[/bold]")
    tbl = Table(box=box.SIMPLE, show_header=True, header_style="cyan")
    tbl.add_column("MSSV",   min_width=14)
    tbl.add_column("Họ tên", min_width=22)
    tbl.add_column("Khoa",   min_width=8,  justify="center")
    tbl.add_column("GPA",    min_width=6,  justify="right")
    tbl.add_column("Tỉnh",   min_width=20)
    for r in matches[:10]:
        tbl.add_row(
            r["student_id"],
            f"[green]{r['name']}[/green]",
            r["department_code"],
            str(r["gpa"]),
            r["province_name"],
        )
    console.print(tbl)
    if match_count > 10:
        console.print(f"  [dim]... và {match_count - 10} kết quả khác[/dim]")


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 1 — Tra cứu theo MSSV
# ══════════════════════════════════════════════════════════════════

def display_banner():
    banner = Text()
    banner.append("HashIndex", style="bold cyan")
    banner.append(" — So sánh Hash Table với Linear & Binary Search", style="white")
    banner.append("\nBài toán: Hệ thống quản lý sinh viên đại học · 3 Scenario", style="dim")
    console.print(Panel(banner, box=box.DOUBLE, padding=(0, 2)))
    console.print()


def display_s1_single(result: dict, target_id: str):
    """In kết quả 1 thuật toán Scenario 1."""
    console.print()
    if result["failed"]:
        console.print(f"  [{C_FAILED}]{result['algo']}[/{C_FAILED}]  →  FAILED")
        return

    ms_str = fmt_ms(result["ms"])
    console.print(f"  [green]{result['algo']}[/green]  →  [green]{ms_str}[/green]")

    if result["sort_ms"] is not None:
        console.print(f"  [dim]  (+ sort: {fmt_ms(result['sort_ms'])} → tổng: {fmt_ms(result['ms'] + result['sort_ms'])})[/dim]")

    _found_row(result["found"], target_id)


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 2 — Lọc đa điều kiện
# ══════════════════════════════════════════════════════════════════

def display_s2_single(result: dict, filter_type: str, params: dict):
    console.print()
    if result["failed"]:
        console.print(f"  [{C_FAILED}]{result['algo']}[/{C_FAILED}]  →  [red]FAILED[/red]")
        console.print(f"  [dim]Hash không có khái niệm khoảng — chỉ tìm chính xác theo key.[/dim]")
        return

    console.print(f"  [green]{result['algo']}[/green]  →  [green]{fmt_ms(result['ms'])}[/green]  │  {result['match_count']} kết quả")
    if result.get("sort_ms") is not None:
        console.print(f"  [dim]  (+ sort: {fmt_ms(result['sort_ms'])} → tổng: {fmt_ms(result['ms'] + result['sort_ms'])})[/dim]")
    _matches_table(result["matches"], result["match_count"])


# ══════════════════════════════════════════════════════════════════
#  SCENARIO 3 — Tìm tên mờ
# ══════════════════════════════════════════════════════════════════

def display_s3_single(result: dict, query: str):
    console.print()
    if result["failed"]:
        console.print(f"  [{C_FAILED}]{result['algo']}[/{C_FAILED}]  →  [red]FAILED[/red]")
        console.print(f"  [dim]Hash chỉ tìm theo key chính xác (student_id), không tìm được theo tên.[/dim]")
        return

    console.print(
        f"  [green]{result['algo']}[/green]  →  "
        f"[green]{fmt_ms(result['ms'])}[/green]  │  {result['match_count']} kết quả"
    )
    _matches_table(result["matches"], result["match_count"])
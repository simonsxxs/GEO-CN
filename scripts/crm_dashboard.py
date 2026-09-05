#!/usr/bin/env python3
"""
GEO 客户管理看板 —— 命令行版
用 rich 渲染潜在客户 CRM 看板。

用法：
    python crm_dashboard.py                      # 主视图
    python crm_dashboard.py --prospect PRO-001   # 单个客户详情
    python crm_dashboard.py --pipeline           # 按阶段查看管道
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text
    from rich.rule import Rule
    from rich.layout import Layout
    from rich.align import Align
    from rich import box
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.padding import Padding
    from rich.style import Style
    from rich.markup import escape
except ImportError:
    print("错误：缺少 rich 库。请运行：pip install rich")
    sys.exit(1)

# ── 路径 ─────────────────────────────────────────────────────────────
CRM_PATH = Path.home() / ".geo-prospects" / "prospects.json"
AUDITS_DIR = Path.home() / ".geo-prospects" / "audits"
PROPOSALS_DIR = Path.home() / ".geo-prospects" / "proposals"

console = Console()

# ── 颜色辅助 ──────────────────────────────────────────────────────
# 状态字段值保持英文（与 prospects.json 数据结构兼容），仅展示层中文化。
# geo-prospect 使用五阶段（lead/qualified/proposal/won/lost），
# 历史数据里可能还有 audit/active/churned 写法，这里两组都映射。
STATUS_STYLE = {
    "lead":      ("⬜", "dim white",       "grey50"),
    "qualified": ("🔍", "bold yellow",     "yellow"),
    "audit":     ("🔍", "bold yellow",     "yellow"),
    "proposal":  ("📄", "bold cyan",       "cyan"),
    "won":       ("✅", "bold green",      "green"),
    "active":    ("✅", "bold green",      "green"),
    "churned":   ("❌", "dim red",         "red"),
    "lost":      ("💀", "dim red",         "red"),
}

STATUS_LABEL = {
    "lead":      "线索",
    "qualified": "已审计",
    "audit":     "已审计",
    "proposal":  "已发提案",
    "won":       "已签约",
    "active":    "合作中",
    "churned":   "已流失",
    "lost":      "已丢单",
}


def score_style(score: int) -> tuple[str, str]:
    """按 GEO 评分返回展示样式。

    参数：
        score: GEO 评分（0-100 整数）。
    返回：
        (颜色, 中文标签) 元组，标签分四档：优秀/中等/较差/危险。
    """
    if score >= 80:
        return "bold green",  "优秀"
    elif score >= 60:
        return "bold blue",   "中等"
    elif score >= 40:
        return "bold yellow",  "较差"
    else:
        return "bold red",    "危险"


def score_bar(score: int, width: int = 20) -> Text:
    """把评分渲染成彩色进度条。

    参数：
        score: GEO 评分（0-100 整数）。
        width: 进度条字符宽度，默认 20。
    返回：
        rich 的 Text 对象，含彩色进度条和“XX/100”数值。
    """
    filled = round((score / 100) * width)
    empty = width - filled
    color, _ = score_style(score)
    bar = Text()
    bar.append("█" * filled, style=color)
    bar.append("░" * empty, style="grey30")
    bar.append(f" {score}/100", style=color)
    return bar


def format_rmb(value: int | None) -> str:
    """把月合同额格式化为人民币展示字符串。

    参数：
        value: 金额（整数，单位元），None 或 0 视为未填写。
    返回：
        格式化字符串，如“¥18,000”；无金额时返回“—”。
    """
    if not value:
        return "—"
    return f"¥{value:,.0f}"


# ── 加载 CRM 数据 ────────────────────────────────────────────────────
def load_prospects() -> list[dict]:
    """从 prospects.json 加载全部客户记录。

    参数：无。
    返回：
        客户记录字典列表；文件不存在时打印提示并返回空列表。
    """
    if not CRM_PATH.exists():
        console.print(f"[red]未找到 CRM 文件：[/red] {CRM_PATH}")
        return []
    with open(CRM_PATH) as f:
        return json.load(f)


# ── 视图 ──────────────────────────────────────────────────────────────
def view_summary(prospects: list[dict]):
    """渲染顶部 KPI 汇总卡片。

    参数：
        prospects: 客户记录字典列表。
    返回：无，直接输出到终端。
    """
    total = len(prospects)
    # won 与 active 都视为已签约/合作中，保证两套状态写法下统计一致
    active = sum(1 for p in prospects if p.get("status") in ("active", "won"))
    pipeline = sum(p.get("monthly_value", 0) for p in prospects if p.get("status") == "proposal")
    mrr = sum(p.get("monthly_value", 0) for p in prospects if p.get("status") in ("active", "won"))
    avg_score = round(sum(p.get("geo_score", 0) for p in prospects) / total) if total else 0

    cards = [
        Panel(
            Align.center(
                Text.from_markup(
                    f"[bold white]{total}[/bold white]\n[dim]客户总数[/dim]"
                )
            ),
            border_style="bright_blue",
            padding=(1, 3),
        ),
        Panel(
            Align.center(
                Text.from_markup(
                    f"[bold green]{active}[/bold green]\n[dim]合作中客户[/dim]"
                )
            ),
            border_style="green",
            padding=(1, 3),
        ),
        Panel(
            Align.center(
                Text.from_markup(
                    f"[bold cyan]{format_rmb(mrr)}[/bold cyan]\n[dim]月收入（MRR）[/dim]"
                )
            ),
            border_style="cyan",
            padding=(1, 3),
        ),
        Panel(
            Align.center(
                Text.from_markup(
                    f"[bold yellow]{format_rmb(pipeline)}[/bold yellow]\n[dim]管道价值（已发提案）[/dim]"
                )
            ),
            border_style="yellow",
            padding=(1, 3),
        ),
        Panel(
            Align.center(
                Text.from_markup(
                    f"[bold]{avg_score}[/bold][dim]/100[/dim]\n[dim]平均 GEO 评分[/dim]"
                )
            ),
            border_style="magenta",
            padding=(1, 3),
        ),
    ]
    console.print(Columns(cards, equal=True, expand=True))


def view_prospect_table(prospects: list[dict]):
    """渲染客户主列表表格。

    参数：
        prospects: 客户记录字典列表，按 GEO 评分升序展示。
    返回：无，直接输出到终端。
    """
    table = Table(
        title=None,
        box=box.ROUNDED,
        border_style="bright_blue",
        header_style="bold bright_white on grey23",
        show_lines=False,
        expand=True,
        padding=(0, 1),
    )

    table.add_column("ID",       style="dim", width=9)
    table.add_column("公司",     style="bold white", min_width=16)
    table.add_column("域名",     style="cyan", min_width=18)
    table.add_column("状态",     justify="center", min_width=12)
    table.add_column("GEO 评分", justify="left", min_width=26)
    table.add_column("审计日期", justify="center", min_width=12)
    table.add_column("月合同额", justify="right", min_width=10)
    table.add_column("提案",     justify="center", min_width=10)

    for p in sorted(prospects, key=lambda x: x.get("geo_score", 0)):
        pid     = p.get("id", "—")
        company = p.get("company", "—")
        domain  = p.get("domain", "—")
        status  = p.get("status", "lead")
        score   = p.get("geo_score", 0)
        audit   = p.get("audit_date", "—")
        mrr     = format_rmb(p.get("monthly_value"))
        has_proposal = "✓" if p.get("proposal_file") else "—"

        icon, status_style, _ = STATUS_STYLE.get(status, ("?", "white", "white"))
        label = STATUS_LABEL.get(status, status)
        status_text = Text(f"{icon} {label}", style=status_style)

        table.add_row(
            pid,
            company,
            domain,
            status_text,
            score_bar(score),
            audit,
            mrr,
            has_proposal,
        )

    console.print(table)


def view_prospect_detail(prospects: list[dict], prospect_id: str):
    """渲染单个客户的详情视图。

    参数：
        prospects: 客户记录字典列表。
        prospect_id: 要查看的客户 ID（如 PRO-001）。
    返回：无，直接输出到终端；找不到客户时打印提示。
    """
    p = next((x for x in prospects if x.get("id") == prospect_id), None)
    if not p:
        console.print(f"[red]未找到客户：[/red] {prospect_id}")
        return

    score = p.get("geo_score", 0)
    color, label = score_style(score)

    # 头部
    console.print(Rule(f"[bold]{p['company']}[/bold] —— {p['domain']}", style="bright_blue"))
    console.print()

    # 评分与信息并排
    score_panel = Panel(
        Align.center(
            Text.from_markup(
                f"\n[{color}]{score}[/{color}]\n[dim]/100[/dim]\n\n[{color}]{label}[/{color}]\n"
            )
        ),
        title="GEO 评分",
        border_style=color.replace("bold ", ""),
        width=20,
    )

    status = p.get("status", "—")
    info_lines = [
        f"[dim]ID：[/dim]        {p.get('id', '—')}",
        f"[dim]状态：[/dim]      {STATUS_LABEL.get(status, status)}",
        f"[dim]行业：[/dim]      {p.get('industry', '—')}",
        f"[dim]地区：[/dim]      {p.get('country', '—')}",
        f"[dim]审计日期：[/dim]  {p.get('audit_date', '—')}",
        f"[dim]月合同额：[/dim]  {format_rmb(p.get('monthly_value'))}",
        f"[dim]合约期：[/dim]    {p.get('contract_months', '—')} 个月",
    ]
    if p.get("contact_name"):
        info_lines.append(f"[dim]联系人：[/dim]    {p['contact_name']}")
    if p.get("contact_email"):
        info_lines.append(f"[dim]邮箱：[/dim]      {p['contact_email']}")

    info_panel = Panel(
        "\n".join(info_lines),
        title="详细信息",
        border_style="bright_blue",
    )

    console.print(Columns([score_panel, info_panel], expand=False))
    console.print()

    # 关联文件
    files = []
    if p.get("audit_file"):
        audit_path = Path(p["audit_file"].replace("~", str(Path.home())))
        exists = "✓" if audit_path.exists() else "✗"
        files.append(f"  {exists} [cyan]审计：[/cyan]    {p['audit_file']}")
    if p.get("proposal_file"):
        prop_path = Path(p["proposal_file"].replace("~", str(Path.home())))
        exists = "✓" if prop_path.exists() else "✗"
        files.append(f"  {exists} [yellow]提案：[/yellow] {p['proposal_file']}")
    if files:
        console.print(Panel("\n".join(files), title="关联文件", border_style="dim"))
        console.print()

    # 跟进备注
    notes = p.get("notes", [])
    if notes:
        note_text = ""
        for note in notes:
            date = note.get("date", "")[:10]
            text = escape(note.get("text", ""))
            note_text += f"[dim]{date}[/dim]  {text}\n\n"
        console.print(Panel(note_text.rstrip(), title="跟进备注", border_style="dim"))


def view_pipeline(prospects: list[dict]):
    """按状态分组渲染管道视图。

    参数：
        prospects: 客户记录字典列表。
    返回：无，直接输出到终端。
    """
    statuses = ["lead", "qualified", "audit", "proposal", "won", "active", "churned", "lost"]
    console.print()
    console.print(Rule("[bold]按阶段查看管道[/bold]", style="bright_blue"))
    console.print()

    for status in statuses:
        group = [p for p in prospects if p.get("status") == status]
        if not group:
            continue
        icon, style, _ = STATUS_STYLE.get(status, ("?", "white", "white"))
        label = STATUS_LABEL.get(status, status)
        total_mrr = sum(p.get("monthly_value", 0) for p in group)
        line = f"{icon} [bold]{label}[/bold]（{len(group)} 个）  {format_rmb(total_mrr)}/月"
        console.print(f"  {line}", style=style)
        for p in group:
            score = p.get("geo_score", 0)
            color, _ = score_style(score)
            console.print(
                f"    [dim]·[/dim] {p.get('company', '—'):<25} [{color}]{score:>3}/100[/{color}]  [dim]{p.get('domain', '—')}[/dim]"
            )
        console.print()


# ── 主入口 ───────────────────────────────────────────────────────────
def main():
    """命令行入口：解析参数并渲染对应视图。

    参数：无（从 sys.argv 解析 --prospect / --pipeline）。
    返回：无。
    """
    parser = argparse.ArgumentParser(description="GEO 客户管理看板")
    parser.add_argument("--prospect", "-p", help="查看指定客户 ID 的详情")
    parser.add_argument("--pipeline", action="store_true", help="按阶段查看管道")
    args = parser.parse_args()

    prospects = load_prospects()
    if not prospects:
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    console.print()
    console.print(
        Panel.fit(
            f"[bold bright_white]GEO 客户管理[/bold bright_white]  [dim]—  {now}[/dim]",
            border_style="bright_blue",
            padding=(0, 2),
        )
    )
    console.print()

    if args.prospect:
        view_prospect_detail(prospects, args.prospect)
    elif args.pipeline:
        view_pipeline(prospects)
    else:
        view_summary(prospects)
        console.print()
        view_prospect_table(prospects)
        console.print()
        view_pipeline(prospects)

    console.print(
        f"[dim]CRM 数据：{CRM_PATH}   |   用 /geo-cn audit <域名> 新增客户[/dim]\n"
    )


if __name__ == "__main__":
    main()

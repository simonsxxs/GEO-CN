#!/usr/bin/env python3
"""
GEO 客户管理 —— 网页看板（Flask + HTMX）
用法：
    pip install flask
    python app.py
    打开 http://localhost:5050
"""

import json
import os
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, send_file, abort, jsonify

app = Flask(__name__)


@app.context_processor
def inject_now():
    """向所有模板注入当前时间变量。

    参数：无。
    返回：包含 now 字段（当前时间字符串）的字典。
    """
    return {"now": datetime.now().strftime("%Y-%m-%d %H:%M")}

CRM_PATH = Path.home() / ".geo-prospects" / "prospects.json"
PROPOSALS_DIR = Path.home() / ".geo-prospects" / "proposals"
AUDITS_DIR = Path.home() / ".geo-prospects" / "audits"


# ── 辅助函数 ────────────────────────────────────────────────────────────

def load_prospects() -> list[dict]:
    """从 prospects.json 加载全部客户记录。

    参数：无。
    返回：客户记录字典列表；文件不存在时返回空列表。
    """
    if not CRM_PATH.exists():
        return []
    with open(CRM_PATH) as f:
        return json.load(f)


def save_prospects(prospects: list[dict]):
    """把客户记录列表写回 prospects.json。

    参数：
        prospects: 客户记录字典列表。
    返回：无。
    """
    with open(CRM_PATH, "w") as f:
        json.dump(prospects, f, indent=2, ensure_ascii=False)


def score_tier(score: int) -> str:
    """按 GEO 评分返回样式等级（供模板 CSS 类使用）。

    参数：
        score: GEO 评分（0-100 整数）。
    返回：等级字符串：good / moderate / poor / critical。
    """
    if score >= 80: return "good"
    if score >= 60: return "moderate"
    if score >= 40: return "poor"
    return "critical"


def score_label(score: int) -> str:
    """按 GEO 评分返回中文档位标签。

    参数：
        score: GEO 评分（0-100 整数）。
    返回：中文标签：优秀 / 中等 / 较差 / 危险。
    """
    if score >= 80: return "优秀"
    if score >= 60: return "中等"
    if score >= 40: return "较差"
    return "危险"


def format_rmb(value) -> str:
    """把月合同额格式化为人民币展示字符串。

    参数：
        value: 金额（单位元），None 或 0 视为未填写。
    返回：格式化字符串，如“¥18,000”；无金额时返回“—”。
    """
    if not value:
        return "—"
    return f"¥{int(value):,}"


def crm_stats(prospects: list[dict]) -> dict:
    """计算看板顶部 KPI 统计数据。

    参数：
        prospects: 客户记录字典列表。
    返回：包含客户总数、合作中数量、月收入、管道价值、
        平均评分及平均评分等级的字典。
    """
    total = len(prospects)
    # won 与 active 都视为已签约/合作中，保证两套状态写法下统计一致
    active = [p for p in prospects if p.get("status") in ("active", "won")]
    proposals = [p for p in prospects if p.get("status") == "proposal"]
    mrr = sum(p.get("monthly_value", 0) for p in active)
    pipeline = sum(p.get("monthly_value", 0) for p in proposals)
    avg_score = round(sum(p.get("geo_score", 0) for p in prospects) / total) if total else 0
    return {
        "total": total,
        "active": len(active),
        "mrr": format_rmb(mrr),
        "pipeline": format_rmb(pipeline),
        "avg_score": avg_score,
        "avg_tier": score_tier(avg_score),
    }


def find_pdf(prospect: dict) -> Path | None:
    """查找某个客户对应的 PDF 文件。

    参数：
        prospect: 单条客户记录字典。
    返回：最新的 PDF 文件路径；没有则返回 None。
    """
    domain = prospect.get("domain", "")
    for f in sorted(PROPOSALS_DIR.glob(f"{domain}*.pdf"), reverse=True):
        return f
    return None


# ── 模板过滤器 ────────────────────────────────────────────────────

app.jinja_env.filters["score_tier"] = score_tier
app.jinja_env.filters["score_label"] = score_label
app.jinja_env.filters["format_rmb"] = format_rmb

# 状态字段值保持英文（与 prospects.json 数据结构兼容），仅展示层中文化。
# geo-prospect 使用五阶段（lead/qualified/proposal/won/lost），
# 历史数据里可能还有 audit/active/churned 写法，这里两组都映射。
STATUS_META = {
    "lead":      {"icon": "⬜", "badge": "secondary",  "label": "线索"},
    "qualified": {"icon": "🔍", "badge": "warning",    "label": "已审计"},
    "audit":     {"icon": "🔍", "badge": "warning",    "label": "已审计"},
    "proposal":  {"icon": "📄", "badge": "info",       "label": "已发提案"},
    "won":       {"icon": "✅", "badge": "success",    "label": "已签约"},
    "active":    {"icon": "✅", "badge": "success",    "label": "合作中"},
    "churned":   {"icon": "❌", "badge": "danger",     "label": "已流失"},
    "lost":      {"icon": "💀", "badge": "dark",       "label": "已丢单"},
}


@app.template_filter("status_meta")
def status_meta_filter(status: str) -> dict:
    """把状态字段值映射为展示元数据（图标、徽章颜色、中文标签）。

    参数：
        status: 状态字段值（如 lead / proposal / active）。
    返回：含 icon、badge、label 的字典；未知状态原样返回字段值。
    """
    return STATUS_META.get(status, {"icon": "?", "badge": "secondary", "label": status})


# ── 路由 ─────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    """主看板页：客户列表 + KPI 卡片，支持状态过滤和排序。

    参数：无（从 query string 读取 status / sort）。
    返回：渲染后的 dashboard.html 页面。
    """
    prospects = load_prospects()
    status_filter = request.args.get("status", "")
    sort = request.args.get("sort", "score")

    filtered = [p for p in prospects if not status_filter or p.get("status") == status_filter]

    if sort == "score":
        filtered.sort(key=lambda x: x.get("geo_score", 0))
    elif sort == "company":
        filtered.sort(key=lambda x: x.get("company", "").lower())
    elif sort == "mrr":
        filtered.sort(key=lambda x: x.get("monthly_value", 0), reverse=True)

    stats = crm_stats(prospects)
    statuses = list(STATUS_META.keys())

    return render_template(
        "dashboard.html",
        prospects=filtered,
        stats=stats,
        status_filter=status_filter,
        sort=sort,
        statuses=statuses,
        STATUS_META=STATUS_META,
    )


@app.route("/prospect/<pid>")
def prospect_detail(pid):
    """客户详情页：评分、信息、关联文件、备注。

    参数：
        pid: 客户 ID（如 PRO-001）。
    返回：渲染后的 prospect.html 页面；客户不存在时返回 404。
    """
    prospects = load_prospects()
    p = next((x for x in prospects if x.get("id") == pid), None)
    if not p:
        abort(404)

    pdf_path = find_pdf(p)
    has_pdf = pdf_path is not None

    return render_template(
        "prospect.html",
        p=p,
        has_pdf=has_pdf,
        STATUS_META=STATUS_META,
        statuses=list(STATUS_META.keys()),
    )


@app.route("/prospect/<pid>/note", methods=["POST"])
def add_note(pid):
    """HTMX 接口：为客户追加一条备注，返回更新后的备注片段。

    参数：
        pid: 客户 ID。备注内容从表单字段 text 读取。
    返回：渲染后的 _notes.html 片段；客户不存在时返回 404。
    """
    prospects = load_prospects()
    p = next((x for x in prospects if x.get("id") == pid), None)
    if not p:
        abort(404)

    text = request.form.get("text", "").strip()
    if text:
        if "notes" not in p:
            p["notes"] = []
        p["notes"].append({
            "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "text": text,
        })
        p["updated_at"] = datetime.now().strftime("%Y-%m-%d")
        save_prospects(prospects)

    return render_template("_notes.html", p=p)


@app.route("/prospect/<pid>/status", methods=["POST"])
def update_status(pid):
    """HTMX 接口：更新客户状态，返回新的状态徽章片段。

    参数：
        pid: 客户 ID。新状态从表单字段 status 读取。
    返回：状态徽章 HTML 片段；客户不存在时返回 404。
    """
    prospects = load_prospects()
    p = next((x for x in prospects if x.get("id") == pid), None)
    if not p:
        abort(404)

    new_status = request.form.get("status", "").strip()
    if new_status in STATUS_META:
        p["status"] = new_status
        p["updated_at"] = datetime.now().strftime("%Y-%m-%d")
        save_prospects(prospects)

    meta = STATUS_META.get(p["status"], {})
    return f'<span class="badge bg-{meta["badge"]} fs-6">{meta["icon"]} {meta["label"]}</span>'


@app.route("/prospect/<pid>/pdf")
def download_pdf(pid):
    """下载客户对应的 PDF 报告。

    参数：
        pid: 客户 ID。
    返回：PDF 文件下载响应；客户或 PDF 不存在时返回 404。
    """
    prospects = load_prospects()
    p = next((x for x in prospects if x.get("id") == pid), None)
    if not p:
        abort(404)

    pdf_path = find_pdf(p)
    if not pdf_path:
        abort(404)

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=pdf_path.name,
        mimetype="application/pdf",
    )


# ── 启动 ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, port=5050)

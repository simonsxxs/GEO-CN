---
name: geo-prospect
description: >
  轻量 CRM：管理 GEO 服务商的潜在客户与客户。跟踪销售管道全流程：
  线索 → 已审计 → 已发提案 → 已签约 → 已丢单。存储审计历史、跟进备注、
  合同金额，并生成管道汇总。当用户说 "客户"、"线索"、"prospect"、"lead"、
  "管道"、"crm"、"新增客户"、"跟进"，或管理 GEO 接单的业务侧时使用。
version: 2.0.0
tags: [geo, business, crm, prospect, pipeline, sales]
allowed-tools: Read, Write, Bash, Glob
---

# GEO 客户管理器

## 用途

管理 GEO 接单全流程的潜在客户与客户。
所有数据存储在 `~/.geo-prospects/prospects.json`（跨会话持久化）。

---

## 命令

| 命令 | 作用 |
|---------|-------------|
| `/geo-cn prospect new <域名>` | 新建客户（交互式录入） |
| `/geo-cn prospect list` | 显示全部客户及管道状态 |
| `/geo-cn prospect list <状态>` | 按状态过滤：lead、qualified、proposal、won、lost |
| `/geo-cn prospect show <id或域名>` | 客户完整详情与历史 |
| `/geo-cn prospect audit <id或域名>` | 跑一次快速 GEO 审计并存入客户记录 |
| `/geo-cn prospect note <id或域名> "<内容>"` | 添加带时间戳的跟进备注 |
| `/geo-cn prospect status <id或域名> <新状态>` | 在管道中推进阶段 |
| `/geo-cn prospect won <id或域名> <月合同额>` | 标记签约，设置合同金额（元/月） |
| `/geo-cn prospect lost <id或域名> "<原因>"` | 标记丢单并记录原因 |
| `/geo-cn prospect pipeline` | 可视化管道汇总与营收预测 |

---

## 数据结构

每个客户存储为一条 JSON 记录（字段名固定，不要改动）：

```json
{
  "id": "PRO-001",
  "company": "杭州明川教育科技有限公司",
  "domain": "mingchuan-edu.cn",
  "contact_email": "zhangwei@mingchuan-edu.cn",
  "contact_name": "张伟",
  "industry": "教育装备（B2B）",
  "country": "中国",
  "status": "qualified",
  "geo_score": 32,
  "audit_date": "2026-08-20",
  "audit_file": "~/.geo-prospects/audits/mingchuan-edu.cn-2026-08-20.md",
  "proposal_file": "~/.geo-prospects/proposals/mingchuan-edu.cn-proposal.md",
  "monthly_value": 0,
  "contract_start": null,
  "contract_months": 0,
  "notes": [
    {
      "date": "2026-08-20",
      "text": "首次 GEO 快速扫描。评分 32/100 —— 危险档。GEO 服务意向很强的候选客户。"
    }
  ],
  "created_at": "2026-08-20",
  "updated_at": "2026-08-20"
}
```

---

## 编排指令

### `/geo-cn prospect new <域名>`

1. 检查 `~/.geo-prospects/prospects.json` 是否存在，不存在则创建（空数组）
2. 从域名自动推断公司名（如 `mingchuan-edu.cn` → `Mingchuan Edu`，再向用户确认中文公司名）
3. 分配下一个顺序 ID：`PRO-001`、`PRO-002`……
4. 向用户询问：
   - 联系人姓名（可选）
   - 联系邮箱（可选）
   - 预估月合同额（可选，单位：元）
5. 状态设为 `lead`
6. 保存到 JSON 文件
7. 建议下一步："运行 `/geo-cn prospect audit mingchuan-edu.cn` 给这个客户打个分"

### `/geo-cn prospect list`

读取 `~/.geo-prospects/prospects.json` 并渲染汇总表：

```
GEO 客户管道 —— 2026 年 8 月
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID       域名                    公司               状态        评分    月合同额
───────  ──────────────────────  ────────────────  ──────────  ──────  ────────
PRO-001  mingchuan-edu.cn        明川教育          已审计      32/100  ¥1.8万
PRO-002  lanjing-scm.com         蓝鲸供应链        线索        —       —
PRO-003  shiguang-coffee.cn      拾光咖啡          已签约      55/100  ¥0.8万

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
管道：1 线索 | 1 已审计 | 0 已发提案 | 1 已签约 | 0 已丢单
已签约月收入（MRR）：¥8,000 | 管道价值：¥18,000
```

### `/geo-cn prospect audit <id或域名>`

1. 运行 `/geo-cn quick <域名>` 获取 GEO 快照评分
2. 把评分存入客户记录：`geo_score`、`audit_date`
3. 审计输出存到 `~/.geo-prospects/audits/<域名>-<日期>.md`
4. 更新客户记录里的 `audit_file` 路径
5. 添加自动备注："快速审计完成。GEO 评分：XX/100。"
6. 评分 < 55 时建议："评分显示明确的商机。运行 `/geo-cn proposal <域名>` 生成提案。"

### `/geo-cn prospect note <id或域名> "<内容>"`

1. 按 ID 或域名找到客户
2. 追加带当前 ISO 日期的备注
3. 保存回 JSON
4. 确认："已为 明川教育（PRO-001）添加备注"

### `/geo-cn prospect status <id或域名> <状态>`

合法状态：`lead`、`qualified`、`proposal`、`won`、`lost`

1. 更新状态字段
2. 添加自动备注："状态变更为 <状态>"
3. 保存并确认

### `/geo-cn prospect pipeline`

面向营收的可视化管道汇总：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GEO 接单管道汇总 —— 2026 年 8 月
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

阶段            数量    潜在月价值       备注
─────────────  ─────   ───────────────   ─────────────────────
线索              2      ¥16,000/月       新发现
已审计            1      ¥9,000/月        可出提案
已发提案          1      ¥12,000/月       等待签单
已签约            3      ¥37,000/月       服务中（MRR）
已丢单            1      —                 预算冻结

已签约月收入：      ¥37,000
管道（已审计+）：   ¥21,000
总潜在价值：        ¥58,000/月 → ¥696,000/年

下一步动作：
→ PRO-003（lanjing-scm.com）：发提案 —— 评分 38/100（商机明确）
→ PRO-007（some-shop.cn）：跟进 —— 提案发出已 8 天
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 存储位置

所有数据存于 `~/.geo-prospects/`：
```
~/.geo-prospects/
├── prospects.json          # CRM 主数据库
├── audits/                 # 快速审计快照
│   └── mingchuan-edu.cn-2026-08-20.md
└── proposals/              # 生成的提案
    └── mingchuan-edu.cn-proposal.md
```

目录不存在时先创建：`mkdir -p ~/.geo-prospects/audits ~/.geo-prospects/proposals`

---

## 管道阶段定义

| 状态 | 含义 | 典型下一步 |
|--------|---------|---------------------|
| `lead`（线索） | 已发现，尚未接触 | 跑快速审计，评估商机 |
| `qualified`（已审计） | 审计完成，痛点确认 | 生成提案 |
| `proposal`（已发提案） | 提案已发，等待决定 | 跟进、答疑 |
| `won`（已签约） | 合同已签，服务中 | 跑完整审计，启动服务 |
| `lost`（已丢单） | 成交失败 | 记录原因备查 |

---

## 输出

- 所有命令在终端打印确认信息 + 客户当前状态
- 除明确保存审计/提案外不写外部文件
- JSON 数据库是唯一事实来源

# geo-cn — 国内网站 AI 搜索可见性审计工具

> 作者：**simonsxxs**（一个不会代码的AI极客） ｜ 微信交流群：**simonsxxs**

**GEO 优先，SEO 托底。** 让网站更容易被国内 AI 搜索引擎
（百度AI搜索、Kimi、DeepSeek、豆包、元宝、夸克/通义）引用，
同时保留传统 SEO 基础检查。

AI 搜索正在吃掉传统搜索。这个工具优化的是流量正在流向的地方，而不是它曾经所在的地方。

geo-cn 不只是一套审计工具，还内置了完整的 **GEO 接单工作流**：
从客户管理、快速初筛、出具提案，到每月进度汇报，一个工具包跑完
「找客户 → 做审计 → 签单 → 续费」的全流程。

---

## 它能帮你做什么

**审计侧（给客户做诊断）：**

- 对任意国内网站跑一次完整 GEO + SEO 审计，产出 0-100 综合评分和分优先级整改计划
- 逐段给内容打「AI 可引用性」分数（针对中文内容专门设计的评分引擎）
- 检查国内 AI 爬虫（Bytespider、Baiduspider 等）能否抓取你的网站
- 扫描品牌在知乎、B站、百科、公众号等国内 AI 引用源上的存在感
- 针对百度AI搜索、Kimi、DeepSeek、豆包、元宝、夸克/通义逐一给出优化清单
- 生成 llms.txt、Schema 结构化数据、客户级中文报告（Markdown / PDF）

**接单侧（把审计变成生意）：**

- `/geo-cn prospect` —— 轻量客户管理（CRM）：记录潜在客户、跟踪销售管道、管理跟进笔记
- `/geo-cn proposal` —— 基于审计数据一键生成中文服务提案（含三档报价、ROI 测算）
- `/geo-cn compare` —— 每月自动生成「评分涨了多少」的进度月报，向客户证明价值

---

## 快速开始

### 一键安装（macOS/Linux）

```bash
cd geo-cn
./install.sh
```

### Windows（Git Bash）

需要安装 [Git for Windows](https://git-scm.com/downloads)（自带 Git Bash）。

```bash
# 在 Git Bash 中运行（不要用 PowerShell / CMD）
cd geo-cn
./install-win.sh
```

> **注意：** 右键文件夹选择 "Open Git Bash here"，或打开 Git Bash 后切换到该目录。不要使用 PowerShell 或命令提示符。

### 环境要求

- Python 3.8+（Debian/Ubuntu 还需 `python3-venv`）
- Claude Code CLI
- Git
- 可选：[`uv`](https://docs.astral.sh/uv/) —— 存在时安装器会用它加速依赖安装
- 可选：Playwright（用于截图）
- 可选：pandoc + Google Chrome（用于 PDF 报告）

### 隔离安装

Python 依赖安装在独立的虚拟环境 `~/.claude/skills/geo/.venv/` 中，
**不会改动**系统 Python，卸载时会连同虚拟环境一起删除。

Skill 和 agent 文件直接引用该虚拟环境，因此无论你的 `PATH` 上的
`python3` 指向哪里，工具都能正常工作。

---

## 命令列表

打开 Claude Code，使用以下命令：

| 命令 | 作用 |
|---------|-------------|
| `/geo-cn audit <url>` | 完整 GEO + SEO 审计（并行子代理） |
| `/geo-cn quick <url>` | 60 秒 GEO 可见性快照 |
| `/geo-cn citability <url>` | 内容 AI 可引用性评分（中文引擎） |
| `/geo-cn crawlers <url>` | 检查 AI 爬虫访问权限（robots.txt） |
| `/geo-cn llmstxt <url>` | 分析或生成 llms.txt |
| `/geo-cn brands <url>` | 扫描国内平台品牌提及（知乎、B站、百科、公众号等） |
| `/geo-cn platforms <url>` | 国内平台专项优化（含出海附录） |
| `/geo-cn schema <url>` | 结构化数据检测与生成 |
| `/geo-cn technical <url>` | 技术 SEO 审计（含百度站长、ICP 备案） |
| `/geo-cn content <url>` | 内容质量与 E-E-A-T 评估 |
| `/geo-cn report <url>` | 生成客户级 GEO 报告（中文） |
| `/geo-cn report-pdf` | 生成带图表和可视化评分的专业 PDF 报告 |
| `/geo-cn prospect <子命令>` | 轻量 CRM：潜在客户管道管理 |
| `/geo-cn proposal <域名>` | 基于审计数据生成中文客户提案 |
| `/geo-cn compare <域名>` | 月度对比报告：向客户展示评分提升 |

---

## 目录架构

```
geo-cn/
├── geo/                          # 主 skill 编排器
│   └── SKILL.md                  # 主 skill 文件（/geo-cn 命令与路由）
├── skills/                       # 14 个专项子 skill
│   ├── geo-audit/                # 完整审计编排与评分
│   ├── geo-citability/           # AI 引用就绪度评分（中文引擎）
│   ├── geo-crawlers/             # AI 爬虫访问分析（国内版爬虫名单）
│   ├── geo-llmstxt/              # llms.txt 标准分析与生成
│   ├── geo-brand-mentions/       # 国内平台品牌存在感
│   ├── geo-platform-optimizer/   # 国内 AI 搜索平台专项优化（含出海附录）
│   ├── geo-schema/               # 面向 AI 发现的结构化数据
│   ├── geo-technical/            # 技术 SEO 基础（含百度站长、ICP 备案）
│   ├── geo-content/              # 内容质量与 E-E-A-T
│   ├── geo-report/               # 客户级 markdown 报告生成
│   ├── geo-report-pdf/           # 带图表的专业 PDF 报告（pandoc 管线）
│   ├── geo-prospect/             # 轻量 CRM 潜在客户管道管理
│   ├── geo-proposal/             # 自动生成中文客户提案
│   └── geo-compare/              # 月度增量追踪与进度报告
├── agents/                       # 5 个并行子代理
│   ├── geo-ai-visibility.md      # GEO 审计、可引用性、爬虫、品牌提及
│   ├── geo-platform-analysis.md  # 平台专项优化分析
│   ├── geo-technical.md          # 技术 SEO 分析
│   ├── geo-content.md            # 内容与 E-E-A-T 分析
│   └── geo-schema.md             # Schema 标记分析
├── scripts/                      # Python 工具脚本
│   ├── fetch_page.py             # 页面抓取与解析
│   ├── citability_scorer.py      # 中文 AI 可引用性评分引擎
│   ├── brand_scanner.py          # 品牌提及检测（国内平台版）
│   ├── llmstxt_generator.py      # llms.txt 校验与生成
│   ├── crm_dashboard.py          # CRM 终端看板（rich）
│   └── webapp/                   # CRM 网页看板（Flask + HTMX）
├── schema/                       # JSON-LD 模板
│   ├── organization.json         # Organization schema（含 sameAs）
│   ├── local-business.json       # LocalBusiness schema
│   ├── article-author.json       # Article + Person schema（E-E-A-T）
│   ├── software-saas.json        # SoftwareApplication schema
│   ├── product-ecommerce.json    # 带报价的 Product schema
│   └── website-searchaction.json # WebSite + SearchAction schema
├── templates/                    # PDF 报告样式模板
├── docs/                         # 使用文档（入门、命令参考、评分方法等）
├── examples/                     # 示例数据
├── install.sh                    # 一键安装脚本
├── uninstall.sh                  # 卸载脚本
├── requirements.txt              # Python 依赖
└── README.md                     # 本文件
```

> **打包说明：** 仓库中的 `openspec/` 是开发过程档案（需求、设计、任务记录），
> **发布打包时请整体排除该目录**，它不是产品的一部分。

---

## 数据存储

CRM 与报告类 skill（`/geo-cn prospect`、`/geo-cn proposal`、`/geo-cn compare`）
将运行时数据存储在 Claude Code 目录之外：

```
~/.geo-prospects/
├── prospects.json              # 客户/潜在客户管道数据
├── audits/                     # 快速审计快照
├── proposals/                  # 生成的提案文档
│   └── <域名>-proposal-<日期>.md
└── reports/                    # 月度增量报告
    └── <域名>-monthly-<YYYY-MM>.md
```

卸载脚本**不会删除**该目录 —— 如不再需要客户数据，请手动删除。

---

## 工作原理

### 完整审计流程

运行 `/geo-cn audit https://example.com` 时：

1. **发现** —— 抓取首页、识别业务类型、解析 sitemap
2. **并行分析** —— 同时启动 5 个子代理：
   - AI 可见性（可引用性、爬虫、llms.txt、品牌提及）
   - 平台分析（百度AI搜索、Kimi、DeepSeek、豆包、元宝、夸克/通义就绪度）
   - 技术 SEO（Core Web Vitals、SSR、安全、移动端）
   - 内容质量（E-E-A-T、可读性、时效性）
   - Schema 标记（检测、验证、生成）
3. **综合** —— 汇总评分，计算综合 GEO 评分（0-100）
4. **报告** —— 输出分优先级的整改计划与速赢项（中文）

### 评分方法

| 类别 | 权重 |
|----------|--------|
| AI 可引用性与可见性 | 25% |
| 品牌权威信号 | 20% |
| 内容质量与 E-E-A-T | 20% |
| 技术基础 | 15% |
| 结构化数据 | 10% |
| 平台优化 | 10% |

---

## 核心功能

### 可引用性评分（中文引擎）
按中文字符数分析内容块的 AI 引用就绪度：识别「是指 / 简单来说 / 换句话说」
等定义句式、中文代词密度、按中文标点切分句子、识别「元 / 万元 / 亿元」金额
和「据…显示」类具名来源。最易被 AI 引用的中文段落为 200-350 字（推断值）、
自成一体、事实密度高、直接回答问题。

### AI 爬虫分析
检查 robots.txt 中的国内外 AI 爬虫（Bytespider、Baiduspider、
Kimi-User、GPTBot、ClaudeBot、PerplexityBot 等），给出放行/拦截建议。
DeepSeek 无公开爬虫 UA，手册中如实标注。

### 品牌提及扫描
品牌提及与 AI 可见性的相关性是反向链接的 3 倍。扫描知乎、B站、
百度百科/中文维基、微信公众号（搜狗微信入口）、CSDN、掘金、V2EX、
GitHub、Gitee 等国内平台。

### 平台专项优化
针对 6 个国内 AI 平台分别给出来源选择机制说明、优化清单和百分制评分表。
未公开的平台机制如实标注「未公开」，不做臆测。

### llms.txt 生成
生成新兴的 llms.txt 标准文件，帮助 AI 爬虫理解你的网站结构。

### 客户级报告
生成 markdown 或 PDF 格式的专业中文 GEO 报告。PDF 报告包含评分仪表盘、
彩色评分表、分优先级整改计划，可直接交付客户。

---

## 适用场景

- **GEO 服务商** —— 为客户做审计、出提案、按月汇报，跑通完整接单流程
- **市场团队** —— 监测并提升国内 AI 搜索可见性
- **内容创作者** —— 优化内容以提高被 AI 引用率
- **本地商家** —— 让 AI 助手能找到你
- **SaaS 公司** —— 提升国内 AI 平台上的实体识别度
- **电商** —— 优化商品页以获得 AI 购物推荐

---

## 文档

| 文档 | 内容 |
|------|------|
| [docs/getting-started.md](docs/getting-started.md) | 环境要求、安装、第一次审计、排错、卸载 |
| [docs/commands-reference.md](docs/commands-reference.md) | 全部 `/geo-cn` 命令的用法、参数与输出 |
| [docs/architecture.md](docs/architecture.md) | 仓库结构、审计流程、并行子代理、数据存储 |
| [docs/skills-and-agents.md](docs/skills-and-agents.md) | 每个子 skill、子代理、脚本、模板的参考手册 |
| [docs/scoring-methodology.md](docs/scoring-methodology.md) | 综合评分与可引用性评分的计算方法 |
| [docs/faq.md](docs/faq.md) | 常见问题 |

---

## 卸载

```bash
./uninstall.sh
```

或手动卸载：

```bash
rm -rf ~/.claude/skills/geo ~/.claude/skills/geo-* ~/.claude/agents/geo-*.md
```

---

## 许可证

MIT License。

---

## 作者与交流

- **作者：** simonsxxs（一个不会代码的AI极客）
- **微信交流群：** simonsxxs

欢迎进群交流 GEO 实战心得、反馈问题、分享案例。

---

为 AI 搜索时代而生。

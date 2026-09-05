---
name: geo-cn
description: >
  面向国内 AI 平台的 GEO 审计工具。优化网站在国内 AI 搜索引擎（百度AI搜索、
  Kimi、DeepSeek、豆包、元宝、夸克/通义）中的可见性与被引用率，同时保留
  传统 SEO 基础检查。支持完整 GEO 审计、可引用性评分、AI 爬虫分析、
  llms.txt 生成、品牌提及扫描、平台专项优化、Schema 结构化数据、
  技术 SEO、内容质量（E-E-A-T）评估，以及客户级 GEO 报告生成。
  Use when user says "geo-cn", "geo", "seo", "audit", "AI search",
  "AI visibility", "optimize", "citability", "llms.txt", "schema",
  "brand mentions", "GEO report", or any URL for analysis.
allowed-tools: Read, Grep, Glob, Bash, WebFetch, Write
---

# GEO-CN 国内版 GEO/SEO 审计工具 — Claude Code Skill（2026 年 2 月）

> **理念：** GEO 优先，SEO 托底。AI 搜索正在吃掉传统搜索。
> 这个工具优化的是流量正在流向的地方，而不是它曾经所在的地方。
>
> **国内化说明：** 本版本面向国内 AI 平台（百度AI搜索、Kimi、DeepSeek、
> 豆包、元宝、夸克/通义）。国外平台（ChatGPT、Perplexity、Gemini、
> Google AIO、Copilot）检查见 `skills/geo-platform-optimizer` 出海附录。

---

## 快速参考

| 命令 | 作用 |
|---------|-------------|
| `/geo-cn audit <url>` | 完整 GEO + SEO 审计（并行子代理） |
| `/geo-cn page <url>` | 单页面深度 GEO 分析 |
| `/geo-cn citability <url>` | 内容 AI 可引用性评分 |
| `/geo-cn crawlers <url>` | 检查 AI 爬虫访问权限（robots.txt 分析） |
| `/geo-cn llmstxt <url>` | 分析或生成 llms.txt 文件 |
| `/geo-cn brands <url>` | 扫描国内平台品牌提及（知乎、B站、百科、公众号等） |
| `/geo-cn platforms <url>` | 平台专项优化（百度AI搜索、Kimi、DeepSeek、豆包、元宝、夸克/通义） |
| `/geo-cn schema <url>` | 检测、验证并生成结构化数据 |
| `/geo-cn technical <url>` | 传统技术 SEO 审计（含百度站长、ICP 备案检查） |
| `/geo-cn content <url>` | 内容质量与 E-E-A-T 评估 |
| `/geo-cn report <url>` | 生成客户级 GEO 交付报告 |
| `/geo-cn report-pdf <url>` | 生成带图表和评分的专业 PDF 报告 |
| `/geo-cn quick <url>` | 60 秒 GEO 可见性快照 |
| `/geo-cn prospect <cmd>` | 轻量 CRM：管理销售管道中的潜在客户 |
| `/geo-cn proposal <domain>` | 基于审计数据自动生成客户提案 |
| `/geo-cn compare <domain>` | 月度对比报告：向客户展示评分提升 |

---

## 市场背景（为什么 GEO 重要）

> 以下为全球 AI 搜索市场公开数据；国内各 AI 平台的引用机制与流量
> 分布数据大多**未公开**，分析时以可观测信号为准，不做臆测。

| 指标 | 数值 | 来源 |
|--------|-------|--------|
| GEO 服务市场（2025） | $850M-$886M | Yahoo Finance / Superlines |
| GEO 市场预测（2031） | $7.3B（34% CAGR） | 行业分析师 |
| AI 引荐会话增长 | +527%（2025 年 1-5 月） | SparkToro |
| AI 流量转化率 vs 自然搜索 | 高 4.4 倍 | 行业数据 |
| Google AI Overviews 覆盖 | 15 亿用户/月，200+ 国家 | Google |
| ChatGPT 周活跃用户 | 9 亿+ | OpenAI |
| Perplexity 月查询量 | 5 亿+ | Perplexity |
| Gartner 预测 2028 年搜索流量下降 | -50% | Gartner |
| 投入 GEO 的营销人员占比 | 仅 23% | 行业调研 |
| 品牌提及 vs 反向链接对 AI 引用 | 相关性高 3 倍 | Ahrefs（2025 年 12 月） |

---

## 编排逻辑

### 完整审计（`/geo-cn audit <url>`）

**阶段 1：发现（顺序执行）**
1. 抓取首页 HTML（curl 或 WebFetch）
2. 识别业务类型（SaaS、本地服务、电商、内容站、代理商、其他）
3. 从 sitemap.xml 或内链提取关键页面（最多 50 页）

**阶段 2：并行分析（委派给子代理）**
同时启动以下 5 个子代理：

| 子代理 | 文件 | 职责 |
|----------|------|---------------|
| geo-ai-visibility | `agents/geo-ai-visibility.md` | GEO 审计、可引用性、AI 爬虫、llms.txt、品牌提及 |
| geo-platform-analysis | `agents/geo-platform-analysis.md` | 平台专项优化（百度AI搜索、Kimi、DeepSeek、豆包、元宝、夸克/通义） |
| geo-technical | `agents/geo-technical.md` | 技术 SEO、Core Web Vitals、可抓取性、可索引性 |
| geo-content | `agents/geo-content.md` | 内容质量、E-E-A-T、可读性、AI 内容检测 |
| geo-schema | `agents/geo-schema.md` | Schema 标记检测、验证、生成 |

**阶段 3：综合（顺序执行）**
1. 汇总所有子代理报告
2. 计算综合 GEO 评分（0-100）
3. 生成分优先级的整改计划
4. 输出客户级中文报告

### 评分方法

| 类别 | 权重 | 衡量方式 |
|----------|--------|-------------|
| AI 可引用性与可见性 | 25% | 段落评分、答案块质量、AI 爬虫访问权限 |
| 品牌权威信号 | 20% | 知乎、B站、百度百科/中文维基、微信公众号等平台提及；实体存在感 |
| 内容质量与 E-E-A-T | 20% | 专业性信号、原创数据、作者资历 |
| 技术基础 | 15% | SSR、Core Web Vitals、可抓取性、移动端、安全性 |
| 结构化数据 | 10% | Schema 完整度、JSON-LD 校验、富媒体结果资格 |
| 平台优化 | 10% | 国内平台就绪度（百度AI搜索、Kimi、DeepSeek 等） |

---

## 业务类型识别

分析首页特征：

| 类型 | 信号 |
|------|---------|
| **SaaS** | 定价页、"注册"、"免费试用"、"/app"、"/dashboard"、API 文档 |
| **本地服务** | 电话号码、地址、地图嵌入、服务范围 |
| **电商** | 商品页、购物车、"加入购物车"、价格元素、商品 schema |
| **内容站** | 博客、文章、作者署名、发布日期、文章 schema |
| **代理商** | 案例集、客户案例、"我们的服务"、客户 logo、客户评价 |
| **其他** | 默认 —— 应用通用 GEO 最佳实践 |

根据识别出的类型调整建议。本地服务需要 LocalBusiness schema 和地图平台（百度地图、高德）信息完善；SaaS 需要 SoftwareApplication schema 和对比页策略；电商需要 Product schema 和评价聚合。

---

## 子 Skill（14 个专项组件）

| # | Skill | 目录 | 用途 |
|---|-------|-----------|---------|
| 1 | geo-audit | `skills/geo-audit/` | 完整审计编排与评分 |
| 2 | geo-citability | `skills/geo-citability/` | 段落级 AI 引用就绪度 |
| 3 | geo-crawlers | `skills/geo-crawlers/` | AI 爬虫访问与 robots.txt（国内版爬虫名单） |
| 4 | geo-llmstxt | `skills/geo-llmstxt/` | llms.txt 标准分析与生成 |
| 5 | geo-brand-mentions | `skills/geo-brand-mentions/` | 国内平台品牌存在感（知乎、B站、百科、公众号等） |
| 6 | geo-platform-optimizer | `skills/geo-platform-optimizer/` | 国内 AI 搜索平台专项优化（含出海附录） |
| 7 | geo-schema | `skills/geo-schema/` | 面向 AI 发现的结构化数据 |
| 8 | geo-technical | `skills/geo-technical/` | 技术 SEO 基础（含百度站长、ICP 备案） |
| 9 | geo-content | `skills/geo-content/` | 内容质量与 E-E-A-T |
| 10 | geo-report | `skills/geo-report/` | 客户级交付物生成 |
| 11 | geo-report-pdf | `skills/geo-report-pdf/` | 带图表和评分的专业 PDF 报告 |
| 12 | geo-prospect | `skills/geo-prospect/` | 轻量 CRM 潜在客户管道管理 |
| 13 | geo-proposal | `skills/geo-proposal/` | 基于审计数据自动生成客户提案 |
| 14 | geo-compare | `skills/geo-compare/` | 月度增量追踪与进度报告 |

---

## 子代理（5 个并行工作者）

| 代理 | 文件 | 使用的 Skill |
|-------|------|-------------|
| geo-ai-visibility | `agents/geo-ai-visibility.md` | geo-citability、geo-crawlers、geo-llmstxt、geo-brand-mentions |
| geo-platform-analysis | `agents/geo-platform-analysis.md` | geo-platform-optimizer |
| geo-technical | `agents/geo-technical.md` | geo-technical |
| geo-content | `agents/geo-content.md` | geo-content |
| geo-schema | `agents/geo-schema.md` | geo-schema |

---

## 输出文件

所有命令生成结构化输出。**输出文件默认使用中文撰写**（代码、命令、
User-Agent 字符串保持原文）：

| 命令 | 输出文件 |
|---------|------------|
| `/geo-cn audit` | `GEO-AUDIT-REPORT.md` |
| `/geo-cn page` | `GEO-PAGE-ANALYSIS.md` |
| `/geo-cn citability` | `GEO-CITABILITY-SCORE.md` |
| `/geo-cn crawlers` | `GEO-CRAWLER-ACCESS.md` |
| `/geo-cn llmstxt` | `llms.txt`（可直接部署） |
| `/geo-cn brands` | `GEO-BRAND-MENTIONS.md` |
| `/geo-cn platforms` | `GEO-PLATFORM-OPTIMIZATION.md` |
| `/geo-cn schema` | `GEO-SCHEMA-REPORT.md` + 生成的 JSON-LD |
| `/geo-cn technical` | `GEO-TECHNICAL-AUDIT.md` |
| `/geo-cn content` | `GEO-CONTENT-ANALYSIS.md` |
| `/geo-cn report` | `GEO-CLIENT-REPORT.md`（可直接演示） |
| `/geo-cn report-pdf` | `GEO-REPORT.pdf`（带图表的专业 PDF） |
| `/geo-cn quick` | 内联摘要（不生成文件） |
| `/geo-cn prospect` | 更新 `~/.geo-prospects/prospects.json` |
| `/geo-cn proposal` | `~/.geo-prospects/proposals/<domain>-proposal-<date>.md` |
| `/geo-cn compare` | `~/.geo-prospects/reports/<domain>-monthly-<YYYY-MM>.md` |

---

## PDF 报告生成

`/geo-cn report-pdf <url>` 命令将 `GEO-AUDIT-REPORT.md` 转换为带样式的客户级 PDF。

### 依赖
- **pandoc** — `brew install pandoc`
- **Google Chrome** — `/Applications/Google Chrome.app/`（Mac 标准安装路径）

PDF 生成不需要 Python 依赖。

### PDF 包含内容
- **封面页** — 深蓝渐变、GEO 评分徽章、品牌/域名/日期/地点元数据
- **彩色评分表** — 含 `XX/100` 数值的单元格自动按 绿/蓝/黄/橙/红 着色
- **严重级别标记的发现项** — 严重/高/中/低 各节带彩色左边框提示块
- **章节自动分页** — 主要章节自动另起一页
- **代码块样式** — JSON schema 模板以深色等宽主题渲染

### 模板
位于 `~/.claude/skills/geo/templates/`：
- `geo-report-style.css` — 样式表（在此改颜色、字体、布局）
- `geo-report-template.html` — pandoc HTML 模板（在此改封面字段）

### 工作流程
1. 运行 `/geo-cn audit <url>` 生成 `GEO-AUDIT-REPORT.md`
2. 运行 `/geo-cn report-pdf` —— 从报告中提取元数据并执行：
   ```bash
   pandoc GEO-AUDIT-REPORT.md \
     --to html5 --standalone --embed-resources \
     --template ~/.claude/skills/geo/templates/geo-report-template.html \
     --css ~/.claude/skills/geo/templates/geo-report-style.css \
     --metadata brand_name="..." --metadata geo_score="..." \
     -o GEO-REPORT.html

   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
     --headless=new --disable-gpu --no-sandbox \
     --print-to-pdf="$(pwd)/GEO-REPORT.pdf" \
     --print-to-pdf-no-header --no-pdf-header-footer \
     --virtual-time-budget=5000 \
     "file://$(pwd)/GEO-REPORT.html"
   ```
3. 输出：当前目录下的 `GEO-REPORT.pdf`

---

## 质量门槛

- **抓取上限：** 每次审计最多 50 页（质量优先于数量）
- **超时：** 每页抓取 30 秒
- **速率限制：** 请求间隔 1 秒，最多 5 并发
- **Robots.txt：** 始终遵守，始终检查
- **重复检测：** 跳过内容相似度 >80% 的页面

---

## 快速上手示例

```
# 对网站做完整 GEO 审计
/geo-cn audit https://example.com

# 检查 AI 爬虫能否访问你的网站
/geo-cn crawlers https://example.com

# 给某个页面的 AI 可引用性打分
/geo-cn citability https://example.com/blog/best-article

# 为你的网站生成 llms.txt 文件
/geo-cn llmstxt https://example.com

# 获取 60 秒可见性快照
/geo-cn quick https://example.com

# 生成客户级报告
/geo-cn report https://example.com
```

---

## 作者与社区

- **作者：** simonsxxs（一个不会代码的AI极客）
- **微信交流群：** simonsxxs

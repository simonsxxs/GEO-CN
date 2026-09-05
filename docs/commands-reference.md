# 命令参考

本文档列出 geo-cn 工具包的全部命令。命令在 Claude Code 内使用 `/geo-cn` 前缀调用。`geo/SKILL.md` 中的主 skill 充当路由器：读取 `/geo-cn` 后的第一个参数，委派给 `skills/` 下对应的子 skill。所有命令以 URL 为主要参数；CRM 类命令操作域名或客户 ID。每个产出评分的命令都遵循 [scoring-methodology.md](scoring-methodology.md) 中的加权模型。`/geo-cn audit` 使用的并行子代理架构见 [architecture.md](architecture.md)。

---

## 命令分类

**审计** —— 整站与专项分析

| 命令 | 说明 |
|---------|-------------|
| `/geo-cn audit <url>` | 完整 GEO + SEO 审计（并行子代理） |
| `/geo-cn quick <url>` | 60 秒 GEO 可见性快照 |
| `/geo-cn citability <url>` | 单页 AI 引用就绪度评分（中文引擎） |
| `/geo-cn crawlers <url>` | 通过 robots.txt 和 meta 标签检查 AI 爬虫访问权限 |
| `/geo-cn llmstxt <url>` | 分析现有 llms.txt 或从零生成 |
| `/geo-cn brands <url>` | 扫描国内 AI 引用源平台上的品牌提及 |
| `/geo-cn platforms <url>` | 分平台就绪度评分（百度AI搜索、Kimi、DeepSeek、豆包、元宝、夸克/通义） |

**诊断** —— 定向技术与内容检查

| 命令 | 说明 |
|---------|-------------|
| `/geo-cn schema <url>` | 检测、验证并生成 Schema.org 结构化数据 |
| `/geo-cn technical <url>` | 技术 SEO 审计（含百度站长、ICP 备案检查） |
| `/geo-cn content <url>` | 内容质量与 E-E-A-T 评估 |

**报告** —— 可交付客户的成果物

| 命令 | 说明 |
|---------|-------------|
| `/geo-cn report <url>` | 生成客户级 Markdown GEO 报告（中文） |
| `/geo-cn report-pdf <url>` | 生成带图表与可视化的专业 PDF 报告 |

**接单** —— 客户与销售管道管理

| 命令 | 说明 |
|---------|-------------|
| `/geo-cn prospect <子命令>` | 管理销售管道中的潜在客户 |
| `/geo-cn proposal <域名>` | 基于审计数据自动生成中文客户提案 |
| `/geo-cn compare <域名>` | 月度增量报告，展示评分提升 |

---

## /geo-cn audit

使用 5 个并行子代理对网站执行全面的 GEO + SEO 审计。

**用法**

```
/geo-cn audit https://example.com
```

**做什么**

- 阶段 1（顺序）：抓取首页，识别业务类型（SaaS、本地服务、电商、内容站、代理商），从 sitemap 或内链抓取最多 50 个页面。
- 阶段 2（并行）：同时委派给 5 个专项子代理 —— AI 可见性、平台分析、技术 SEO、内容 E-E-A-T、Schema 标记。子代理流程见 [architecture.md](architecture.md)。
- 阶段 3（顺序）：把各子代理评分汇总为加权综合 GEO 评分（0-100）。加权公式见 [scoring-methodology.md](scoring-methodology.md)。
- 把每个问题按严重程度分级：严重 / 高 / 中 / 低。
- 产出按周划分的 30 天整改计划。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<url>` | 是 | 待审计网站的首页 URL |

**输出**

在当前目录写入 `GEO-AUDIT-REPORT.md`（中文）。内容包括：摘要、评分明细表、分类深入分析、按严重程度分级的问题清单、速赢项、逐周 30 天整改计划。终端同时打印摘要。

**什么时候用**

接触任何新客户或新网站时第一个跑；它是所有其他分析的入口。

---

## /geo-cn quick

输出 60 秒 GEO 可见性快照，不写任何文件。

**用法**

```
/geo-cn quick https://example.com
```

**做什么**

- 抓取首页和少量关键页面。
- 对主要 GEO 信号做轻量检查：AI 爬虫访问权限、llms.txt 是否存在、首页 schema、首屏内容的可引用性粗评。
- 产出近似 GEO 评分和一份影响最大的短板清单。
- 被 CRM 工作流中的 `/geo-cn prospect audit` 自动调用。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<url>` | 是 | 要快照的 URL |

**输出**

仅终端内联摘要，不写文件。通过 `/geo-cn prospect audit` 调用时，评分会存入客户记录。

**什么时候用**

在投入完整审计前做快速资格判断，或由 `/geo-cn prospect audit` 自动触发。

---

## /geo-cn citability

用五维度规则给单个页面的 AI 引用就绪度打分（针对中文内容设计）。

**用法**

```
/geo-cn citability https://example.com/blog/my-article
```

**做什么**

- 抓取页面，按 H2/H3 边界把内容切分为内容块。
- 按五个维度给每个块打分：答案块质量（30%）、段落自包含性（25%）、结构可读性（20%）、数据密度（15%）、独特性/原创数据（10%）。
- 找出最强的 3 个块和最弱的 3 个块。
- 给每个低于 60 分的块生成具体改写建议（含建议的开头句）。规则细节见 [scoring-methodology.md](scoring-methodology.md)。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<url>` | 是 | 要评分的具体页面 URL |

**输出**

写入 `GEO-CITABILITY-SCORE.md`。内容包括：整体可引用性评分、加权评分表、最强/最弱块分析（含原文摘录）、改写建议、分节评分表。

**什么时候用**

任何内容页发布前跑一遍，或用来排定「哪些旧页面最值得为 AI 引用重写」的优先级。

---

## /geo-cn crawlers

分析哪些 AI 爬虫能访问网站，并给出推荐的 robots.txt 配置。

**用法**

```
/geo-cn crawlers https://example.com
```

**做什么**

- 抓取并解析 `robots.txt`，把每条 User-agent 规则映射到已知 AI 爬虫名单（国内为主：Bytespider、Baiduspider、ToutiaoSpider 等；国外爬虫作对照参考）。
- 抽查关键页面的 `<meta name="robots">` 覆盖和 `X-Robots-Tag` HTTP 头。
- 检查 `/llms.txt` 是否存在。
- 评估关键内容是否依赖 JavaScript 渲染（AI 爬虫不执行 JS）。
- 按三个层级评估爬虫可达性：Tier 1（AI 搜索/引用型爬虫，建议放行）、Tier 2（传统搜索蜘蛛 —— 国内 AI 搜索的索引底座，必须放行）、Tier 3（纯训练型爬虫，策略自选）。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<url>` | 是 | 域名根 URL |

**输出**

写入 `GEO-CRAWLER-ACCESS.md`。内容包括：逐爬虫访问状态表、AI 可见性评分（0-100）、关键问题清单、一份可直接粘贴的 robots.txt 配置块。

**什么时候用**

客户反馈「AI 搜索里搜不到我们」时的快速独立检查，或 robots.txt 改动上线前的验证。

---

## /geo-cn llmstxt

分析现有 `llms.txt` 的质量，或在文件不存在时从零生成一个新文件。

**用法**

```
/geo-cn llmstxt https://example.com
```

**做什么**

- 抓取 `https://example.com/llms.txt` 和 `llms-full.txt`，检查 HTTP 状态。
- **分析模式**（文件存在）：校验格式（H1 标题、引用块简介、H2 分节、绝对 URL、条目描述、关键事实、联系方式）；按完整性（40%）、准确性（35%）、实用性（25%）打分；找出缺失的重要页面。
- **生成模式**（文件不存在）：抓取 sitemap 和首页，按页面类型排优先级，为入选页面写 10-30 字描述，收集关键业务事实，组装成可直接部署的完整 `llms.txt`。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<url>` | 是 | 域名根 URL |

**输出**

- 分析模式：写入 `GEO-LLMSTXT-ANALYSIS.md`，含校验结果、缺失页面和建议的更新文件。
- 生成模式：写入可直接部署的 `llms.txt` 文件，以及一份简述页面取舍理由的 `GEO-LLMSTXT-GENERATION.md`。

**什么时候用**

任何网站都可以跑：校验现有 `llms.txt`，或生成新文件。截至 2026 年初，拥有 `llms.txt` 的网站不足 5%，是一个容易拿到的速赢项。

---

## /geo-cn brands

扫描品牌在国内 AI 系统用于实体识别和引用决策的平台上的提及情况。

**用法**

```
/geo-cn brands https://example.com
```

**做什么**

- 检查品牌在知乎（机构号、第三方讨论、推荐类问题出现率）、B站（官方号、第三方视频提及）、中文维基/百度百科（词条是否存在、质量）、微信公众号（搜狗微信入口可查的提及）上的存在感。
- 补充扫描：CSDN、掘金、V2EX、GitHub、Gitee、小红书、新闻媒体等。
- 计算综合品牌权威度评分：知乎 25%、B站 25%、中文维基/百度百科 20%、微信公众号 15%、其他平台 15%。权重为基于公开信息的合理推断值，详见 [scoring-methodology.md](scoring-methodology.md)。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<url>` | 是 | 域名 URL（品牌名从站点推断） |

**输出**

写入 `GEO-BRAND-MENTIONS.md`。内容包括：品牌权威度评分（0-100）、分平台明细表、情感倾向评估、竞品对照表（如能识别竞品）、按时间跨度分组的改进建议（第 1-2 周、第 1-3 月、第 3-12 月）。

**什么时候用**

网站内容技术层面没问题、但就是不出现在 AI 生成的推荐里时；或作为实体建设策略的一部分。

---

## /geo-cn platforms

逐一审计网站在各国内 AI 搜索平台上的就绪度，产出分平台评分。

**用法**

```
/geo-cn platforms https://example.com
```

**做什么**

- 对 6 个平台分别执行检查清单和评分规则：百度AI搜索、Kimi、DeepSeek、豆包、元宝、夸克/通义。
- 每个平台给出来源选择机制说明、优化清单和百分制评分表；机制未公开的平台如实标注「未公开」，分值为推断值，不做臆测。
- 产出跨平台协同项清单：一次投入、六个平台共同受益的通用动作。
- 面向海外站点的场景另有「出海附录」（ChatGPT、Perplexity、Gemini 等国外平台检查）。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<url>` | 是 | 网站首页 URL |

**输出**

写入 `GEO-PLATFORM-OPTIMIZATION.md`。内容包括：综合得分、分平台评分表、分平台差距分析与具体动作、分优先级整改计划（速赢 / 中期 / 战略）。平台权重见 [scoring-methodology.md](scoring-methodology.md)。

**什么时候用**

需要知道网站在哪个具体 AI 平台上表现落后时，或用来制定分平台优化路线图。

---

## /geo-cn schema

检测网站全部结构化数据，按 Schema.org 规范校验，并为缺失或不完整的 schema 生成可直接粘贴的 JSON-LD 代码块。

**用法**

```
/geo-cn schema https://example.com
```

**做什么**

- 用 `fetch_page.py`（而非会剥离 `<head>` 内容的 WebFetch）抓取原始 HTML，提取全部 JSON-LD、Microdata、RDFa 块。
- 逐一校验：JSON 语法、`@type` 合法性、必填属性、推荐属性、`sameAs` 链接、URL 有效性、嵌套关系、是否服务端渲染。
- 检查 GEO 关键 schema 类型：Organization、LocalBusiness、带作者的 Article、Product、FAQPage、SoftwareApplication、带 SearchAction 的 WebSite、BreadcrumbList。
- 按优先级平台清单审计 `sameAs` 属性（百度百科/中文维基、知乎、B站、公众号等国内平台优先）。
- 用 `@graph` 模式为缺失或不完整的 schema 生成完整 JSON-LD 代码块。schema 评分如何计入综合评分见 [scoring-methodology.md](scoring-methodology.md)。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<url>` | 是 | 要审计的页面或域名 URL |

**输出**

写入 `GEO-SCHEMA-REPORT.md`。内容包括：schema 评分（0-100）、已检测 schema 表、逐属性校验结果、缺失 schema 清单、sameAs 审计表、可直接粘贴的 JSON-LD 代码块（含实施说明）。

**什么时候用**

给开发团队开一张自包含的实施工单，或 CMS 迁移后验证 schema 质量。

---

## /geo-cn technical

按八大类目执行技术 SEO 审计，重点关注服务端渲染和 AI 爬虫可达性，并增补国内特色检查（百度搜索资源平台、头条站长平台、ICP 备案）。

**用法**

```
/geo-cn technical https://example.com
```

**做什么**

- 可抓取性（15 分）：robots.txt 合法性、AI 爬虫访问权限、XML sitemap、抓取深度、noindex 指令。
- 可索引性（12 分）：canonical 标签、重复内容（www/HTTP/尾斜杠）、分页、hreflang。
- 安全性（10 分）：HTTPS 强制跳转、HSTS、`X-Content-Type-Options`、`X-Frame-Options`、`Referrer-Policy`、CSP。
- URL 结构（8 分）：可读 URL、层级逻辑、重定向链、参数处理。
- 移动端优化（10 分）：viewport 标签、响应式布局、点击区域尺寸、字体可读性。
- Core Web Vitals（15 分）：LCP < 2.5s、INP < 200ms、CLS < 0.1（2026 年阈值）。
- 服务端渲染（15 分）：对比 `curl` 输出与渲染后 DOM；标记 AI 爬虫读不到的前端渲染内容。
- 页面速度与服务器性能（15 分）：TTFB、页面体积、图片优化、JS 包体积、压缩、缓存、CDN。技术分如何计入综合评分见 [scoring-methodology.md](scoring-methodology.md)。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<url>` | 是 | 域名根 URL |

**输出**

写入 `GEO-TECHNICAL-AUDIT.md`。内容包括：技术评分（0-100）、分类评分表（通过/警告/未通过）、AI 爬虫访问表、关键问题清单、警告与建议。

**什么时候用**

网站内容不错但 AI 可见性差时；或产出面向开发者的整改清单。

---

## /geo-cn content

通过 E-E-A-T 框架（经验、专业、权威、可信）评估内容质量，并评估 AI 可引用性与话题权威度。

**用法**

```
/geo-cn content https://example.com
```

**做什么**

- 按 25 分制给四个 E-E-A-T 维度分别打分：经验（第一人称叙述、原创数据、案例）、专业（作者资历、技术深度、方法论、有数据支撑的论断）、权威（被引用情况、媒体报道、获奖、百科词条）、可信（联系方式、隐私政策、HTTPS、编辑规范、论断准确性）。
- 应用话题权威度修正：20+ 篇强聚集文章 +10，话题下不足 5 篇最多 −5。
- 评估每页内容时效性（3 个月内到无日期/24 个月以上）。
- 标记低质量 AI 生成内容特征（套话堆砌、无原创见解、过度含糊表述），识别高质量信号。
- 按页面类型核对字数基准和面向 AI 提取的段落结构（中文段落以 200-350 字为佳，推断值）。内容分如何计入综合评分见 [scoring-methodology.md](scoring-methodology.md)。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<url>` | 是 | 域名根 URL（分析首页加关键内容页） |

**输出**

写入 `GEO-CONTENT-ANALYSIS.md`。内容包括：内容评分（0-100）、E-E-A-T 明细表、已分析页面表、分维度详细发现、含改写建议的内容质量问题、AI 内容风险、时效性评估、最易/最难被引用的段落、内容缺口建议、E-E-A-T 改进步骤。

**什么时候用**

网站技术基础良好、但不被 AI 系统引用时 —— 这通常指向内容质量问题。

---

## /geo-cn report

把所有审计 skill 的产出汇总成一份专业的、面向客户的中文 Markdown 报告。

**用法**

```
/geo-cn report https://example.com
```

**做什么**

- 读取当前目录已有的 `GEO-*.md` 审计文件；缺哪个自动补跑。
- 计算综合 GEO 就绪度评分：AI 平台就绪度 25%、内容 E-E-A-T 25%、技术基础 20%、Schema 15%、品牌权威 15%。见 [scoring-methodology.md](scoring-methodology.md)。
- 把所有技术发现翻译成面向老板和市场负责人的商业语言，而不是开发者语言。
- 产出 12 个结构化章节：摘要、评分仪表盘、AI 可见性仪表盘（分平台）、AI 爬虫访问表、品牌权威分析、可引用性分析（Top 5 / Bottom 5 页面）、技术健康摘要、schema 状态、llms.txt 状态、分优先级整改计划（速赢 / 中期 / 战略）、竞品对比（如分析过竞品）、术语附录。
- 包含与评分提升挂钩的保守流量与营收影响估算。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<url>` | 是 | 域名 URL；自动消费当前目录已有的审计文件 |

**输出**

写入 `GEO-CLIENT-REPORT.md`。报告 3,000-6,000 字，自包含，无需再编辑即可交付。

**什么时候用**

跑完整套审计后产出最终交付物，或每个月度服务周期结束时。

---

## /geo-cn report-pdf

把 GEO 审计数据转成专业排版的 PDF，带评分仪表盘、彩色评分表和分级发现块。

**用法**

```
/geo-cn report-pdf https://example.com
```

**做什么**

- 检查当前目录是否有 `GEO-CLIENT-REPORT.md` 或 `GEO-AUDIT-REPORT.md`；都没有则先跑一次完整审计。
- 从 Markdown 报告提取评分、平台就绪度、爬虫状态、发现项和整改项。
- 用 pandoc + 内置 HTML 模板/CSS 生成自包含的 `GEO-REPORT.html`，再用 Chrome 无头模式打印为 PDF（不依赖 Python 库）。
- 评分单元格自动按分值着色（绿 80+、蓝 60-79、黄 40-59、红 40 以下）。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<url>` | 是 | 域名 URL；用于定位或生成审计数据 |

**输出**

在当前目录写入 `GEO-REPORT.pdf`。PDF 包含：带评分徽章的封面页、摘要、评分明细表、AI 平台就绪度、爬虫访问彩色表、按严重程度分级的关键发现、分优先级整改计划、方法论/术语附录。完成后报告文件路径和大小。

**什么时候用**

交付物需要直接发微信/邮件给客户、对方期待一份精致文档而不是 Markdown 文件时。

---

## /geo-cn prospect

轻量 CRM：跟踪潜在客户从初次发现到签约的全过程。

**用法**

```
/geo-cn prospect new <域名>
/geo-cn prospect list [<状态>]
/geo-cn prospect show <id或域名>
/geo-cn prospect audit <id或域名>
/geo-cn prospect note <id或域名> "<备注内容>"
/geo-cn prospect status <id或域名> <新状态>
/geo-cn prospect won <id或域名> <月合同额>
/geo-cn prospect lost <id或域名> "<丢单原因>"
/geo-cn prospect pipeline
```

**做什么**

- 把所有客户数据持久化在 `~/.geo-prospects/prospects.json`，记录包含 ID、公司、域名、状态、GEO 评分、审计文件路径、提案文件路径、月合同额和带时间戳的备注。
- 跟踪五个管道阶段：`lead`（线索）、`qualified`（已审计）、`proposal`（已发提案）、`won`（已签约）、`lost`（已丢单）。
- `prospect audit` 调用 `/geo-cn quick` 并把评分存入客户记录。
- `prospect pipeline` 打印面向营收的管道汇总：已签约月收入（MRR）、管道价值和每条记录的建议下一步动作。
- 所有子命令在终端打印确认信息和当前客户状态；除审计快照和提案外不写外部文件。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<子命令>` | 是 | `new`、`list`、`show`、`audit`、`note`、`status`、`won`、`lost`、`pipeline` |
| `<id或域名>` | 视情况 | 客户 ID（如 `PRO-001`）或域名 |
| `<状态>` | `status`、`list` 时 | 管道阶段：`lead`、`qualified`、`proposal`、`won`、`lost` |
| `<月合同额>` | `won` 时 | 数字，月合同金额（元） |
| `"<内容>"` | `note`、`lost` 时 | 自由文本备注或丢单原因 |

**输出**

更新 `~/.geo-prospects/prospects.json`。审计快照存到 `~/.geo-prospects/audits/`。所有子命令都有终端输出。

**什么时候用**

管理 GEO 接单的销售管道，跨会话跟踪客户历史。

---

## /geo-cn proposal

基于审计数据自动生成完全定制的中文 GEO 服务提案。

**用法**

```
/geo-cn proposal <域名>
/geo-cn proposal <域名> --tier basic|standard|premium --client-name "客户名" --monthly 金额
```

**示例**

```
/geo-cn proposal example.com
/geo-cn proposal example.com --tier standard --client-name "某某科技"
/geo-cn proposal ~/.geo-prospects/audits/example.com-2026-03-12.md
```

**做什么**

- 从 `~/.geo-prospects/audits/<域名>*.md` 加载最近一次审计文件（没有则建议先跑 `/geo-cn quick`）。
- 根据 GEO 评分选择推荐服务档位：0-40 分 → 旗舰版；41-60 分 → 标准版；61-75 分 → 基础版。
- 填充 12 节提案模板：摘要、市场背景表、审计发现、三档服务包及报价（基础版 ¥8,000/月、标准版 ¥18,000/月、旗舰版 ¥35,000/月）、ROI 测算表、六个月服务时间表、投入汇总、合作条款。
- 把客户记录状态更新为 `proposal` 并保存提案文件路径。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<域名>` | 是 | 域名或审计文件路径 |
| `--tier` | 否 | 强制指定档位，不用评分自动推荐 |
| `--client-name` | 否 | 覆盖自动识别的公司名 |
| `--monthly` | 否 | 覆盖估算的月合同额 |

**输出**

写入 `~/.geo-prospects/proposals/<域名>-proposal-<日期>.md`。终端打印确认信息和推荐档位、报价。提案无需再编辑即可发送。

**什么时候用**

完成客户初审计、GEO 评分显示明确商机（低于 75 分）后立刻使用。

---

## /geo-cn compare

生成月度增量报告：对比基线审计与当前审计，向客户展示评分提升。

**用法**

```
/geo-cn compare <域名>
/geo-cn compare <基线文件> <当前文件>
/geo-cn compare <域名> --month 2026-03
```

**做什么**

- 在 `~/.geo-prospects/audits/` 中按域名匹配审计文件；最早的作基线，最新的作当前。只有一份时，跑一个新的快速审计作为当前快照。
- 从两份文件中提取综合 GEO 评分、六个分类评分、各平台评分和 AI 爬虫状态。
- 计算增量并标注趋势符号（▲▲ 显著提升、▲ 提升、── 持平、▼ 下降、▼▼ 明显下降）。
- 跟踪速赢项、中期项、战略项整改计划的完成状态。
- 包含六个月趋势表和保守的业务影响估算（AI 引用概率变化、爬虫覆盖变化、预估流量价值）。

**参数**

| 参数 | 必填 | 说明 |
|----------|----------|-------------|
| `<域名>` | 是（或两个文件路径） | 域名，或显式指定基线与当前审计文件路径 |
| `--month` | 否 | 报告文件名使用的月份标签 |

**输出**

写入 `~/.geo-prospects/reports/<域名>-monthly-<YYYY-MM>.md`。终端打印摘要：评分变化、速赢项完成率、新发现问题数、六个月目标是否在轨。

**什么时候用**

每月 1 号为每个活跃客户跑一次，产出那份「向客户证明服务费花得值」的进度报告。

---

## 已知差异

以下是 `geo/SKILL.md` 与 `skills/` 目录之间的已知差异：

- **`/geo-cn quick`**：在 `geo/SKILL.md` 的快速参考表中列出，并被 `geo-prospect` 和 `geo-compare` 引用为真实行为，但没有独立的 `skills/geo-quick/SKILL.md`。快速扫描行为通过 `geo/SKILL.md` 的编排指令实现，本文档据此描述。
- **`/geo-cn page`**：在 `geo/SKILL.md` 的快速参考表中列出（单页面深度 GEO 分析，产出 `GEO-PAGE-ANALYSIS.md`），但没有 `skills/geo-page/SKILL.md`，不存在独立实现。上文未收录该命令的详细文档。

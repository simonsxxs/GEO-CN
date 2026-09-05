# Skill、子代理、脚本与 Schema 模板

本参考手册描述 geo-cn 工具包的每个组成部分。工具包为网站做生成式引擎优化（GEO）—— 让内容能被国内 AI 搜索平台（百度AI搜索、Kimi、DeepSeek、豆包、元宝、夸克/通义）发现并引用 —— 同时保留传统 SEO 基础。结构上是一个编排器主 skill、14 个子 skill、5 个并行子代理、若干 Python 辅助脚本和 6 个 JSON-LD schema 模板。

完整斜杠命令参考见 [commands-reference.md](commands-reference.md)，完整审计时的并行子代理流程见 [architecture.md](architecture.md)。

---

## 编排器

- **geo-cn**（`geo/SKILL.md`）—— 所有 GEO 命令的入口。识别业务类型，为单命令分派子 skill，并协调完整审计的三阶段流程：发现、并行子代理委派、评分综合。产出按六个类目加权的综合 GEO 评分（0-100）。

---

## 子 Skill

### geo-audit

**用途：** 编排一次完整的 GEO + SEO 审计：跑发现阶段，委派 5 个并行子代理，把它们的评分汇总成一个综合 GEO 评分。

**输入：** 一个 URL。可选预抓取的页面数据。

**输出：** `GEO-AUDIT-REPORT.md` —— 综合评分、分类明细、按严重程度分级的问题清单（严重 / 高 / 中 / 低）、30 天整改计划、已分析页面附录。

**评分权重：**
- AI 可引用性 25%、品牌权威 20%、内容 E-E-A-T 20%、技术 GEO 15%、结构化数据 10%、平台优化 10%

**依赖：** 委派给全部 5 个子代理（`geo-ai-visibility`、`geo-platform-analysis`、`geo-technical`、`geo-content`、`geo-schema`）。

命令文档见 [commands-reference.md](commands-reference.md) 的 `/geo-cn audit`。

---

### geo-citability

**用途：** 按 0-100 分给单个内容段落的 AI 引用就绪度打分，衡量 AI 系统多大可能原样摘录并引用这段内容。评分引擎针对中文内容设计。

**输入：** 一个 URL（用 WebFetch 抓取）。

**输出：** `GEO-CITABILITY-SCORE.md` —— 分节评分、最易被引用的段落、最弱内容块及改写建议、可引用覆盖率。

**评分维度（每段）：** 答案块质量（30%）、自包含性（25%）、结构可读性（20%）、数据密度（15%）、独特性（10%）。

**关键阈值：** 最易被 AI 引用的中文段落为 200-350 字（推断值）、自成一体、事实密度高、在前 1-2 句直接回答问题。

命令文档见 [commands-reference.md](commands-reference.md) 的 `/geo-cn citability`。

---

### geo-crawlers

**用途：** 通过解析 `robots.txt`、meta robots 标签和 HTTP `X-Robots-Tag` 头，审计哪些 AI 爬虫能访问网站。产出覆盖三个层级的完整访问地图，国内爬虫名单为主（Bytespider、Baiduspider、ToutiaoSpider 等），国外爬虫作对照参考。

**输入：** 一个域名 URL。

**输出：** `GEO-CRAWLER-ACCESS.md` —— 逐爬虫状态（放行 / 屏蔽 / 未提及）、AI 可见性评分、推荐的 robots.txt 配置、JavaScript 渲染评估。

**爬虫层级：**
- Tier 1（AI 搜索/引用型，建议放行）：9 个爬虫
- Tier 2（传统搜索蜘蛛 —— 国内 AI 搜索的索引底座，必须放行）：6 个爬虫
- Tier 3（纯训练型，策略自选）：6 个爬虫

命令文档见 [commands-reference.md](commands-reference.md) 的 `/geo-cn crawlers`。

---

### geo-llmstxt

**用途：** 分析现有 `llms.txt` 的格式合规性与完整性，或通过抓取网站从零生成新文件。`llms.txt` 标准向 AI 系统明确提供站点结构与关键页面指引。

**输入：** 一个域名 URL。按文件是否存在分别进入分析模式或生成模式。

**输出（分析模式）：** `GEO-LLMSTXT-ANALYSIS.md` —— 格式校验表、缺失页面、llms.txt 总分（完整性 40%、准确性 35%、实用性 25%）。

**输出（生成模式）：** 可直接部署的 `llms.txt` 文件，以及说明页面取舍理由的 `GEO-LLMSTXT-GENERATION.md`。

**依赖：** `scripts/llmstxt_generator.py` 提供校验与生成辅助。

命令文档见 [commands-reference.md](commands-reference.md) 的 `/geo-cn llmstxt`。

---

### geo-brand-mentions

**用途：** 扫描品牌在国内 AI 模型用于实体识别和引用决策的平台上的存在感，按平台加权产出品牌权威度评分。

**输入：** 品牌名、域名 URL、行业（未提供时从站点收集）。

**输出：** `GEO-BRAND-MENTIONS.md` —— 分平台评分（知乎 25%、B站 25%、中文维基/百度百科 20%、微信公众号 15%、其他 15%）、情感倾向评估、综合品牌权威度评分、分优先级建议。

**核心洞察：** 品牌提及与 AI 可见性的相关性约为传统外链的 3 倍（Ahrefs 2025 年 12 月对 75,000 个品牌的研究，国外平台数据）。国内平台权重为基于公开信息的合理推断值，报告中需向读者说明。

**依赖：** `scripts/brand_scanner.py` 提供平台检查框架。

命令文档见 [commands-reference.md](commands-reference.md) 的 `/geo-cn brands`。

---

### geo-platform-optimizer

**用途：** 逐一审计网站在各国内 AI 搜索平台上的就绪度 —— 不同平台的来源选择机制不同，通用优化打不满分。

**输入：** 一个 URL 和网站的主话题或行业。

**输出：** `GEO-PLATFORM-OPTIMIZATION.md` —— 百度AI搜索、Kimi、DeepSeek、豆包、元宝、夸克/通义六个平台的分平台评分与差距清单；跨平台优先级行动计划。机制未公开的平台如实标注「未公开」，分值为推断值。面向海外站点的场景另有「出海附录」。

命令文档见 [commands-reference.md](commands-reference.md) 的 `/geo-cn platforms`。

---

### geo-schema

**用途：** 检测、验证并生成 Schema.org 结构化数据（优先 JSON-LD）。结构化数据是 AI 模型识别和信任实体的主要机器可读信号。

**输入：** 一个 URL。用 `scripts/fetch_page.py` 抓取含 `<head>` 内容的原始 HTML（WebFetch 会剥离这部分）。

**输出：** `GEO-SCHEMA-REPORT.md` —— 已检测 schema 及校验结果、`sameAs` 实体链接审计、过时 schema 标记，以及可直接粘贴的 JSON-LD 代码块。

**GEO 关键 schema：** Organization + `sameAs`、Article + Author（Person）、speakable 属性、BreadcrumbList、WebSite + SearchAction。

**依赖：** `scripts/fetch_page.py`（原始 HTML 提取）；`schema/*.json` 模板（作为生成参考）。

命令文档见 [commands-reference.md](commands-reference.md) 的 `/geo-cn schema`。

---

### geo-technical

**用途：** 按八大类目审计技术健康度，重点关注独有影响 AI 爬虫可见性的因素：服务端渲染和 AI 爬虫访问。增补国内特色检查：百度搜索资源平台、头条站长平台、ICP 备案。

**输入：** 首页 URL 加 2-3 个关键内页。

**输出：** `GEO-TECHNICAL-AUDIT.md` —— 分类评分、AI 爬虫访问表、SSR 评估、Core Web Vitals 风险（LCP / INP / CLS）、安全响应头、移动端优化状态。

**评分类目（满分）：** 服务端渲染 15、Core Web Vitals 15、可抓取性 15、可索引性 12、安全性 10、移动端 10、页面速度 15、URL 结构 8。

**关键检查：** AI 爬虫不执行 JavaScript。没有 SSR 的纯前端 SPA，在 AI 爬虫眼里就是一个空页面。

命令文档见 [commands-reference.md](commands-reference.md) 的 `/geo-cn technical`。

---

### geo-content

**用途：** 通过 E-E-A-T 框架（经验、专业、权威、可信）评估内容质量，衡量内容深度、可读性、AI 内容迹象和话题权威度。

**输入：** 一个 URL（用 WebFetch 抓取）。

**输出：** `GEO-CONTENT-ANALYSIS.md` —— E-E-A-T 评分（各 25 分）、内容指标表、AI 内容评估、话题权威度评级、时效性评估、改写建议。

**评分修正：** 话题权威度在 100 分制 E-E-A-T 基础分上加 +10 到 −5 分。

命令文档见 [commands-reference.md](commands-reference.md) 的 `/geo-cn content`。

---

### geo-report

**用途：** 把所有审计子 skill 的产出汇总成一份面向客户（老板，而非开发者）的中文交付物 —— 技术发现全部翻译成商业影响和钱的说法。

**输入：** `geo-platform-optimizer`、`geo-schema`、`geo-technical`、`geo-content` 的输出文件，可选 `geo-llmstxt` 和 `geo-brand-mentions` 的输出。

**输出：** `GEO-CLIENT-REPORT.md` —— 摘要、GEO 就绪度评分、AI 可见性仪表盘、爬虫访问表、品牌权威表、可引用性分析、技术健康摘要、schema 状态、含工作量和平台影响的整改计划、完整术语附录。目标篇幅 3,000-6,000 字。

命令文档见 [commands-reference.md](commands-reference.md) 的 `/geo-cn report`。

---

### geo-report-pdf

**用途：** 用 pandoc + Chrome 无头模式把 GEO 审计数据转成专业排版的客户级 PDF。包含评分仪表盘、彩色评分表和分级发现块。

**输入：** 当前目录已有的 `GEO-AUDIT-REPORT.md` 或 `GEO-CLIENT-REPORT.md`。传入 URL 时先跑完整审计。

**输出：** `GEO-REPORT.pdf` —— 带评分徽章的封面页、评分明细、AI 平台就绪度、爬虫访问彩色表、按严重程度分级的发现、整改计划、方法论附录。

**依赖：** pandoc（`brew install pandoc`）和 macOS 标准路径下的 Google Chrome；无 Python 依赖。样式模板在 `templates/` 目录。

命令文档见 [commands-reference.md](commands-reference.md) 的 `/geo-cn report-pdf`。

---

### geo-prospect

**用途：** 轻量 CRM：管理 GEO 接单的销售管道，五个阶段（lead 线索 → qualified 已审计 → proposal 已发提案 → won 已签约 → lost 已丢单）。全部数据持久化在 `~/.geo-prospects/prospects.json`。

**输入：** 通过子命令录入的域名、联系方式、状态更新和备注。

**输出：** `prospects.json` 更新；审计快照存 `~/.geo-prospects/audits/`；终端打印管道汇总表。

**关键子命令：** `new`、`list`、`show`、`audit`、`note`、`status`、`won`、`lost`、`pipeline`。

**依赖：** `scripts/crm_dashboard.py` 提供终端看板（需要 `pip install rich`）；`scripts/webapp/` 提供网页看板（Flask + HTMX）。

命令文档见 [commands-reference.md](commands-reference.md) 的 `/geo-cn prospect`。

---

### geo-proposal

**用途：** 基于审计数据自动生成中文客户提案，含摘要、评分明细、三档服务包与报价、ROI 测算和服务时间表。

**输入：** 域名或已有审计文件路径。如客户在 `~/.geo-prospects/prospects.json` 中有记录则自动读取。

**输出：** `~/.geo-prospects/proposals/<域名>-proposal-<日期>.md` —— 一份可直接发送的完整中文提案。同时把客户记录状态更新为 `proposal`。

**档位推荐逻辑：** 评分 0-40 → 旗舰版（¥35,000/月）；41-60 → 标准版（¥18,000/月）；61-75 → 基础版（¥8,000/月）。

命令文档见 [commands-reference.md](commands-reference.md) 的 `/geo-cn proposal`。

---

### geo-compare

**用途：** 生成月度增量报告，对比两次 GEO 审计（基线 vs 当前），跟踪全类目评分提升和整改项完成状态。

**输入：** 一个域名或两个审计文件路径。只给域名时从 `~/.geo-prospects/audits/` 按日期排序读取。

**输出：** `~/.geo-prospects/reports/<域名>-monthly-<YYYY-MM>.md` —— 评分进度条、前后对比表、平台与爬虫增量表、整改计划状态、本月成绩、新发现问题、六个月趋势。

命令文档见 [commands-reference.md](commands-reference.md) 的 `/geo-cn compare`。

---

## 并行子代理

这 5 个代理在 `/geo-cn audit` 期间同时运行，缩短总耗时。每个返回一段结构化的 markdown 报告和一个计入综合 GEO 评分的类目分（0-100）。并行流程图见 [architecture.md](architecture.md)。

### geo-ai-visibility

**文件：** `agents/geo-ai-visibility.md`

**角色：** GEO 专家，覆盖权重最高的四个 AI 可见性维度。

**何时派发：** `/geo-cn audit` 阶段 2 开始时。

**做什么：** 按五维度规则给每个内容块打可引用性分，解析 `robots.txt` 中的 AI 爬虫规则，校验 `llms.txt` 格式与完整性，扫描品牌在知乎、B站、百科、公众号等国内平台上的存在感。

**返回：** AI 可见性评分 = 可引用性（35%）+ 品牌提及（30%）+ 爬虫访问（25%）+ llms.txt（10%）。

**使用的子 skill：** geo-citability、geo-crawlers、geo-llmstxt、geo-brand-mentions。

---

### geo-platform-analysis

**文件：** `agents/geo-platform-analysis.md`

**角色：** 平台优化专家。

**何时派发：** `/geo-cn audit` 阶段 2 开始时（与其他代理并行）。

**做什么：** 用各平台专用评分规则和信号检查，评估网站对六个国内 AI 搜索平台（百度AI搜索、Kimi、DeepSeek、豆包、元宝、夸克/通义）的就绪度。

**返回：** 分平台评分（各 0-100）和平台就绪度平均分；跨平台协同动作。

**使用的子 skill：** geo-platform-optimizer。

---

### geo-technical

**文件：** `agents/geo-technical.md`

**角色：** 技术 SEO 专家。

**何时派发：** `/geo-cn audit` 阶段 2 开始时（与其他代理并行）。

**做什么：** 抓取原始 HTML 和响应头；审计 SSR 与 CSR 渲染差异（权重最高的检查）、可抓取性、meta 标签、安全响应头、Core Web Vitals 风险指标、移动端优化、URL 结构，以及 ICP 备案、百度站长平台接入等国内特色项。

**返回：** 技术评分（0-100）及分类明细；SSR 严重程度评级（严重 / 高 / 中 / 低）。

**使用的子 skill：** geo-technical。

---

### geo-content

**文件：** `agents/geo-content.md`

**角色：** 内容质量专家。

**何时派发：** `/geo-cn audit` 阶段 2 开始时（与其他代理并行）。

**做什么：** 按四个维度评估 E-E-A-T（各 25 分），统计字数、可读性、标题结构和内链，检测 AI 内容质量信号，评估话题权威度和内容时效性。

**返回：** 内容评分（0-100）；E-E-A-T 明细；AI 内容评估标签。

**使用的子 skill：** geo-content。

---

### geo-schema

**文件：** `agents/geo-schema.md`

**角色：** Schema 标记专家。

**何时派发：** `/geo-cn audit` 阶段 2 开始时（与其他代理并行）。

**做什么：** 用 `fetch_page.py` 抓取原始 HTML，检测全部 JSON-LD / Microdata / RDFa 块，按 Schema.org 规范逐一校验，审计 `sameAs` 实体链接，标记过时或 JS 注入的 schema，并为缺失的 schema 生成可直接粘贴的 JSON-LD 模板。

**返回：** Schema 评分（0-100）；校验过的 schema 清单；生成的 JSON-LD 代码块。

**使用的子 skill：** geo-schema。

---

## Python 脚本

| 脚本 | 用途 | 使用者 |
|--------|---------|---------|
| `scripts/fetch_page.py` | 抓取 URL 并返回结构化数据：原始 HTML、meta 标签、标题结构、中文字符数（char_count）、解析出的 JSON-LD 块。绕开 WebFetch 的 markdown 转换，保留 `<head>` 内容。 | geo-schema（skill + agent）、geo-technical |
| `scripts/citability_scorer.py` | 中文 AI 可引用性评分引擎：按中文字符数计量，识别中文定义句式、代词密度、按中文标点切句、识别中文金额与具名来源，五个加权维度打分。提供可调用的 `score_passage()` 函数。 | geo-citability |
| `scripts/brand_scanner.py` | 检查品牌在国内 AI 引用源平台（知乎、B站、百科、公众号等）上的存在感。提供分平台检查函数和基于 WebFetch 的验证指引。依赖 `requests` 和 `beautifulsoup4`。 | geo-brand-mentions |
| `scripts/llmstxt_generator.py` | 按规范校验现有 `llms.txt`（H1 标题、引用块简介、H2 分节、绝对 URL、描述），并从站点抓取数据生成新文件。 | geo-llmstxt |
| `scripts/crm_dashboard.py` | 用 rich 渲染客户 CRM 终端看板。读取 `~/.geo-prospects/prospects.json`，展示管道阶段、月收入（MRR）和客户详情。依赖 `rich`。 | geo-prospect |
| `scripts/webapp/app.py` | CRM 网页看板（Flask + HTMX）。在浏览器中查看客户列表、详情、改状态、加备注。依赖 `flask`。 | geo-prospect |

---

## Schema 模板

`schema/` 下的这些 JSON-LD 文件，在 `geo-schema` 或 `geo-report` 需要产出可直接粘贴的结构化数据时作为生成参考。所有占位符遵循 `YOUR_FIELD_NAME` 或 `REPLACE_WITH_VALUE` 模式。

| 模板 | 什么时候用 |
|----------|-------------|
| `schema/organization.json` | 任何企业网站；提供完整的 Organization 类型，含指向百科、知乎、B站、公众号等平台的 `sameAs` 链接，以及用于实体话题信号的 `knowsAbout`。 |
| `schema/local-business.json` | 有实体门店的商家；在 Organization 基础上扩展地址、`geo` 坐标、营业时间、服务范围、综合评分和目录报价。 |
| `schema/article-author.json` | 内容站与博客页；Article 类型配完整 Person 作者（资历、`sameAs`、`alumniOf`、`knowsAbout`），以及便于 AI 助手朗读的 `speakable` 规范。 |
| `schema/product-ecommerce.json` | 电商商品页；Product 类型含 Offer（含配送细节和退货政策）、AggregateRating 和逐条 Review。 |
| `schema/software-saas.json` | SaaS 产品页；SoftwareApplication 类型含分档 AggregateOffer 报价、`featureList`、截图和 `sameAs` 链接。 |
| `schema/website-searchaction.json` | 每个网站的首页；WebSite 类型带 SearchAction `potentialAction`，用于启用站内搜索框并向 AI 系统提供站点搜索端点。 |

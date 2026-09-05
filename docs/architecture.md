# 架构与设计

本仓库围绕「GEO 优先，SEO 托底」组织：用 Claude 的工具能力、并行子代理和 Python 工具脚本，为国内网站提供 GEO + SEO 一体化审计，并内置 GEO 接单工作流（客户管理 → 提案 → 月度汇报）。

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
│   ├── geo-report-pdf/           # 专业 PDF 报告（pandoc 管线）
│   ├── geo-prospect/             # 轻量 CRM 潜在客户管道管理
│   ├── geo-proposal/             # 自动生成中文客户提案
│   └── geo-compare/              # 月度增量追踪与进度报告
├── agents/                       # 5 个并行子代理
│   ├── geo-ai-visibility.md      # GEO 审计、可引用性、爬虫、品牌提及
│   ├── geo-platform-analysis.md  # 平台专项优化
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
├── install.sh                    # 一键安装脚本
├── uninstall.sh                  # 卸载脚本
├── requirements.txt              # Python 依赖
└── README.md                     # 项目主入口
```

### 完整审计流程

运行 `/geo-cn audit https://example.com` 时：

1. **发现** —— 抓取首页、识别业务类型、解析 sitemap
2. **并行分析** —— 同时启动 5 个子代理：
   - AI 可见性（可引用性、爬虫、llms.txt、品牌提及）
   - 平台分析（百度AI搜索、Kimi、DeepSeek、豆包、元宝、夸克/通义就绪度）
   - 技术 SEO（Core Web Vitals、SSR、安全、移动端）
   - 内容质量（E-E-A-T、可读性、时效性）
   - Schema 标记（检测、验证、生成）
3. **综合** —— 汇总评分，生成综合 GEO 评分（0-100）
4. **报告** —— 输出分优先级整改计划与速赢项（中文）

### 数据存储

CRM 与报告类 skill（`/geo-cn prospect`、`/geo-cn proposal`、`/geo-cn compare`）把运行时数据存在 Claude Code 目录之外：

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

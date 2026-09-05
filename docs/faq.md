# 常见问题

---

## 基础问题

### GEO 是什么？和 SEO 有什么区别？

SEO（搜索引擎优化）针对的是传统搜索引擎的蓝色链接排名，比如百度、Google 的搜索结果页。GEO（生成式引擎优化，Generative Engine Optimization）针对的是 AI 生成答案里的可见性，比如百度AI搜索、Kimi、DeepSeek、豆包、元宝这类 AI 助手的回答。两门学问有重叠 —— 技术基础和内容质量对两者都重要 —— 但 GEO 多了一些 AI 检索特有的关注点：可引用性评分、品牌提及密度、llms.txt、跨 AI 引用源平台的实体识别。

### 这个工具收费吗？

工具本身免费，MIT 协议开源。它完全运行在你自己的 Claude Code 会话里，用你已有的订阅。工具包本身没有额外的 API key、用量计费或订阅费。

### 适合谁用？

- 给客户做审计的 GEO 服务商（内置客户管理、提案、月报的完整接单流程）
- 监测 AI 搜索可见性的企业市场团队
- 想提高内容被 AI 引用率的内容创作者
- 想要可落地 GEO + SEO 反馈、又不想买 SaaS 订阅的网站开发与运营者

### 它能替代我现有的 SEO 工具吗？

不能，是互补关系。`/geo-cn technical` 覆盖技术 SEO 基础，但它替代不了 Screaming Frog 这类爬虫工具、关键词研究平台或排名监控工具。它的核心价值在 GEO 层 —— AI 可引用性、爬虫访问、品牌信号、平台就绪度 —— 这些是传统 SEO 工具基本不覆盖的。

---

## 安装与配置

### 为什么需要 Claude Code CLI？

整个工具包是以 Claude Code 斜杠命令形式实现的。所有命令（`/geo-cn audit`、`/geo-cn quick` 等）都通过 Claude Code 的 skill 和 agent 系统路由执行。CLI 就是运行时，没有它，skill 文件无从执行。安装命令：`npm install -g @anthropic-ai/claude-code`。

### Windows 上不用 WSL 能跑吗？

能，但必须用 Git Bash，不能用 PowerShell 或命令提示符。Windows 安装脚本是 `install-win.sh`，依赖 Git for Windows（自带 Git Bash）。右键仓库文件夹选 "Open Git Bash here"，然后运行 `./install-win.sh`。不需要 WSL。

### `install.sh` 实际做了什么？

先检查 Git、Python 3.8+ 和 Claude Code CLI，然后把文件复制到你的 Claude 配置目录（`~/.claude/`）：主 skill 进 `~/.claude/skills/geo/`，14 个子 skill 分别进 `~/.claude/skills/geo-<名称>/`，5 个子代理文件进 `~/.claude/agents/`。随后在 `~/.claude/skills/geo/.venv/` 创建独立虚拟环境，从 `requirements.txt` 安装 Python 依赖（不污染系统 Python）。交互式运行时还会问你是否安装 Playwright Chromium 浏览器用于截图。

### 必须装 Playwright 吗？

不是必须的。安装器会提示你安装（`python3 -m playwright install chromium`）。没有它，截图相关功能不可用，但其他所有审计和分析命令都正常工作。之后随时可以补装。

### PDF 报告需要什么额外依赖？

`/geo-cn report-pdf` 用 pandoc + Chrome 无头模式生成 PDF，不依赖 Python 库。需要 `brew install pandoc`，以及安装在标准路径 `/Applications/Google Chrome.app/` 的 Google Chrome（macOS）。

---

## 使用

### `/geo-cn quick` 和 `/geo-cn audit` 有什么区别？

`/geo-cn quick` 产出 60 秒内联可见性快照，不写任何文件，适合在决定跑完整审计前快速摸底。`/geo-cn audit` 是完整工作流：抓取站点、识别业务类型、并行启动 5 个子代理、汇总全部类目评分，并写出一份带分优先级整改计划的 `GEO-AUDIT-REPORT.md`。完整命令清单见 [commands-reference.md](commands-reference.md)。

### 综合 GEO 评分是怎么算出来的？

评分（0-100）是六个类目的加权汇总：AI 可引用性与可见性（25%）、品牌权威信号（20%）、内容质量与 E-E-A-T（20%）、技术基础（15%）、结构化数据（10%）、平台优化（10%）。每个类目内各信号的度量方式见 [scoring-methodology.md](scoring-methodology.md)。

### 并行子代理是怎么工作的？

完整审计在初始发现阶段之后，同时运行 5 个子代理：`geo-ai-visibility`、`geo-platform-analysis`、`geo-technical`、`geo-content`、`geo-schema`。每个对应 `~/.claude/agents/` 下的一个代理定义文件，各自负责一块独立的分析。并行调度由 Claude Code 的 agent 系统处理；编排器收齐 5 份报告后综合出总分。完整流程见 [architecture.md](architecture.md)。

### prospect、proposal、report 的数据存在哪里？

`/geo-cn prospect`、`/geo-cn proposal`、`/geo-cn compare` 的数据写在 Claude Code 目录之外的 `~/.geo-prospects/`：

```
~/.geo-prospects/
├── prospects.json
├── audits/<域名>-<日期>.md
├── proposals/<域名>-proposal-<日期>.md
└── reports/<域名>-monthly-<YYYY-MM>.md
```

`uninstall.sh` 有意不删除这个目录。想丢弃客户数据的话，手动执行 `rm -rf ~/.geo-prospects`。

---

## 二次开发

### 怎么新增一个子 skill？

在 `skills/` 下按 `geo-<名称>/` 的命名规则新建目录，在里面写一个 `SKILL.md`，定义 skill 的名称、描述和逻辑。如果它要参与完整审计，在 `agents/` 下对应的代理文件里注册。可以参考现有子 skill（如 `skills/geo-citability/`）的结构。skill 与 agent 的对应关系图见 [skills-and-agents.md](skills-and-agents.md)。

### 改动之后怎么验证？

在项目目录运行 `./install.sh` —— 脚本检测到本地存在 `geo/SKILL.md` 时会直接从当前工作目录安装。然后打开 Claude Code，对一个真实 URL 跑一遍受影响的命令。

### 在哪里反馈问题或提需求？

加微信交流群 **simonsxxs**，直接跟作者聊。反馈问题时请附上说清问题的描述、你在审计的 URL（如果相关）以及报错输出。

---

## 局限性

### 这个工具能保证被 AI 引用或排名提升吗？

不能。工具审计的是「与 AI 可见性相关」的信号并给出改进建议，但没有任何工具能保证某个 AI 系统一定引用或展示某个域名。AI 检索是概率性的，随查询、平台和模型版本变化。

### 它会向第三方服务提交数据吗？

工具用 `WebFetch` 和 `Bash`（通过 `curl`）抓取你提供的 URL，品牌提及扫描器会查询公开可访问的平台（知乎、B站、百科、公众号等）上的品牌信号。审计数据不会发往任何第三方分析端点，数据只留在你的 Claude Code 会话和本地文件系统里。

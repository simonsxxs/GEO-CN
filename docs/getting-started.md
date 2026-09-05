# 快速上手

## 环境要求

| 依赖 | 用途 |
|---|---|
| Python 3.8+ | 运行工具脚本（页面抓取、可引用性评分等） |
| Claude Code CLI | skill 和子代理都通过 Claude Code 加载与调用 |
| Git | 安装脚本用来克隆仓库 |
| Playwright（可选） | 启用截图功能，主安装完成后可单独安装 |
| pandoc + Google Chrome（可选） | 生成 PDF 报告（`/geo-cn report-pdf`） |

如果还没装 Claude Code：

```bash
npm install -g @anthropic-ai/claude-code
```

---

## 安装

### macOS / Linux

```bash
cd geo-cn
./install.sh
```

### Windows —— 必须用 Git Bash

不支持 PowerShell 和命令提示符。必须使用 [Git Bash](https://git-scm.com/downloads)（随 Git for Windows 一起安装）。

```bash
# 在 Git Bash 中运行
cd geo-cn
./install-win.sh
```

右键克隆下来的文件夹选择 "Open Git Bash here"，或先打开 Git Bash 再切换到该目录。

### 安装脚本做了什么

- 把 `geo` 主编排 skill 复制到 `~/.claude/skills/geo/`
- 把 14 个子 skill 复制到 `~/.claude/skills/geo-*/`
- 把 5 个子代理定义复制到 `~/.claude/agents/`
- 在 `~/.claude/skills/geo/.venv/` 创建独立虚拟环境并安装 Python 依赖（不污染系统 Python）
- 可选安装 Playwright Chromium 浏览器用于截图

---

## 验证安装

安装完成后，在任意项目目录打开 Claude Code，运行：

```
/geo-cn quick https://example.com
```

如果 skill 接线正确，Claude Code 会开始一次 60 秒 GEO 可见性快照。如果提示「未知命令」或没有任何反应，重启 Claude Code —— 它只在启动时读取 skill 和 agent 文件。

确认文件落到了正确位置：

```bash
ls ~/.claude/skills/geo/
ls ~/.claude/skills/ | grep geo
ls ~/.claude/agents/ | grep geo
```

---

## 你的第一次审计

### 快速路径 —— 60 秒快照

```
/geo-cn quick https://你的网站.com
```

返回一个总的 GEO 可见性评分和最突出的问题。适合第一次摸底或见客户前的快速检查。

### 完整路径 —— 全面审计

```
/geo-cn audit https://你的网站.com
```

并行启动 5 个子代理，覆盖 AI 可见性、平台优化、技术 SEO、内容质量和结构化数据，产出带综合 GEO 评分（0-100）的分优先级整改计划。

完整审计需要几分钟，取决于网站规模。评分计算方法见 [scoring-methodology.md](scoring-methodology.md)，全部命令见 [commands-reference.md](commands-reference.md)。

---

## 排错

**安装时提示找不到 Python**
- 现象：安装脚本退出并报 `Python 3.8+ is required but not found`
- 原因：没装 Python，或不在 `PATH` 里
- 解决：从 [python.org](https://www.python.org/downloads/) 安装；Windows 安装时勾选 "Add Python to PATH"；然后重新打开终端

**找不到 Claude Code CLI**
- 现象：安装脚本警告 `Claude Code CLI not found in PATH`
- 原因：没装 `claude`，或不在 `PATH` 里
- 解决：`npm install -g @anthropic-ai/claude-code`；用 `claude --version` 确认

**Claude Code 里看不到命令**
- 现象：`/geo-cn quick` 提示未知命令或没有反应
- 原因：Claude Code 只在启动时读取 skill，启动后新增的文件看不到
- 解决：完全退出并重新打开 Claude Code

**`./install.sh` 权限不足**
- 现象：`bash: ./install.sh: Permission denied`
- 原因：没有可执行权限
- 解决：`chmod +x install.sh && ./install.sh`

**Windows 上用错了 shell**
- 现象：`curl` 无法识别，或脚本语法报错
- 原因：在 PowerShell 或命令提示符里运行了 `install-win.sh`
- 解决：只用 Git Bash —— 右键文件夹，"Open Git Bash here"

**Playwright 不可用 / 没有截图**
- 现象：截图相关步骤静默跳过或报错
- 原因：安装时跳过了 Playwright（非交互模式或选了否）
- 解决：手动安装：
  ```bash
  python3 -m playwright install chromium
  ```

**Python 依赖安装失败**
- 现象：安装脚本提示 `Some Python dependencies failed to install`
- 原因：pip 报错（网络、权限或虚拟环境冲突）
- 解决：在项目目录或 `~/.claude/skills/geo/` 下手动执行：
  ```bash
  python3 -m pip install -r requirements.txt
  ```

**PDF 报告生成失败**
- 现象：`/geo-cn report-pdf` 报错找不到 pandoc 或 Chrome
- 原因：PDF 管线依赖 pandoc 和 macOS 标准路径下的 Google Chrome
- 解决：`brew install pandoc`，并确认 Chrome 装在 `/Applications/Google Chrome.app/`

---

## 卸载

### 脚本卸载

在项目目录运行：

```bash
./uninstall.sh
```

这会删除 `~/.claude/skills/geo/`、所有 `~/.claude/skills/geo-*/` 子 skill、所有 `~/.claude/agents/geo-*.md` 子代理文件，以及安装时创建的虚拟环境。

### 手动卸载

```bash
rm -rf ~/.claude/skills/geo ~/.claude/skills/geo-* ~/.claude/agents/geo-*.md
```

### 运行时数据

`~/.geo-prospects/` 目录（`/geo-cn prospect`、`/geo-cn proposal`、`/geo-cn compare` 使用的客户数据）**不会**被卸载脚本删除。如不再需要，请手动删除：

```bash
rm -rf ~/.geo-prospects
```

---

另见：[architecture.md](architecture.md) ｜ [commands-reference.md](commands-reference.md) ｜ [scoring-methodology.md](scoring-methodology.md) ｜ [skills-and-agents.md](skills-and-agents.md)

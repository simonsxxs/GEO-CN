# geo-cn 文档中心

geo-cn 是一套 Claude Code skill 工具包：对国内网站做 GEO（生成式引擎优化）+ SEO 审计，产出综合 GEO 评分（0-100）和分优先级整改计划，并内置 GEO 接单工作流（客户管理 → 提案 → 月度汇报）。

如果你是第一次接触，从 **快速上手** 开始。如果你要改代码，先大致浏览 **架构** 和 **Skills 与代理**。

## 目录

| 文档 | 内容 |
|-----|--------------|
| [快速上手](getting-started.md) | 环境要求、安装（macOS/Linux/Windows）、第一次审计、排错、卸载 |
| [命令参考](commands-reference.md) | 每个 `/geo-cn` 斜杠命令的用法、参数、输出和使用时机 |
| [架构](architecture.md) | 仓库结构、审计流程、并行子代理调度、数据存储 |
| [Skills 与代理](skills-and-agents.md) | 每个子 skill、子代理、Python 脚本和 schema 模板的参考手册 |
| [评分方法](scoring-methodology.md) | 综合 GEO 评分的计算方法、各类目信号、注意事项 |
| [常见问题](faq.md) | 用户与贡献者的常见问题 |
| [贡献指南](../CONTRIBUTING.md) | 如何反馈问题、提需求、提交改动 |

## 快捷入口

- 第一次审计：[快速上手 → 你的第一次审计](getting-started.md#你的第一次审计)
- 完整命令清单：[命令参考](commands-reference.md)
- 权重表：[评分方法](scoring-methodology.md)
- 并行审计流程：[架构 → 完整审计流程](architecture.md)

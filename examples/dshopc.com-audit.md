# GEO 审计报告：DSHOPC（dshopc.com）

**审计日期：** 2026-09-05
**审计 URL：** https://dshopc.com
**业务类型：** 内容站 / 技术社区（Publisher）——Rspress v2.0.19 静态生成的 DeepSeek Harness 中文实战与生态社区
**分析页面数：** 15（13 个重点页面 + /connect/ 连通性检查 + sitemap 全量 29 条 URL 清单核对）
**执行工具：** geo-cn（fetch_page.py / citability_scorer.py / llmstxt_generator.py / brand_scanner.py）

> 说明：本次审计指定品牌名为「点石网络」，但**该名称在被审计站点上从未出现**（about 页全文 0 次提及），站点实际品牌为「DSHOPC」。两个品牌名均已用 brand_scanner.py 扫描，结果见「品牌权威」章节。正文评分以站点实际品牌 DSHOPC 为准。

---

## 执行摘要

**综合 GEO 得分：47 / 100（较差 Poor）**

站点技术底子很好：Rspress 全静态生成（SSG），AI 爬虫不执行 JS 也能读到完整内容；meta 标签、canonical、OG/Twitter Card、sitemap 齐全；教程页有 TechArticle + BreadcrumbList 结构化数据。但面向 AI 搜索的三块短板非常致命：**豆包生态的 Bytespider 被 robots.txt 整体屏蔽**、**llms.txt 完全缺失**、**品牌在知乎/B站/百科/公众号零可见存在感**，导致「内容再好也没人引用」。内容引用性中等（站均 45 分），主要卡在统计密度过低——229 个内容块中 0 个 A 级、55 个 F 级。

### 六维度得分表

| 维度 | 得分 | 权重 | 加权得分 |
|---|---|---|---|
| AI 可引用性（Citability） | 45/100 | 25% | 11.3 |
| 品牌权威（Brand Authority） | 10/100 | 20% | 2.0 |
| 内容质量与 E-E-A-T | 61/100 | 20% | 12.2 |
| 技术基础（Technical GEO） | 89/100 | 15% | 13.4 |
| 结构化数据（Schema） | 43/100 | 10% | 4.3 |
| 平台优化（Platform） | 40/100 | 10% | 4.0 |
| **综合 GEO 得分** | | | **47/100** |

计算公式：`GEO = 引用性×0.25 + 品牌×0.20 + E-E-A-T×0.20 + 技术×0.15 + Schema×0.10 + 平台×0.10`
= 45×0.25 + 10×0.20 + 61×0.20 + 89×0.15 + 43×0.10 + 40×0.10 = 47.1

---

## 严重问题（Critical — 立即修复）

1. **Bytespider 被 robots.txt 屏蔽**（`User-agent: Bytespider / Disallow: /`）。Bytespider 是豆包可见性的前提条件，且 Cloudflare 托管段与自定义段重复屏蔽了它，等于主动放弃了豆包生态的全部流量入口。证据：`https://dshopc.com/robots.txt` 两处 Bytespider Disallow 规则。
2. **robots.txt 存在自相冲突的规则组**。Cloudflare 托管段 `ClaudeBot Disallow: /`，站长自定义段又 `ClaudeBot Allow: /`；按 RFC 9309 同名 User-agent 的规则组会被合并，Allow/Disallow 冲突时不同爬虫裁决行为不一致，属于「你以为放行了、实际可能被拦」的高危配置。同问题还涉及 GPTBot、CCBot、Google-Extended、Meta-ExternalAgent 的重复定义。
3. **llms.txt 完全缺失**（`/llms.txt` 返回 404，`/llms-full.txt` 也不存在）。llms.txt 得分 0/100。对文档型站点这是成本最低、收益最直接的 GEO 动作。
4. **品牌实体零存在感**。品牌扫描显示「DSHOPC」与「点石网络」在知乎、B站、中文维基/百度百科、微信公众号均无官方账号或词条（国内平台反爬，结论为脚本降级输出，**需人工打开搜索 URL 确认**，见附录）。AI 模型无法把站点与任何已知实体关联，引用动机趋近于零。

## 高优先级问题（High — 一周内修复）

1. **Organization schema 残缺**：首页 Organization 只有 name + url，无 `sameAs`、无 `logo`、无 `description`。sameAs 是 GEO 中单体性价比最高的属性，直接决定 AI 能否跨平台识别实体。
2. **引用性整体偏低**：站均 45.0 分，229 个内容块中 A 级 0 个、B 级 11 个、F 级 55 个。所有块的 statistical_density（统计密度）子项普遍只有 0-2 分——全文几乎没有任何数字、日期、百分比类可量化陈述，AI 找不到「值得原样引用的事实点」。
3. **作者信号缺失**：TechArticle 的 author 是 Organization「DSHOPC」，全站无 Person schema、无作者署名页，E-E-A-T 的 Expertise 维度缺证据。
4. **首页引用性全站最低**（36.6 分，18 块中 9 个 F 级）：首页文案偏宣传口号式（如「一切皆插件」），没有 1-3 句话可直接引用的定义性答案块。

## 中优先级问题（Medium — 一个月内修复）

1. TechArticle 缺 `image`、`speakable` 属性；无 FAQPage/HowTo（HowTo 已被 Google 移除富媒体资格，不必加，但问答结构本身对 AI 仍有用）。
2. 导航页 `/connect/` 返回 200 但**未被 sitemap 收录**（sitemap 29 条 URL 中 0 条 connect），影响发现完整性。
3. 故障排查页（troubleshooting）内容块最多（62 块）但均分最低之一（38.8，F 级 23 块）：症状-解法结构很适合做引用块，但目前写法偏长句叙述，建议改为「症状 → 原因 → 一行命令解决」的短块结构。
4. 无 ICP 备案号且站点托管在 Cloudflare 境外节点（cf-ray 显示 SJC 圣何塞），对百度系平台的信任与访问速度均有影响。

## 低优先级问题（Low — 有空再优化）

1. 安全响应头缺失：无 HSTS、CSP、X-Frame-Options、Permissions-Policy（仅 x-content-type-options: nosniff 与 referrer-policy 存在）。
2. 不支持 Markdown 内容协商（`Accept: text/markdown` 返回 `text/html`）。站点跑在 Cloudflare 上，可通过 Workers/Pages 一行配置开启，属于前瞻性能力。
3. sitemap 的 XML 解析兼容性：geo-cn 抓取时触发 `XMLParsedAsHTMLWarning`（工具侧问题，不影响站点本身）。

---

## 分维度详查

### AI 可引用性（45/100）

**数据证据：** citability_scorer.py 对 13 个重点页面共 229 个内容块打分。

| 指标 | 数值 |
|---|---|
| 页面平均分均值 | 45.0 |
| 最高/最低页面 | about 52.4 / 首页 36.6 |
| 零分页面数 | 0（无大面积零分误判，中文页面均获得有效分数） |
| 等级分布 | A:0 / B:11 / C:73 / D:90 / F:55 |
| 最优长度块（optimal length） | 27 个 |

分数结构非常一致：answer_block_quality（25-30/30）和 self_containment（19-25/25）普遍较高——站点的问答式写作（「怎样算安装成功？」「3080 端口被占用怎么办？」）天然适合引用；**失分集中在 statistical_density（普遍 0-2 分）与 uniqueness_signals（2-5 分）**。也就是说：内容结构对了，但缺「硬事实」。

最佳引用块示例（B 级）：
1. 「怎样算安装成功？」（install 页，71 分）——「验证成功至少包括四项：Node.js 符合当前要求……」
2. 「更新节奏」（about 页，72 分）——「跟踪对象：dsh 官方仓库的 tag、npm 包 @deepseek-ai/dsh 的发布……」
3. 「向本站反馈与参与共建」（community 页，66 分）

### 品牌权威（10/100）

brand_scanner.py 分别扫描「点石网络」「DSHOPC」，国内平台反爬，脚本按降级策略输出搜索 URL + 人工核对清单：

| 平台 | 状态 | 人工确认入口 |
|---|---|---|
| 知乎 | 未发现机构号（需人工确认） | https://www.zhihu.com/search?type=content&q=DSHOPC |
| B站 | 未发现官方账号（需人工确认） | https://search.bilibili.com/all?keyword=DSHOPC |
| 中文维基/百度百科 | 维基 API 无标题匹配词条（「点石网络」有 10 条搜索结果但均为同名其他实体）；百度百科需人工打开 | https://baike.baidu.com/search/word?word=DSHOPC |
| 微信公众号 | 未发现（需人工确认） | https://weixin.sogou.com/weixin?type=1&query=DSHOPC |
| 技术社区 | 脚本未覆盖自动抓取，需人工查 GitHub/CSDN/掘金 | — |

给 10 分而非 0 分的原因：站点自身有完整的 about 页（声明独立性、事实核验方法、更新节奏），站内权威信号存在；但站外实体信号为零。**此项为全站最大失分点（权重 20% 只得 2 分）。**

### 内容质量与 E-E-A-T（61/100）

| 维度 | 得分 | 关键证据 |
|---|---|---|
| Experience 经验 | 16/25 | 安装/首跑/故障排查页均为实测产出（含具体端口 3080、Node 版本 ^22.19.0、命令输出判定标准）；ecosystem 页有「收录规则说明」要求每条来源可访问 |
| Expertise 专业 | 15/25 | 架构解析（Agent Loop、Cordis 内核、插件系统）有深度；但无署名作者、无作者资历页 |
| Authoritativeness 权威 | 11/25 | 独立社区站，明确声明「与 DeepSeek 无隶属或背书关系」；无外部引用、无百科词条、无媒体报道 |
| Trustworthiness 可信 | 19/25 | HTTPS、来源核验声明、内容分级标注（官方事实/DSHOPC分析/社区第三方未实测）、透明的反馈渠道；扣分为无备案号、无隐私政策/联系方式页面（仅微信一对一） |

### 技术基础（89/100）

| 子项 | 得分 | 证据 |
|---|---|---|
| SSR/JS 依赖 | 100 | Rspress SSG，原始 HTML 含完整正文（has_ssr_content=true，首页 2358 字符正文），AI 爬虫无需执行 JS |
| Meta 与可索引性 | 95 | title/description/canonical/robots(index,follow)/OG/Twitter Card/keywords 齐全，og:locale=zh_CN |
| 可抓取性 | 90 | robots.txt 存在且含 Sitemap 声明；sitemap.xml 29 条 URL 有效；扣分：/connect/ 漏收、规则组冲突 |
| 安全响应头 | 72 | HTTPS ✓；缺 HSTS(-10)、CSP(-10)、X-Frame-Options(-5)、Permissions-Policy(-3) |
| Core Web Vitals 风险 | 80 | 静态站风险低；有一处 JS preload、无内联大图；静态分析估计，建议 PageSpeed 实测 |
| 移动端 | 85 | viewport 正确，Rspress 主题响应式 |
| URL 结构 | 95 | 干净、层级清晰、全小写、连字符分隔 |
| 响应头与状态 | 90 | 200、gzip、Cloudflare CDN；无 X-Robots-Tag |
| 附加检查 | 70 | canonical 自引用、无重定向链；Markdown 协商不支持（非计分项） |

加权：100×0.25 + 95×0.15 + 90×0.15 + 72×0.10 + 80×0.10 + 85×0.10 + 95×0.05 + 90×0.05 + 70×0.05 = 89.2

**Content Signals（非计分）：** robots.txt 含 `Content-Signal: search=yes, ai-input=yes, ai-train=no`，声明允许搜索与 AI 输入、禁止训练——策略清晰，但与 Bytespider 屏蔽存在意图矛盾（想被 AI 引用却屏蔽了豆包的爬虫）。

### 结构化数据（43/100）

| 组件 | 得分 | 现状 |
|---|---|---|
| Organization | 10/20 | 存在（首页），但无 sameAs/logo/description |
| Article 类 schema | 11/15 | 教程页 TechArticle + datePublished/dateModified ✓，author 是 Organization 而非 Person |
| Person 作者 schema | 0/15 | 全站无 |
| sameAs 实体链接 | 0/15 | 无 |
| speakable | 0/10 | 无 |
| BreadcrumbList | 5/5 | 内容页均有且有效 |
| WebSite + SearchAction | 2/5 | WebSite 存在，无 SearchAction |
| 无废弃 schema | 5/5 | 未发现 HowTo/SpecialAnnouncement 等 |
| JSON-LD 格式 | 5/5 | 全部 JSON-LD，服务端直出（非 JS 注入） |
| 校验无错误 | 5/5 | JSON 合法、@context 正确 |

合计 43/100。**最优先动作：Organization 补 sameAs + logo + description；TechArticle 的 author 增加 Person。**

### 平台优化（40/100）

| 平台 | 得分 | 状态与依据 |
|---|---|---|
| 百度AI搜索 | 50 | Baiduspider 未被屏蔽（继承 `User-agent: *` Allow）、SSR 完整、有 sitemap；缺百度站长验证（外部不可观测，标注「无法从外部分析验证」）、无备案号 |
| Kimi | 60 | `Kimi-User` 被显式放行（robots.txt 自定义段），内容为纯文本 SSR——六个平台中就绪度最高 |
| DeepSeek | 45 | bingbot 未屏蔽（兜底通道可用）；缺 llms.txt |
| 豆包 | 15 | **Bytespider 被 Disallow: / 整体屏蔽**——可见性前提不存在 |
| 元宝 | 30 | 搜狗蜘蛛未单独声明（继承放行）；但无公众号内容源，元宝独家内容通道缺失 |
| 夸克/通义 | 35 | 神马蜘蛛未单独声明（继承放行）；无其他差异化信号 |

各平台得分平均 39.2 → 40。注意：国内平台排名机制未公开，以上为可观测信号推断。

---

## 速赢清单（本周可做）

1. **删掉 robots.txt 中对 Bytespider 的 Disallow**（两处），并消除 Cloudflare 托管段与自定义段对 ClaudeBot 等爬虫的冲突定义——预计豆包生态从「不可见」恢复为「可索引」。
2. **生成并部署 llms.txt**：用 llmstxt_generator.py 的输出结构，按 sitemap 的 29 页组织 `## 教程 / ## 架构 / ## 生态 / ## 关于` 四个分区。文档站适配度极高，半天工作量。
3. **首页 Organization schema 补 sameAs**（先指向 GitHub 与后续注册的知乎/公众号主页）、logo、description——一个 JSON-LD 代码块的事。
4. **给首页加一个「DSHOPC 是什么」的定义性答案块**（1-3 句话、可原样引用），例如：「DSHOPC 是一个独立的 DeepSeek Harness 中文社区，提供教程、架构解析与插件生态内容，与 DeepSeek 官方无隶属关系。」直接救全站引用性最低的页面。
5. **在 install / troubleshooting 页的高流量答案块里补数字**：版本号、端口、命令数量、耗时——每块 +10 分统计密度的空间。

## 30 天行动计划

### 第 1 周：止血（爬虫与入口）
- [ ] 修复 robots.txt：放行 Bytespider，合并/消除冲突规则组
- [ ] 部署 llms.txt（含 llms-full.txt）
- [ ] 把 /connect/ 加入 sitemap

### 第 2 周：实体与结构化数据
- [ ] Organization schema 补 sameAs/logo/description
- [ ] TechArticle author 改为 Person（创建作者页 + 作者 Person schema）
- [ ] 注册知乎机构号、微信公众号，完成基础认证并互链官网

### 第 3 周：内容引用性改造
- [ ] 首页与 6 个栏目落地页各加 1 个定义性答案块
- [ ] troubleshooting 页按「症状→原因→解决」短块结构重写 Top 10 高频问题
- [ ] 全站教程页补量化数据（版本、耗时、步骤数）

### 第 4 周：品牌存在感
- [ ] 知乎发布 2 篇架构解析长文（由站内内容改编，文末链回官网）
- [ ] 公众号开通并同步首篇
- [ ] 评估百度百科词条创建条件（需先积累媒体报道）
- [ ] 用 `/geo-cn compare` 跑月度对比，验证得分变化

---

## 附录 A：分析页面清单

| URL | 标题 | 引用性均分 | 块数 | 主要问题 |
|---|---|---|---|---|
| / | DSHOPC - DeepSeek Harness 中文实战与生态社区 | 36.6 | 18 | F 级块 9 个，宣传式文案缺答案块 |
| /deepseek-harness/ | 教程栏目落地页 | 48.2 | 4 | 页面薄，仅 4 块 |
| /deepseek-harness/getting-started/ | 入门指南 | 47.4 | 27 | D 级 9 块，统计密度低 |
| /deepseek-harness/install/ | 安装与启动教程 | 52.0 | 27 | 全站最佳教程页，4 个 B 级块 |
| /deepseek-harness/first-run/ | 首次运行 | 45.2 | 26 | D 级 12 块、F 级 5 块 |
| /deepseek-harness/troubleshooting/ | 故障排查 | 38.8 | 62 | 块最多质量最散，F 级 23 块 |
| /architecture/ | 架构栏目落地页 | 41.0 | 5 | 栏目页内容薄 |
| /architecture/overview/ | 架构总览 | 44.2 | 9 | 「证据与来源」块是亮点（63 分） |
| /architecture/agent-loop/ | Agent Loop 解析 | 42.0 | 8 | 统计密度全块为 0 |
| /ecosystem/ | 生态目录 | 46.6 | 9 | 收录规则块 65 分，其余偏薄 |
| /applications/ | 应用模型 | 41.9 | 11 | 长段落（2194 字符单块）不利引用 |
| /about/ | 关于 DSHOPC | 52.4 | 13 | 全站引用性最高页 |
| /community/ | 社区 | 48.2 | 10 | 反馈渠道块 66 分 |
| /connect/ | 加入交流 | —（未跑分） | — | 未收录进 sitemap |
| sitemap.xml 其余 14 页 | — | 未抓取 | — | 本次控制在 15 页内 |

抓取失败页：0。全部页面 30 秒超时内返回 200。

## 附录 B：robots.txt 关键片段（证据）

```
# Cloudflare 托管段（BEGIN/END Cloudflare Managed content 之间）
User-agent: Bytespider
Disallow: /
User-agent: ClaudeBot
Disallow: /
...

# 站长自定义段
User-agent: Kimi-User
Allow: /
User-agent: ClaudeBot
Allow: /          ← 与上方 Cloudflare 段冲突
User-agent: Bytespider
Disallow: /       ← 重复屏蔽，合并后必然被拦
Content-Signal: search=yes, ai-input=yes, ai-train=no
Sitemap: https://dshopc.com/sitemap.xml
```

## 附录 C：工具执行记录

| 脚本 | 调用 | 结果 |
|---|---|---|
| fetch_page.py | `full` 模式抓首页 | 200，page+robots+llms+sitemap 四件套一次拿全 |
| fetch_page.py | `page` 模式抓 about、install | 结构化数据解析正常 |
| citability_scorer.py | 13 个重点页面 | 全部成功，229 块，无零分误判 |
| llmstxt_generator.py | https://dshopc.com | 正确报告 404；未生成建议内容（suggestions 为空） |
| brand_scanner.py | 「点石网络」「DSHOPC」 | 反爬降级：输出搜索 URL + 人工核对清单 |

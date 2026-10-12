---
name: geo-crawlers
description: AI 爬虫可达性分析（国内版）。检查 robots.txt、meta 标签和 HTTP 响应头，判断国内主流 AI 平台（Kimi、豆包、百度 AI 搜索等）及出海平台的爬虫能否访问站点，输出完整可达性地图与放行建议，在保留必要控制权的前提下最大化 AI 可见性。
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - WebFetch
  - Write
---

# AI 爬虫可达性分析 Skill（国内版）

## 目的

本 Skill 分析网站对 AI 爬虫的可达性——这些爬虫是 AI 公司用来发现、索引和训练网页内容的机器人。如果 AI 爬虫被屏蔽，无论内容质量多高，都无法出现在 AI 生成的回答里。爬虫可达性是 GEO 最基础的技术前提。

## 核心洞察

截至 2026 年初，大量网站因为沿用传统 SEO 时期的 robots.txt 配置，在无意中屏蔽了 AI 爬虫。Originality.ai 2025 年的研究发现，Top 1000 网站中超过 35% 屏蔽了至少一个主流 AI 爬虫，5-10% 屏蔽了全部 AI 爬虫。屏蔽 AI 爬虫是让自己在 AI 搜索结果中「隐身」的最快方式。

对国内站点而言，还要特别注意两点：

1. **国内 AI 平台的索引底座是传统搜索引擎**。Kimi、DeepSeek、豆包等联网搜索能力大多依赖百度、Bing、头条搜索等通用索引，屏蔽传统蜘蛛（Baiduspider、bingbot 等）会间接让你在所有国内 AI 助手里消失。
2. **Bytespider 的取舍与西方站点相反**。原版手册建议西方站点屏蔽 Bytespider，但国内版必须放行——它是豆包可见性的前提。

---

## 完整 AI 爬虫参考表（国内视角两层名单 + 国外对照）

### Tier 1：AI 搜索/引用型爬虫（建议：放行 ALLOW）

这些爬虫直接为 AI 搜索产品服务，用户在这些产品里主动找答案。屏蔽它们会直接降低你在 AI 生成回答中的可见性。

#### Kimi-User
- **运营方：** 月之暗面（Moonshot AI）
- **User-Agent：** `Kimi-User`
- **用途：** 用户在 Kimi 中丢入 URL 要求阅读、总结时，由该爬虫实时抓取页面全文。属于用户触发型直读，不用于批量索引。
- **屏蔽影响：** 用户让 Kimi 读取你的页面时会失败，直接阻断用户主动发起的访问。Kimi 以长文本阅读见长，是内容型站点的重要 AI 入口。
- **建议：** **放行** —— 屏蔽它等于拒绝主动找上门来的读者。无任何训练侧收益损失可担忧，纯用户触发。

#### Bytespider
- **运营方：** 字节跳动
- **User-Agent：** `Bytespider`
- **完整 User-Agent 字符串：** `Mozilla/5.0 (Linux; Android 5.0) AppleWebKit/537.36 (KHTML, like Gecko) Mobile Safari/537.36 (compatible; Bytespider; spider-feedback@bytedance.com)`
- **用途：** 字节跳动搜索+训练混合型爬虫，为豆包（Doubao）、抖音 AI 功能等产品抓取内容，既服务于搜索索引也可能用于模型训练。
- **屏蔽影响：** 内容无法被豆包引用，也影响在抖音/头条系 AI 功能中的出现。**对国内站点来说，Bytespider 是豆包可见性的前提，屏蔽它等于主动放弃豆包这个日活亿级的 AI 入口。**
- **建议：** **放行（ALLOW）** —— 与西方站点策略相反，国内站点必须放行。注意：Bytespider 抓取行为较为激进（请求频率高、曾有不完全遵守 robots.txt 的报道），如果服务器压力较大，可用 `Crawl-delay` 缓解抓取频率，而不是直接屏蔽。

---

### Tier 2：传统搜索蜘蛛（AI 搜索的索引底座，必须放行）

国内 AI 助手的联网搜索大多不自建完整索引，而是复用传统搜索引擎的索引。这些蜘蛛是你在 Kimi、DeepSeek、豆包、元宝等 AI 产品里被引用的「地基」，**必须全部放行**。

#### Baiduspider
- **运营方：** 百度
- **User-Agent：** `Baiduspider`
- **用途：** 百度搜索引擎索引，同时是百度 AI 搜索（文心一言联网能力）的内容底座。
- **屏蔽影响：** 失去百度收录，连带失去百度 AI 搜索的引用机会；多个国内 AI 助手间接依赖百度索引，影响面会扩散。
- **建议：** **必须放行** —— 国内站点的第一优先级。同时建议在百度搜索资源平台完成站点验证并提交 sitemap。

#### ToutiaoSpider
- **运营方：** 字节跳动
- **User-Agent：** `ToutiaoSpider`
- **完整 User-Agent 字符串：** `Mozilla/5.0 (compatible; ToutiaoSpider/1.0; +http://www.toutiao.com/spider/)`
- **用途：** 头条搜索索引，是豆包生态的补充索引来源。
- **屏蔽影响：** 失去头条搜索收录，降低在字节系 AI 产品（豆包等）中的可见性。
- **建议：** **必须放行** —— 与 Bytespider 配合，构成豆包可见性的双通道。

#### ShenmaSpider
- **运营方：** 阿里巴巴（神马搜索）
- **User-Agent：** `ShenmaSpider`
- **用途：** 神马搜索索引。夸克浏览器内置搜索及通义相关 AI 产品与其生态关联。
- **屏蔽影响：** 失去神马搜索收录，影响在夸克/通义系 AI 问答中的可见性。
- **建议：** **必须放行** —— 移动端和夸克用户的重要入口。

#### Sogou Spider
- **运营方：** 搜狗（腾讯）
- **User-Agent：** `Sogou web spider`（常见变体：`Sogou inst spider`、`Sogou News Spider`）
- **用途：** 搜狗搜索索引，微信搜一搜内容发现的重要通道之一，与腾讯元宝的引用来源间接相关。
- **屏蔽影响：** 影响在搜狗搜索和微信搜一搜生态中的可见性。
- **建议：** **必须放行** —— 想进入腾讯系 AI（元宝）视野，搜狗通道不能断。

#### 360Spider
- **运营方：** 360
- **User-Agent：** `360Spider`（变体：`360Spider-Image`、`360Spider-Video`）
- **用途：** 360 搜索索引，也是 360 AI 搜索（360 智脑联网能力）的内容底座。
- **屏蔽影响：** 失去 360 搜索及 360 AI 搜索中的可见性。
- **建议：** **必须放行** —— 国内搜索市场份额虽不及百度，但仍是重要补充。

#### bingbot
- **运营方：** 微软
- **User-Agent：** `bingbot`
- **完整 User-Agent 字符串：** `Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)`
- **用途：** Bing 搜索索引。**关键：DeepSeek 等未公开搜索索引来源的国内平台，其联网搜索可能依赖 Bing 等通用索引。** Copilot 也直接使用 Bing 索引。
- **屏蔽影响：** 失去 Bing 收录，连带可能影响 DeepSeek、Copilot 等平台的引用机会。
- **建议：** **必须放行** —— 对「索引来源未公开」的平台来说，Bing 是最可能通用的兜底通道。

---

### 特别说明：DeepSeek 的爬虫

**DeepSeek 未公开独立的爬虫 User-Agent。** 其联网搜索依赖通用搜索索引（具体索引来源未公开）。这意味着：

- 你无法通过 robots.txt 单独针对 DeepSeek 做放行或屏蔽。
- 想被 DeepSeek 引用，唯一可操作的路径是保证百度 + Bing 双索引覆盖，即放行 Baiduspider 和 bingbot 并完成两大站长平台的验证。
- 审计中如遇声称「DeepSeek 爬虫」的 UA，应视为未经证实的信息，不得作为配置依据。

---

### 国外对照（可选参考）

以下国外 AI 爬虫对纯国内业务影响很小，**不参与计分**。仅出海站点（面向海外用户的业务）需要关注，统一列在此处备查：

| 爬虫 | 运营方 | 用途 | 建议 |
|---|---|---|---|
| OAI-SearchBot | OpenAI | ChatGPT 实时搜索（不用于训练） | 出海站点放行 |
| ChatGPT-User | OpenAI | 用户触发型直读 | 出海站点放行 |
| PerplexityBot / Perplexity-User | Perplexity AI | AI 搜索引用，总是署名来源 | 出海站点放行 |
| ClaudeBot / Claude-User | Anthropic | Claude 联网搜索与用户直读 | 出海站点放行 |
| DuckAssistBot | DuckDuckGo | DuckAssist AI 问答 | 出海站点放行 |
| GPTBot | OpenAI | 模型训练（不影响 ChatGPT 搜索） | 视训练数据策略自选 |
| CCBot | Common Crawl | 公开训练数据集 | 视训练数据策略自选 |
| Google-Extended | Google | Gemini 训练（不影响 Google 搜索排名） | 视训练数据策略自选 |
| Meta-ExternalAgent | Meta | Meta AI 功能 | 纯国内站点优先级低 |
| anthropic-ai | Anthropic | Claude 模型训练 | 视训练数据策略自选 |
| cohere-ai | Cohere | 企业级模型训练 | 低优先级，视策略自选 |

---

## 建议矩阵速查表

| 爬虫 | 层级 | 建议 | 理由 |
|---|---|---|---|
| Kimi-User | 1 | **ALLOW** | Kimi 用户触发型直读 |
| Bytespider | 1 | **ALLOW** | 豆包可见性前提；抓取激进可用 Crawl-delay 缓解 |
| Baiduspider | 2 | **必须 ALLOW** | 百度 AI 搜索底座，国内 AI 间接依赖 |
| ToutiaoSpider | 2 | **必须 ALLOW** | 头条搜索，豆包生态补充 |
| ShenmaSpider | 2 | **必须 ALLOW** | 神马搜索，夸克/通义相关 |
| Sogou Spider | 2 | **必须 ALLOW** | 搜狗/微信搜一搜，元宝间接相关 |
| 360Spider | 2 | **必须 ALLOW** | 360 搜索及 360 AI 搜索 |
| bingbot | 2 | **必须 ALLOW** | Bing 索引，DeepSeek 等平台可能的兜底通道 |

> 国外 AI 爬虫（OAI-SearchBot、ClaudeBot 等）见上文「国外对照（可选参考）」，出海站点按需放行，不参与国内版计分。

---

## 分析流程

### 第 1 步：抓取并解析 robots.txt

1. 用 WebFetch 获取 `[域名]/robots.txt`。
2. 解析所有 User-agent 指令及其关联的 Allow/Disallow 规则。
3. 对上面参考表中的每一个爬虫：
   - 检查是否存在针对该爬虫的独立 User-agent 段
   - 检查通配段（`User-agent: *`）中是否有会命中的规则
   - 判定有效状态：**已放行** / **已屏蔽** / **未提及**（继承通配规则）
4. 记录所有 `Crawl-delay` 指令（会减慢 AI 爬虫抓取）。
5. 检查 `Sitemap` 指令（AI 爬虫用它做内容发现）。

### 第 1.5 步：robots.txt 规则冲突检测（国内版特色，重点执行）

robots.txt 最常见的坑不是「写了 Disallow」，而是**多段规则互相冲突或顺序意外生效**。必须按以下流程逐一排查：

1. **列出 robots.txt 的全部 User-agent 段**，标注每段的行号范围。
2. **检查同名爬虫是否出现多次**。robots.txt 标准允许爬虫匹配合并规则最具体的段，但部分解析器只认第一个匹配段，重复段可能导致后写的 Allow 永远不生效。
3. **检查通配段与专属段的冲突**。专属段（如 `User-agent: Bytespider`）一旦存在，通配段（`User-agent: *`）对该爬虫完全失效——这是标准行为，但很多站长误以为通配段的规则会「叠加」生效。
4. **检查 CDN/WAF 托管段与自定义段的冲突**（实测案例）：
   - 某站点（dshopc.com）使用 Cloudflare 托管 robots.txt，文件里存在两段规则：Cloudflare 自动生成的托管段中有针对部分 AI 爬虫的 `Disallow`，站长自定义段中又写了 `Allow`。
   - 后果：相关 AI 爬虫按解析器不同可能命中托管段的 Disallow，站长的 Allow 形同虚设，存在被误拦的风险。
   - 排查动作：对 Tier 1 / Tier 2 名单中的每个爬虫，在文件全文范围内搜索其 UA 出现的**所有位置**，逐段确认最终生效的是 Allow 还是 Disallow。
5. **检查 Allow 与 Disallow 同段共存时的路径优先级**。标准是最长匹配优先，但老旧爬虫实现不一致，关键路径（`/`、重要栏目）建议只用单一指令，不依赖优先级规则。
6. 发现冲突时，在报告的「严重问题」章节给出具体冲突行号和修复后的完整 robots.txt。

### 第 2 步：检查 meta robots 标签

1. 抽取 5-10 个关键页面，抓取 HTML 检查：
   - `<meta name="robots" content="noindex">` —— 屏蔽所有机器人
   - `<meta name="robots" content="nofollow">` —— 禁止跟随链接
   - `<meta name="robots" content="noai">` —— 新兴的 AI 使用屏蔽标签
   - `<meta name="robots" content="noimageai">` —— 屏蔽 AI 图像训练
   - 针对特定爬虫的标签：`<meta name="Bytespider" content="noindex">`
2. 记录所有覆盖 robots.txt 指令的页面级规则。

### 第 3 步：检查 HTTP 响应头

1. 对同一批抽样页面，检查响应头中的：
   - `X-Robots-Tag: noindex` —— 等价于 meta noindex 的 HTTP 头形式
   - `X-Robots-Tag: noai` —— HTTP 头形式的 AI 使用屏蔽
   - `X-Robots-Tag: noimageai` —— 屏蔽 AI 图像训练
   - 针对特定爬虫的响应头：`X-Robots-Tag: Bytespider: noindex`
2. 注意：HTTP 头优先级高于 meta 标签，且对非 HTML 资源（PDF、图片等）同样生效。

### 第 4 步：检查 AI 专属文件

1. 检查 `/llms.txt`（新兴的 AI 爬虫引导标准，对 Kimi 这类支持直读长文本的平台收益最大）。
2. 检查 `/.well-known/ai-plugin.json`（OpenAI 插件清单）。
3. 检查 `/ai.txt`（提案中的标准，类似 ads.txt 的 AI 版）。
4. 记录每个文件的存在与否及质量。

### 第 5 步：评估 JavaScript 渲染需求

1. 判断站点是否为单页应用（SPA）或重度依赖 JS 渲染。
2. 各 AI 爬虫的 JS 渲染能力差异：
   - Kimi-User / Bytespider：JS 渲染能力有限
   - Baiduspider：有一定渲染能力但远不如 Googlebot
   - bingbot：具备较好的 JS 渲染能力
   - 国外 AI 爬虫（见「国外对照」）：JS 渲染能力普遍有限
3. 如果关键内容必须经 JS 渲染才能看到，标记为潜在问题。
4. 检查是否有服务端渲染（SSR）或静态生成（SSG）作为缓解手段——对国内 AI 平台（Kimi 直读、豆包引用）来说，正文 SSR 直出是最重要的可见性保障之一。

### 第 6 步：解析 Content-Signal 声明

复用第 1 步已抓取的 robots.txt，扫描 `Content-Signal:` 指令（IETF 草案 `draft-romm-aipref-contentsignals`）。

1. 逐行扫描以 `Content-Signal:` 开头的行（不区分大小写）。
2. 如果存在：
   - 解析所有 key=value 对（先按 `,` 分割，再按 `=` 分割）。
   - 校验 key 是否在已知集合内：`ai-train`、`search`、`ai-personalization`、`ai-retrieval`。
   - 校验 value：只有 `yes` 和 `no` 合法。
   - 未知 key 或非法 value 标记为警告——该规范仍是 IETF 草案。
   - 结果记录为 **通过（Pass）**，并用大白话解释各值的含义。
3. 如果不存在：记录为 **建议项（Recommendation）** —— 站点尚未声明 AI 使用偏好。

无需额外 HTTP 请求，robots.txt 已在第 1 步抓取。

---

## 输出格式

生成名为 `GEO-CRAWLER-ACCESS.md` 的文件：

```markdown
# AI 爬虫可达性报告：[域名]

**分析日期：** [日期]
**域名：** [域名]
**robots.txt 状态：** [已找到 / 未找到 / 错误]

---

## 爬虫可达性总览

| 爬虫 | 运营方 | 层级 | 状态 | 影响 |
|---|---|---|---|---|
| Kimi-User | 月之暗面 | 1 | [已放行/已屏蔽/未提及] | [影响描述] |
| Bytespider | 字节跳动 | 1 | [状态] | [影响] |
| Baiduspider | 百度 | 2 | [状态] | [影响] |
| ToutiaoSpider | 字节跳动 | 2 | [状态] | [影响] |
| ShenmaSpider | 阿里/神马 | 2 | [状态] | [影响] |
| Sogou Spider | 搜狗/腾讯 | 2 | [状态] | [影响] |
| 360Spider | 360 | 2 | [状态] | [影响] |
| bingbot | 微软 | 2 | [状态] | [影响] |

（出海站点如需检查国外 AI 爬虫，参照本手册「国外对照（可选参考）」小节，在报告附录中补充即可，不计入得分。）

**DeepSeek 说明：** DeepSeek 未公开独立爬虫 UA，其联网搜索依赖通用索引（来源未公开）。可达性取决于 Baiduspider 和 bingbot 的放行状态。

## AI 可见性得分：[X]/100

**Tier 1 可达：** [X/2 个爬虫已放行]
**Tier 2 可达：** [X/6 个爬虫已放行]

---

## 严重问题

[列出所有被屏蔽的 Tier 1 / Tier 2 爬虫，以及检测到的 robots.txt 规则冲突（附行号）]

## 整改建议

### 立即行动项
[需要修改的具体 robots.txt 规则]

### robots.txt 推荐配置
```
[完整的推荐 robots.txt 内容，见本手册末尾模板]
```

### 其他技术发现
- **Meta robots 标签：** [发现]
- **X-Robots-Tag 响应头：** [发现]
- **JavaScript 渲染：** [评估结果]
- **llms.txt：** [存在/缺失]
- **Sitemap 可达性：** [评估结果]

### Content-Signal 声明（IETF 草案）

**状态：** 已声明 / 未声明

<!-- 如果已声明： -->
| 信号键 | 值 | 含义 |
|---|---|---|
| ai-train | no | 拒绝用于 AI 模型训练 |
| search | yes | 允许用于 AI 搜索结果 |

<!-- 如果未声明： -->
**建议：** 在 robots.txt 中增加 `Content-Signal:` 指令，显式声明 AI 使用偏好。示例：

`Content-Signal: ai-train=no, search=yes, ai-retrieval=yes`

完整规范见 https://contentsignals.org/
```

---

## 附录：面向国内站点的 robots.txt 推荐配置模板

适用于希望最大化国内 AI 平台可见性、同时保留训练数据选择权的站点：

```
# ========================================
# Tier 2：传统搜索蜘蛛 —— AI 搜索的索引底座，必须放行
# ========================================
User-agent: Baiduspider
Allow: /

User-agent: ToutiaoSpider
Allow: /

User-agent: ShenmaSpider
Allow: /

User-agent: Sogou web spider
Allow: /

User-agent: 360Spider
Allow: /

User-agent: bingbot
Allow: /

# ========================================
# Tier 1：AI 搜索/引用型爬虫 —— 建议放行
# ========================================
# Kimi（用户丢 URL 直读全文）
User-agent: Kimi-User
Allow: /

# 字节跳动：豆包可见性前提。抓取较激进，用 Crawl-delay 缓解压力
User-agent: Bytespider
Allow: /
Crawl-delay: 10

# ========================================
# 其他配置
# ========================================
# 显式声明 AI 使用偏好（IETF 草案，供支持的爬虫参考）
Content-Signal: ai-train=no, search=yes, ai-retrieval=yes

# 全站 sitemap，供所有爬虫发现内容（替换为实际地址）
Sitemap: https://www.example.com/sitemap.xml
```

**配置注意事项：**

1. 每个爬虫单独成段，不要合并写——合并写（如 `User-agent: Baiduspider, bingbot`）不是合法语法。
2. 不要在该文件里同时出现同一爬虫的两段规则（CDN 托管段冲突的高发原因），上线前用第 1.5 步的冲突检测流程全文核对。
3. `Crawl-delay` 并非所有爬虫都遵守（百度不支持，Bytespider 支持情况不稳定），服务器压力大的站点应同时在 CDN/WAF 层配置速率限制作为兜底。
4. 出海站点如需放行或屏蔽国外 AI 爬虫，按「国外对照（可选参考）」小节的建议在此模板基础上追加对应 User-agent 段即可。

---

## 爬虫可达性评分规则（Scoring for Crawler Access）

AI 爬虫可达性得分按以下方式计算：

| 组成项 | 权重 | 计分方式 |
|---|---|---|
| Tier 1 爬虫放行 | 50% | 每放行 1 个 Tier 1 爬虫得 50 分（2 个爬虫 = 满分 100，折算为 50 分） |
| Tier 2 爬虫放行 | 25% | 每放行 1 个 Tier 2 爬虫得 100/6 分（6 个爬虫 = 满分 100，折算为 25 分） |
| 无一刀切 AI 屏蔽 | 15% | 不存在 `User-agent: *` 配 `Disallow: /`、无 noai meta 标签、无 robots.txt 规则冲突，得满分；发现规则冲突扣一半 |
| AI 专属文件 | 10% | llms.txt 存在得 5 分，sitemap 对 AI 爬虫可达得 5 分 |

最终得分 = 各加权项之和，封顶 100 分。国外 AI 爬虫（见「国外对照」）不参与计分。

**评分解读：**

- Tier 2（传统蜘蛛）权重虽低于 Tier 1，但对国内站点实际是「一票否决」性质：Baiduspider 被屏蔽时，即使 Tier 1 全放行，报告中必须额外标注「国内 AI 可见性地基缺失」的严重警告。
- DeepSeek 因无公开爬虫 UA 不参与直接计分，其可见性通过 Baiduspider + bingbot 的放行状态间接体现。

---

**作者：simon，一个不懂代码的AI极客**

- 微信交流群：simonsxxs
- GitHub：https://github.com/simonsxxs
- Gitee：https://gitee.com/simonsxx

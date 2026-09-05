---
name: geo-technical
description: 面向国内站点的技术 SEO 审计（含 GEO 专项检查）——可抓取性、可索引性、安全、性能、SSR、AI 爬虫放行、国内搜索与 AI 索引渠道接入
version: 1.0.0
author: simonsxxs
tags: [geo, technical-seo, core-web-vitals, ssr, crawlability, security, performance]
allowed-tools: Read, Grep, Glob, Bash, WebFetch, Write
---

# GEO 技术 SEO 审计（国内版）

## 目的

技术 SEO 是传统搜索可见性和 AI 搜索引用的共同地基。技术上坏掉的站点，任何平台都抓不到、收不进、引用不了。本手册审计 8 个技术健康类别，并重点关注 GEO 需求——最关键的是**服务端渲染**（AI 爬虫不执行 JavaScript）和 **AI 爬虫放行**（很多站点在 robots.txt 里无意中屏蔽了 AI 爬虫）。

## 使用方式

1. 收集目标 URL（首页 + 2-3 个关键内页）
2. 用 curl/WebFetch 抓取每个页面，获取原始 HTML 和 HTTP 响应头
3. 逐项过下面 8 个审计类别
4. 按评分细则给每个类别打分
5. 生成 GEO-TECHNICAL-AUDIT.md 报告

---

## 类别 1：可抓取性 Crawlability（15 分）

### 1.1 robots.txt 有效性
- 抓取 `https://[domain]/robots.txt`
- 检查语法有效性：`User-agent`、`Allow`、`Disallow` 指令是否正确
- 检查常见错误：缺少 User-agent、通配符屏蔽了重要路径、`Disallow: /` 屏蔽整站
- 确认引用了 XML sitemap：`Sitemap: https://[domain]/sitemap.xml`

### 1.2 AI 爬虫放行（GEO 关键项）
检查 robots.txt 中针对以下爬虫的指令：

**国内优先（AI 搜索/引用 + 索引底座）：**

| 爬虫 | User-Agent | 平台 |
|---|---|---|
| Kimi-User | Kimi-User | Kimi（月之暗面，用户触发型直读） |
| Bytespider | Bytespider | 豆包 / 字节跳动 AI（抓取较激进，可用 `Crawl-delay` 缓解） |
| Baiduspider | Baiduspider | 百度搜索 + 百度 AI 搜索的索引底座 |
| ToutiaoSpider | ToutiaoSpider | 头条搜索，豆包生态补充 |
| ShenmaSpider | ShenmaSpider | 神马搜索，夸克/通义相关 |
| Sogou Spider | Sogou | 微信搜一搜、元宝间接相关 |
| 360Spider | 360Spider | 360 AI 搜索 |
| bingbot | bingbot | Bing Copilot；DeepSeek 等未公开索引源的平台可能依赖 Bing 索引 |

> 注：DeepSeek 未公开独立爬虫 UA，如实标注「未公开，依赖通用索引」。

**出海/国际平台（有出海业务的站点同样需要放行）：**

| 爬虫 | User-Agent | 平台 |
|---|---|---|
| OAI-SearchBot | OAI-SearchBot | ChatGPT 搜索 |
| GPTBot | GPTBot | OpenAI 训练（策略自选） |
| Googlebot | Googlebot | Google 搜索 + AI Overviews |
| Google-Extended | Google-Extended | Gemini / Google AI 训练（策略自选） |
| PerplexityBot / Perplexity-User | PerplexityBot / Perplexity-User | Perplexity AI |
| ClaudeBot / Claude-User | ClaudeBot / Claude-User | Anthropic Claude |
| Amazonbot | Amazonbot | Alexa / Amazon AI |
| CCBot | CCBot | Common Crawl（众多 AI 模型的数据源） |
| FacebookBot | FacebookExternalHit | Meta AI |
| Applebot-Extended | Applebot-Extended | Apple Intelligence |

**AI 爬虫放行评分：**
- 主流 AI 爬虫和国内搜索蜘蛛全部放行：5 分
- 部分被屏蔽但 Baiduspider + bingbot 放行：3 分
- Bytespider 或 Kimi-User 被屏蔽：1 分（对国内 GEO 影响显著）
- Baiduspider 被屏蔽：0 分（致命）

**重要细节**：屏蔽 Google-Extended 不等于屏蔽 Googlebot。Google-Extended 只控制 AI 训练数据使用，不影响搜索收录。但屏蔽它可能降低在 AI Overviews 中的出现率。除非有明确的数据授权顾虑，否则建议放行。

### 1.3 robots.txt 规则冲突检测（国内版强化）

多 UA 分组、Allow/Disallow 混用时极易产生冲突，且多数站长工具不会报错。实测案例：dshopc.com 曾因 `User-agent: *` 分组里的 `Disallow` 规则覆盖了针对特定 AI 爬虫分组的 `Allow`，导致 AI 爬虫被误伤。

检查流程：
1. 列出 robots.txt 中所有 `User-agent` 分组
2. 对每个重点爬虫（Baiduspider、Bytespider、Kimi-User 等），确认：
   - 是否有专属分组？没有则适用 `User-agent: *` 分组的规则
   - 专属分组与 `*` 分组的规则是否矛盾（大多数爬虫只遵循最匹配的那个分组，不会合并）
3. 检查同一分组内 `Allow` 与 `Disallow` 的路径重叠（百度按最长匹配优先，Google 亦然，但个别蜘蛛实现不一致）
4. 用百度搜索资源平台的 robots 检测工具实际验证一遍（见「国内搜索与 AI 索引渠道」章节）

### 1.4 XML Sitemap
- 抓取 sitemap（从 robots.txt 找地址，或试 `/sitemap.xml`、`/sitemap_index.xml`）
- 校验 XML 语法
- 检查 `<lastmod>` 日期（应当存在且准确）
- 统计 URL 数量——与预期可索引页面数对比
- 大站检查是否有 sitemap 索引（单个 sitemap 上限 50,000 条 URL）
- 抽样验证 sitemap 内 URL 返回 200 状态码

### 1.5 抓取深度
- 首页 = 深度 0。所有重要页面应在 **3 次点击**（深度 3）内可达
- 深度 4+ 的页面分到的抓取配额显著更少，被 AI 引用的概率也更低
- 检查内链：关键内容页是否从首页或主导航可达？

### 1.6 Noindex 管理
- 检查本应被收录的页面上是否有 `<meta name="robots" content="noindex">`
- 检查 `X-Robots-Tag: noindex` HTTP 响应头
- 常见错误：分页页、分类页或关键落地页被误加 noindex

**类别评分：**
| 检查项 | 分值 |
|---|---|
| robots.txt 有效且完整、无规则冲突 | 3 |
| AI 爬虫放行 | 5 |
| XML sitemap 存在且有效 | 3 |
| 抓取深度在 3 次点击内 | 2 |
| 无误伤性 noindex 指令 | 2 |

---

## 类别 2：可索引性 Indexability（12 分）

### 2.1 Canonical 标签
- 每个可索引页面必须有 `<link rel="canonical" href="...">` 标签
- Canonical 应指向自身（自引用），标识权威版本
- 检查 canonical 冲突（HTML 里的 canonical 与 HTTP 头里的不一致）
- 检查 canonical 链（A 指向 B、B 指向 C——应当 A 直接指向 C）

### 2.2 重复内容
- 检查 www 与非 www（两者都应可解析，其中一个 301 跳转）
- 检查 HTTP 与 HTTPS（HTTP 应跳转 HTTPS）
- 检查尾斜杠一致性（选定一种格式，另一种做跳转）
- 检查参数型重复（`?sort=price` 生成重复页面）

### 2.3 分页
- 如有分页内容，检查 `rel="next"` / `rel="prev"`（注：Google 自 2019 年起忽略这两个标签，但 Bing 仍在使用）
- 推荐做法：分页页用 `rel="canonical"` 指向「查看全部」页或第一页
- 分页页若包含独特内容，不要加 noindex

### 2.4 Hreflang（多语言站点）
- 检查 `<link rel="alternate" hreflang="xx">` 标签
- 验证互指关系（A 指向 B，B 必须指回 A）
- 验证存在 x-default 兜底
- 检查语言/地区代码有效性（ISO 639-1 / ISO 3166-1）

### 2.5 索引膨胀
- 估算已收录页面数（看 sitemap 数量，用 `site:domain.com` 粗估；百度可用百度搜索资源平台的索引量数据）
- 对比收录页数与实际有价值的内容页数
- 若收录数显著超过内容页数，标记索引膨胀（薄内容/重复/参数页导致）

**类别评分：**
| 检查项 | 分值 |
|---|---|
| 所有页面 canonical 标签正确 | 3 |
| 无重复内容问题 | 3 |
| 分页处理正确 | 2 |
| Hreflang 正确（如适用） | 2 |
| 无索引膨胀 | 2 |

---

## 类别 3：安全 Security（10 分）

### 3.1 强制 HTTPS
- 站点必须通过 HTTPS 加载
- HTTP 必须 301 跳转到 HTTPS
- 无混合内容警告（HTTPS 页面加载 HTTP 资源）
- SSL/TLS 证书有效且未过期

### 3.2 安全响应头
检查 HTTP 响应头：

| 响应头 | 要求值 | 作用 |
|---|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | 强制 HTTPS |
| `Content-Security-Policy` | 合理的策略 | 防 XSS |
| `X-Content-Type-Options` | `nosniff` | 防 MIME 嗅探 |
| `X-Frame-Options` | `DENY` 或 `SAMEORIGIN` | 防点击劫持 |
| `Referrer-Policy` | `strict-origin-when-cross-origin` 或更严 | 控制 referrer 数据 |
| `Permissions-Policy` | 合理限制 | 控制浏览器特性 |

**类别评分：**
| 检查项 | 分值 |
|---|---|
| 强制 HTTPS 且证书有效 | 4 |
| 有 HSTS 头 | 2 |
| X-Content-Type-Options | 1 |
| X-Frame-Options | 1 |
| Referrer-Policy | 1 |
| Content-Security-Policy | 1 |

---

## 类别 4：URL 结构（8 分）

### 4.1 干净的 URL
- URL 应当可读：`/blog/seo-guide` 而不是 `/blog?id=12345`
- URL 中不含 session ID
- 全小写（不混大小写）
- 用连字符分词（不用下划线）
- 无特殊字符或编码空格

### 4.2 合理的层级
- URL 路径应反映站点架构：`/category/subcategory/page`
- 该扁平就扁平——避免无必要的深层嵌套
- 全站模式一致

### 4.3 跳转链
- 检查跳转链（A 跳 B 再跳 C）
- 建议最多 1 跳（A 直接跳 C）
- 检查跳转循环
- 跳转应使用 301（永久）而非 302（临时），除非确实有意为之

### 4.4 参数处理
- URL 参数不应产生重复的可索引页面
- 用 canonical 标签或 robots.txt Disallow 处理参数变体
- 在百度搜索资源平台配置参数处理；出海站点另见文末「出海站点建议」

**类别评分：**
| 检查项 | 分值 |
|---|---|
| URL 干净可读 | 2 |
| 层级合理 | 2 |
| 无跳转链（最多 1 跳） | 2 |
| 参数处理已配置 | 2 |

---

## 类别 5：移动端优化（10 分）

### 背景
Google 自 **2024 年 7 月**起对所有站点只使用移动端 Googlebot 抓取，不再抓桌面版；百度同样以移动优先。移动端不可用的站点，等于对主流搜索引擎不可用。

### 5.1 响应式设计
- 检查 `<meta name="viewport" content="width=device-width, initial-scale=1">`
- 移动端内容不应需要横向滚动
- 无宽于视口的固定宽度布局

### 5.2 点击目标
- 可交互元素（按钮、链接）至少 48x48 CSS 像素
- 点击目标之间至少 8px 间距
- 检查移动端导航是否可用

### 5.3 字号
- 正文字号至少 16px
- 无需放大即可阅读
- 对比度达标（WCAG AA：正文 4.5:1，大字 3:1）

### 5.4 移动端内容一致性
- 桌面端可见的所有内容，移动端也必须可见
- 关键内容不要藏在爬虫无法展开的「展开更多」折叠里
- 图片和多媒体在移动端正常加载

**类别评分：**
| 检查项 | 分值 |
|---|---|
| viewport meta 标签正确 | 3 |
| 响应式布局（无横向滚动） | 3 |
| 点击目标尺寸合适 | 2 |
| 字号可读 | 2 |

---

## 类别 6：Core Web Vitals（15 分）

### 2026 年指标与阈值
Core Web Vitals 以真实用户数据的**第 75 百分位**为基准。实验室数据可用于调试，但决定排名信号的是实测数据。

| 指标 | 良好 | 待改进 | 差 | 说明 |
|---|---|---|---|---|
| **LCP**（最大内容绘制） | < 2.5s | 2.5s - 4.0s | > 4.0s | 衡量加载——最大可见元素渲染完成的时间 |
| **INP**（交互到下一次绘制） | < 200ms | 200ms - 500ms | > 500ms | 2024 年 3 月替代 FID，衡量所有交互而非首次 |
| **CLS**（累积布局偏移） | < 0.1 | 0.1 - 0.25 | > 0.25 | 衡量视觉稳定性——意外的布局移动 |

### 没有 CrUX 数据时如何评估
真实用户数据不可用时，从页面特征估算：
- **LCP**：检查首屏最大元素。是图片（看大小/格式）？是文字（看 Web 字体加载）？服务器响应时间（TTFB）如何？
- **INP**：检查页面重型 JavaScript。长任务（>50ms）会阻塞交互。检查第三方脚本。
- **CLS**：检查未显式声明宽高的图片、首屏动态插入的内容、导致布局偏移的 Web 字体（FOUT/FOIT）。

### 常见 LCP 修复
1. 优化首屏大图：WebP/AVIF 格式、正确尺寸、用 `<link rel="preload">` 预加载
2. 降低服务器响应时间（TTFB < 800ms）
3. 消除阻塞渲染的 CSS/JS
4. 对关键第三方源做 preconnect

### 常见 INP 修复
1. 用 `requestIdleCallback` 或 `scheduler.yield()` 把长任务（>50ms）拆小
2. 减少第三方 JavaScript
3. 屏外内容用 `content-visibility: auto`
4. 事件处理器加防抖/节流

### 常见 CLS 修复
1. 图片和视频始终带 `width` 和 `height` 属性
2. 用 CSS `aspect-ratio` 或显式尺寸为广告和嵌入内容预留位置
3. 用 `font-display: swap` 搭配尺寸调整过的兜底字体
4. 页面加载后不要在已有内容上方插入新内容

**类别评分：**
| 检查项 | 分值 |
|---|---|
| LCP < 2.5s | 5 |
| INP < 200ms | 5 |
| CLS < 0.1 | 5 |

---

## 类别 7：服务端渲染 SSR（15 分）—— GEO 关键项

### 为什么 SSR 对 AI 可见性是硬性要求
AI 爬虫（Kimi-User、Bytespider 等国内 AI 爬虫）**不执行 JavaScript**。它们抓取原始 HTML 后直接解析。如果你的内容靠 React、Vue、Angular 等框架在客户端渲染，AI 爬虫看到的是空页面。

即使是会执行 JavaScript 的 Googlebot，也会因额外抓取成本而降权 JS 渲染内容。Google 把 JS 渲染放进单独的「渲染队列」，收录可能延迟数天到数周。百度对 JS 渲染的支持更弱，依赖客户端渲染的页面对百度基本不可见。

### 检测方法
1. 用 curl 抓取页面（不执行 JavaScript）：`curl -s [URL]`
2. 对比原始 HTML 与浏览器渲染后的 DOM
3. 如果关键内容（标题、正文段落、产品信息、文章正文）在 curl 输出中**缺失**，说明站点依赖客户端渲染

### 检查清单
- **正文内容**：文章正文 / 产品描述 / 页面主体在原始 HTML 里吗？
- **标题标签**：H1、H2、H3 在原始 HTML 里吗？
- **导航**：主导航是服务端渲染的吗？
- **结构化数据**：JSON-LD 在原始 HTML 里还是 JS 注入的？
- **Meta 标签**：title、description、canonical、OG 标签在原始 HTML 里吗？
- **内链**：导航和内容链接在原始 HTML 里吗？（对可抓取性至关重要）

### 可推荐的 SSR 方案
| 框架 | SSR 方案 |
|---|---|
| React | Next.js（SSR/SSG）、Remix、Gatsby（SSG） |
| Vue | Nuxt.js（SSR/SSG） |
| Angular | Angular Universal |
| Svelte | SvelteKit |
| 通用 | Prerender.io（预渲染服务）、Rendertron |

### 评分细则
- 所有关键内容服务端渲染：15 分
- 主内容服务端渲染但部分元素仅 JS 可见：10 分
- 关键内容（产品信息、文章正文）依赖 JS：5 分
- 整页客户端渲染（原始 HTML 的 body 为空）：0 分

**类别评分：**
| 检查项 | 分值 |
|---|---|
| 主内容在原始 HTML 中 | 8 |
| Meta 标签 + 结构化数据在原始 HTML 中 | 4 |
| 内链在原始 HTML 中 | 3 |

---

## 类别 8：页面速度与服务器性能（15 分）

### 8.1 首字节时间 TTFB
- 目标：**< 800ms**（理想 < 200ms）
- 用 curl 测量：`curl -o /dev/null -s -w 'TTFB: %{time_starttransfer}s\n' [URL]`
- TTFB > 800ms 时：检查服务器位置、缓存、数据库查询、CDN 使用情况
- **国内站点特别要求**：必须从国内网络环境测量。境外服务器 + 无国内 CDN 是国内站点最常见的性能杀手

### 8.2 资源优化
- 页面总大小目标：**< 2MB**（关键页面 < 1MB）
- 检查未压缩资源（应开启 gzip/brotli 压缩）
- 检查未压缩的 CSS 和 JavaScript
- 检查未使用的 CSS/JS（很多站点 50%+ 的下载字节是无用的）

### 8.3 图片优化
- 检查图片格式：优先 WebP 或 AVIF，而非 JPEG/PNG
- 检查超大图片（图片实际尺寸大于显示尺寸）
- 检查懒加载：首屏以下图片应有 `loading="lazy"`
- 检查显式尺寸（width/height 属性防 CLS）
- 首屏图片不应懒加载（伤害 LCP）

### 8.4 代码分割与懒加载
- JavaScript 应做代码分割，每个页面只加载所需部分
- 检查大体积 JS 包（压缩后 > 200KB 警告，> 500KB 严重）
- 第三方脚本应异步加载（`async` 或 `defer`）
- 检查 `<head>` 中的阻塞渲染资源

### 8.5 缓存
- 检查静态资源（图片、CSS、JS）的 `Cache-Control` 头
- 静态资源应有长缓存：`max-age=31536000`（1 年），配合内容哈希文件名
- HTML 页面用较短缓存或 `no-cache` + 协商缓存（`ETag` 或 `Last-Modified`）

### 8.6 CDN 使用（国内站点重点）
- 检查静态资源是否由 CDN 提供（不同域名或 CDN 特征响应头）
- **国内站点应使用国内 CDN**（阿里云 CDN、腾讯云 CDN、又拍云、七牛等）；Cloudflare 等境外 CDN 在国内访问速度差且无国内节点备案，不适用于主站在国内的业务
- 检查 CDN 特征响应头：`CF-Ray`（Cloudflare）、`X-Cache`（AWS CloudFront/多家通用）、`X-Served-By`（Fastly）、`X-Via` / `X-Swr`（部分国内 CDN）
- 从国内多个地区抽样测速（可用 itdog.cn、boce.com 等拨测工具）

**类别评分：**
| 检查项 | 分值 |
|---|---|
| TTFB < 800ms（国内网络环境测量） | 3 |
| 页面大小 < 2MB | 2 |
| 图片已优化（格式、尺寸、懒加载） | 3 |
| JS 包体积合理（压缩后 < 200KB） | 2 |
| 开启压缩（gzip/brotli） | 2 |
| 静态资源有缓存头 | 2 |
| 使用 CDN（国内站点用国内 CDN） | 1 |

---

## 类别 9：Agent 就绪信号（不计分）

以下检查项面向新兴的 AI Agent 兼容性信号。不计入总分——只产出「通过」或「建议」。相关标准要么是 IETF 草案，要么是早期采用特性，对缺失扣分不公平。

### 9.1 RFC 8288 Link 响应头（服务发现）

RFC 8288（Web Linking）定义了 HTTP `Link:` 响应头。服务器可用它声明关联资源——API 目录、服务文档、MCP 服务器卡片——以机器可读的方式暴露，无需解析 HTML。

**检查方法：** 从首页的标准抓取中收集所有 `Link:` 响应头（无需额外请求）。

**关注点：**
- 解析 `<url>; rel="relation-type"` 对
- 高价值 rel 类型：`api-catalog`（RFC 9609）、`describedby`、`service-doc`、`mcp-server-card`

**何时给建议：** 仅对 API 优先的站点（导航中有 API 文档链接、有 `/api/` 或 `/developers/` 路径、sitemap 中有 swagger/OpenAPI）。普通业务站点完全跳过本节——缺失是预期行为，不值得提及。

| 状态 | 处理方式 |
|---|---|
| 有 `Link:` 头，rel 类型已知 | 信息性——记录发现内容 |
| 有 `Link:` 头，rel 类型未知 | 信息性——记录并解释 |
| 缺失，API 优先站点 | 给建议——解释并建议实现 |
| 缺失，普通业务站点 | 跳过——不提及 |

### 9.2 Markdown 内容协商

检查服务器是否对 `Accept: text/markdown` 响应 `Content-Type: text/markdown`。Cloudflare 的 "Markdown for Agents" 功能实现了这一点——AI Agent 收到干净的 Markdown 而非 HTML，省去样板剥离，提高内容提取准确率。

**检查方法：** 向首页发一个带 `Accept: text/markdown` 的 GET 请求。每次审计只多一次 HTTP 请求。

**评估：**
- 响应 `Content-Type` 为 `text/markdown`（或 `text/markdown; charset=utf-8`）：通过——记录为前沿能力
- 否则：前瞻性建议，不算失败
- 请求报错或返回非 200：跳过并记录错误，不扣分

| 状态 | 处理方式 |
|---|---|
| 返回 `text/markdown` | 加分项——记录为前沿能力 |
| 返回标准 HTML | 前瞻性建议 |
| 请求报错 / 非 200 | 跳过，记录错误，不扣分 |

---

## 国内搜索与 AI 索引渠道（国内版新增章节）

国内 AI 平台的可见性底座是各家搜索引擎的索引。这一章节确保站点已接入国内站长平台——它们既能验证所有权、加速收录，也提供国外工具给不了的诊断数据。

### 1. 百度搜索资源平台（ziyuan.baidu.com）

百度 AI 搜索的底座是百度索引，多个国内 AI 助手也间接依赖百度。**这是国内站点最重要的一个站长平台。**

操作流程：
1. 注册并登录 ziyuan.baidu.com
2. **验证站点所有权**（三选一）：
   - 文件验证：下载 HTML 验证文件放到站点根目录
   - HTML 标签验证：在首页 `<head>` 加 meta 标签
   - CNAME 验证：添加 DNS 解析记录
3. **提交 sitemap**：资源提交 → 普通收录 → sitemap，提交 `https://[domain]/sitemap.xml`
4. **主动推送/快速收录**：新内容通过 API 主动推送，加速收录
5. **抓取诊断**：用「抓取诊断」工具模拟 Baiduspider 抓取关键页面，确认返回 200 且内容完整（可顺带验证 SSR 是否生效）
6. **robots 检测**：用平台的 robots 工具验证 robots.txt 实际生效规则（配合类别 1.3 的冲突检测）
7. 定期查看「索引量」数据，对比 sitemap 提交数，发现收录异常

**检查项：**
- [ ] 站点已在百度搜索资源平台完成验证
- [ ] sitemap 已提交且最近 30 天有更新
- [ ] 关键页面通过抓取诊断返回 200
- [ ] robots.txt 通过平台检测工具验证无冲突

### 2. 头条站长平台（zhanzhang.toutiao.com）

头条搜索是豆包生态的补充索引源，ToutiaoSpider 抓取的数据服务于字节系产品。

操作流程：
1. 登录 zhanzhang.toutiao.com
2. 验证站点所有权（文件 / meta 标签 / DNS）
3. 提交 sitemap
4. 使用抓取诊断和收录查询工具

**检查项：**
- [ ] 站点已在头条站长平台完成验证
- [ ] sitemap 已提交

### 3. Bing 站长工具（保留一句）

Bing Webmaster Tools（www.bing.com/webmasters）仍建议接入：DeepSeek 等未公开索引来源的国内 AI 平台可能依赖 Bing 索引，且 Bing 验证后可一并将站点同步给使用 Bing 数据的产品。详细操作建议见文末「出海站点建议」。

### 4. ICP 备案检查（国内版新增）

ICP 备案号是国内站点合法运营的标志，直接影响国内搜索引擎的收录信任度——未备案站点在国内搜索结果中会被显著降权，部分平台甚至不予收录。

**检查方法：**
- 查看页脚是否展示 ICP 备案号（格式如 `京ICP备12345678号-1`）
- 确认备案号链接到工信部备案查询页（`beian.miit.gov.cn`）
- 在工信部备案系统核实备案信息与域名一致

**检查项：**
- [ ] 页脚展示 ICP 备案号
- [ ] 备案号链接到 beian.miit.gov.cn
- [ ] 备案信息与当前域名、主体一致
- [ ] 如有经营性内容，检查是否有 ICP 许可证（经营性 ICP 证）

### 5. 国内访问速度 / CDN 检查（国内版新增）

国内用户的访问速度直接影响百度搜索的排名信号和抓取频率。

**检查项：**
- [ ] 从国内网络环境测量 TTFB < 800ms（见类别 8.1）
- [ ] 使用国内 CDN（见类别 8.6）；境外 CDN（如 Cloudflare 免费版）在国内访问慢且不稳定
- [ ] 用 itdog.cn / boce.com 等多地区拨测工具确认全国访问速度均匀
- [ ] 域名解析使用国内 DNS 服务商（DNSPod、阿里云 DNS 等）

---

## 出海站点建议（仅出海站点需要）

> 本节保留给有海外业务的站点。纯国内业务站点可跳过——以下工具面向国外搜索引擎，对国内 AI 平台可见性没有直接帮助。

### IndexNow 协议

**是什么：** IndexNow 是一个开放协议，允许网站在内容创建、更新或删除时即时通知搜索引擎。支持方包括 Bing、Yandex、Seznam、Naver。Google 不支持 IndexNow，但在关注该协议。

**为什么和 GEO 有关：** ChatGPT 使用 Bing 索引，Bing Copilot 也使用 Bing 索引。Bing 收录越快，这两个平台的 AI 可见性越快。

**实现检查：**
1. 检查 IndexNow key 文件：`https://[domain]/.well-known/indexnow-key.txt` 或类似路径
2. 检查 CMS 是否有 IndexNow 插件（WordPress 有官方 IndexNow 插件；许多现代 CMS 原生支持）
3. 未实现的话，给出接入建议

### Google Search Console 与 Bing Webmaster Tools

- Google Search Console：验证所有权、提交 sitemap、配置 URL 参数处理、查看 Core Web Vitals 实测数据
- Bing Webmaster Tools：验证所有权（可从 GSC 一键导入）、提交 sitemap、配置 IndexNow、参数处理
- 两个平台的「URL 参数处理」配置对应类别 4.4 的检查项

---

## 总分汇总

| 类别 | 满分 | 权重说明 |
|---|---|---|
| 可抓取性 | 15 | 核心地基 |
| 可索引性 | 12 | 核心地基 |
| 安全 | 10 | 信任信号 |
| URL 结构 | 8 | 抓取效率 |
| 移动端优化 | 10 | 搜索引擎硬性要求 |
| Core Web Vitals | 15 | 排名信号 |
| 服务端渲染 | 15 | GEO 关键 |
| 页面速度与服务器 | 15 | 性能 |
| **合计** | **100** | |

不计分检查项（类别 9、国内渠道接入清单）在报告中单独呈现，不影响总分，但国内渠道清单全部未通过时应在报告中显著提示。

### 分数解读
- **90-100**：优秀——传统 SEO 和 GEO 技术层面都扎实
- **70-89**：良好——有小问题要处理，但底子稳
- **50-69**：需改进——明显技术债，正在影响可见性
- **30-49**：差——重大问题正在阻碍抓取、收录或 AI 可见性
- **0-29**：危急——基础技术故障，需立即处理

---

## 输出格式

生成 **GEO-TECHNICAL-AUDIT.md**，结构如下：

```markdown
# GEO 技术 SEO 审计报告 — [域名]
日期：[日期]

## 技术得分：XX/100

## 分类得分
| 类别 | 得分 | 状态 |
|---|---|---|
| 可抓取性 | XX/15 | 通过/警告/失败 |
| 可索引性 | XX/12 | 通过/警告/失败 |
| 安全 | XX/10 | 通过/警告/失败 |
| URL 结构 | XX/8 | 通过/警告/失败 |
| 移动端优化 | XX/10 | 通过/警告/失败 |
| Core Web Vitals | XX/15 | 通过/警告/失败 |
| 服务端渲染 | XX/15 | 通过/警告/失败 |
| 页面速度与服务器 | XX/15 | 通过/警告/失败 |

状态说明：通过 = 拿到类别 80%+ 分数，警告 = 50-79%，失败 = <50%

## AI 爬虫放行情况
| 爬虫 | User-Agent | 状态 | 建议 |
|---|---|---|---|
| Baiduspider | Baiduspider | 放行/屏蔽 | [动作] |
| Bytespider | Bytespider | 放行/屏蔽 | [动作] |
| Kimi-User | Kimi-User | 放行/屏蔽 | [动作] |
[列出所有重点 AI 爬虫和国内搜索蜘蛛]

## 国内渠道接入情况
- [ ] 百度搜索资源平台验证 + sitemap 提交
- [ ] 头条站长平台验证 + sitemap 提交
- [ ] Bing 站长工具验证（DeepSeek 等可能依赖）
- [ ] ICP 备案号页脚展示且信息一致
- [ ] 国内 CDN + 国内访问速度达标

## 严重问题（立即修复）
[列出具体页面 URL 和问题描述]

## 警告（本月修复）
[列出详情]

## 优化建议（本季度处理）
[列出详情]

## Agent 就绪信号（不计分）

### RFC 8288 Link 响应头（服务发现）

**状态：** 存在 / 缺失 / 不适用

<!-- 如存在： -->
| 关系类型 | URL | 含义 |
|---|---|---|
| api-catalog | /.well-known/api-catalog | 可用 API 的机器可读索引 |
| mcp-server-card | /.well-known/mcp.json | MCP 服务器能力声明 |

AI Agent 和 API 客户端无需解析 HTML 即可发现你的服务。

<!-- 如缺失且为 API 优先站点： -->
**信息性建议：** 本站有 API/开发者内容，但没有用 `Link:` 响应头声明可发现的服务。

示例：`Link: </.well-known/api-catalog>; rel="api-catalog"`

适用对象：有公开 API、OpenAPI 文档或 MCP 集成的站点。
参考：RFC 8288、RFC 9609。

<!-- 如缺失且为普通业务站点：整节省略 -->

### Markdown 内容协商

**状态：** 支持 / 不支持
**测试：** GET [url]，请求头 `Accept: text/markdown`
**响应 Content-Type：** [值]

<!-- 如支持： -->
本站可按请求向 AI Agent 提供干净的 Markdown。支持内容协商的 AI 爬虫能拿到无 HTML 样板的格式化文本。

<!-- 如不支持： -->
**前瞻性建议：** Cloudflare Workers/Pages 站点可通过一行配置开启 Markdown 内容协商。AI Agent 发送 `Accept: text/markdown` 时，服务器返回干净 Markdown 而非 HTML。

- 目前为 Cloudflare 专属能力
- 适用对象：已使用 Cloudflare 基础设施的站点
- 随 AI Agent 流量增长，预计其他 CDN 和框架会跟进

## 详细发现
[按类别展开，附证据]
```

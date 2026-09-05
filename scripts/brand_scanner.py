#!/usr/bin/env python3
"""
品牌提及扫描器（国内版）— 检查品牌在国内 AI 高频引用平台上的存在感。

品牌提及与 AI 可见度的相关性约为外链的 3 倍。
（Ahrefs 2025 年 12 月对 75,000 个品牌的研究，该数据来自国外平台，
国内对应平台的权重为基于公开信息的合理推断值）

国内平台重要性排序（权重）：
1. 知乎 25% — 国内问答社区，Kimi/豆包/DeepSeek 高频引用源
2. B站 25% — 视频+弹幕/字幕转录内容可被 AI 索引
3. 百科 20% — 中文维基 + 百度百科，实体识别基石
4. 微信公众号 15% — 元宝（腾讯系 AI）的独家内容源
5. 其他技术社区 15% — CSDN/掘金/V2EX/Gitee/小红书/GitHub

反爬降级策略（重要）：
- 知乎、B站、小红书等平台对直接抓取常有 403/登录墙拦截，
  本脚本不强行抓取这些站点，而是「生成搜索入口 URL + 检查清单」，
  由 AI 浏览器（如 ego-browser）或人工打开 URL 逐项验证。
- 仅对开放 API 的站点（中文维基、Wikidata）做实时查询。
- 微信公众号无公开搜索 API，统一走搜狗微信搜索入口，需浏览器/人工验证。
"""

import sys
import json
from urllib.parse import quote_plus

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("错误：缺少依赖包。请运行：pip install requests beautifulsoup4")
    sys.exit(1)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def check_bilibili_presence(brand_name: str) -> dict:
    """检查品牌在 B站（bilibili）上的存在感。"""
    result = {
        "platform": "B站（bilibili）",
        "correlation": "国外 YouTube 研究为 0.737（最强相关），B站为国内对应平台（推断值）",
        "weight": "25%",
        "has_channel": False,
        "mentioned_in_videos": False,
        "search_url": f"https://search.bilibili.com/all?keyword={quote_plus(brand_name)}",
        "recommendations": [],
    }

    result["check_instructions"] = [
        f"打开搜索 URL 检查「{brand_name}」（B站有反爬，建议用浏览器打开）：",
        "1. 品牌是否有官方账号（UP主）？是否有官方认证标识？",
        "2. 是否有品牌自己发布的视频（教程、演示、行业观点）？",
        "3. 是否有其他 UP 主发布过关于该品牌的视频？",
        "4. 品牌相关视频的播放量和互动量如何？",
        "5. 是否有正面测评或产品演示视频？",
        "6. 视频是否带字幕/简介文本（AI 索引主要依赖文字内容）？",
    ]

    result["recommendations"] = [
        "如果没有官方账号，注册 B站官方账号并完成企业认证",
        "发布与所在行业相关的教程/科普类视频内容",
        "鼓励客户或合作 UP 主制作测评、演示类视频",
        "视频标题和简介中包含完整品牌名，便于检索",
        "开启并校对视频字幕（AI 主要读取文字转录内容）",
        "视频描述区附上官网链接，形成引用闭环",
    ]

    return result


def check_zhihu_presence(brand_name: str) -> dict:
    """检查品牌在知乎上的存在感。"""
    result = {
        "platform": "知乎",
        "correlation": "高（国内 AI 助手高频引用源，推断值）",
        "weight": "25%",
        "has_org_account": False,
        "mentioned_in_discussions": False,
        "search_url": f"https://www.zhihu.com/search?type=content&q={quote_plus(brand_name)}",
        "recommendations": [],
    }

    result["check_instructions"] = [
        f"打开搜索 URL 检查「{brand_name}」（知乎有反爬和登录墙，建议用浏览器打开）：",
        "1. 品牌是否有官方机构号？是否完成认证？",
        "2. 相关行业话题下是否有讨论提及该品牌？",
        "3. 讨论的情感倾向如何（正面/负面/中性）？",
        "4. 是否有「XX 怎么样」「求推荐」类问题下提到该品牌？",
        "5. 高赞回答中是否出现品牌名（高赞内容更易被 AI 引用）？",
        "6. 提及是否较新（近 6 个月内）？",
    ]

    result["recommendations"] = [
        "注册知乎机构号并完成企业认证",
        "关注行业相关话题，监测品牌提及",
        "以专业身份真实参与行业讨论（不要硬广）",
        "在「求推荐」「XX 怎么样」类问题下提供有价值的回答",
        "发布行业长文（知乎专栏文章常被 AI 搜索引用）",
        "知乎社区反感营销腔，内容以专业干货为主",
    ]

    return result


def check_wikipedia_presence(brand_name: str) -> dict:
    """检查品牌在中文维基百科、Wikidata 和百度百科上的实体存在。"""
    result = {
        "platform": "百科（中文维基 + 百度百科）",
        "correlation": "高（实体识别基石）",
        "weight": "20%",
        "has_zh_wikipedia_page": False,
        "has_wikidata_entry": False,
        "search_url": f"https://zh.wikipedia.org/wiki/Special:Search?search={quote_plus(brand_name)}",
        "wikidata_url": f"https://www.wikidata.org/w/index.php?search={quote_plus(brand_name)}",
        "baike_url": f"https://baike.baidu.com/search/word?word={quote_plus(brand_name)}",
        "recommendations": [],
    }

    # 中文维基百科 API（开放接口，可实时查询）
    try:
        api_url = f"https://zh.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote_plus(brand_name)}&format=json"
        response = requests.get(api_url, headers=DEFAULT_HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            search_results = data.get("query", {}).get("search", [])
            if search_results:
                # 判断首条结果是否与品牌直接相关
                top_title = search_results[0].get("title", "").lower()
                if brand_name.lower() in top_title:
                    result["has_zh_wikipedia_page"] = True
                result["zh_wikipedia_search_results"] = len(search_results)
    except Exception:
        result["zh_wikipedia_note"] = "中文维基 API 访问失败，请手动打开 search_url 检查"

    # Wikidata（语言参数切换为中文）
    try:
        wikidata_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={quote_plus(brand_name)}&language=zh&format=json"
        response = requests.get(wikidata_url, headers=DEFAULT_HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            entities = data.get("search", [])
            if entities:
                result["has_wikidata_entry"] = True
                result["wikidata_id"] = entities[0].get("id", "")
                result["wikidata_description"] = entities[0].get("description", "")
    except Exception:
        result["wikidata_note"] = "Wikidata API 访问失败，请手动打开 wikidata_url 检查"

    # 百度百科无公开 API，生成搜索 URL 供人工/浏览器验证
    result["check_instructions"] = [
        f"百度百科需人工验证：打开 {result['baike_url']}",
        "1. 百度百科是否有该品牌词条？词条内容是否完整？",
        "2. 词条是否有权威参考资料（新闻源、官网）支撑？",
        "3. 中文维基是否有该品牌词条（见上方 API 查询结果）？",
        "4. Wikidata 是否有对应实体条目？",
    ]

    result["recommendations"] = [
        "优先创建/完善百度百科词条（国内 AI 对百度百科引用更直接）",
        "百度百科词条需权威参考资料（媒体报道、官网）支撑，提前准备新闻源",
        "如符合收录标准，完善中文维基词条（维基有严格的关注度要求）",
        "确保 Wikidata 条目存在且结构化数据完整",
        "在 schema markup 中用 sameAs 指向百科/Wikidata 页面",
        "通过媒体报道和行业评测积累关注度，这是百科词条过审的前提",
    ]

    return result


def check_wechat_presence(brand_name: str) -> dict:
    """检查品牌微信公众号存在感（元宝 AI 的独家内容源）。"""
    result = {
        "platform": "微信公众号",
        "correlation": "中（元宝独家内容源，推断值）",
        "weight": "15%",
        "has_official_account": False,
        "search_url": f"https://weixin.sogou.com/weixin?type=1&query={quote_plus(brand_name)}",
        "article_search_url": f"https://weixin.sogou.com/weixin?type=2&query={quote_plus(brand_name)}",
        "recommendations": [],
    }

    result["check_instructions"] = [
        f"微信公众号无公开搜索 API，必须通过浏览器/人工打开搜狗微信搜索验证：",
        f"1. 搜公众号：{result['search_url']} — 是否有品牌官方公众号？是否已认证？",
        f"2. 搜文章：{result['article_search_url']} — 是否有文章提及该品牌？",
        "3. 公众号是否持续更新（近 3 个月有发文）？",
        "4. 是否有行业媒体/自媒体公众号写过该品牌？",
        "5. 微信搜一搜中品牌名能否搜到公众号和相关文章？",
        "注意：搜狗微信搜索有验证码拦截，自动化抓取不可靠，建议人工或 AI 浏览器操作。",
    ]

    result["recommendations"] = [
        "注册品牌官方微信公众号并完成企业认证（服务号/订阅号按业务选择）",
        "保持规律更新，公众号文章是元宝 AI 的独家内容来源",
        "文章标题和正文自然包含完整品牌名",
        "争取行业媒体公众号的报道和转载",
        "公众号资料页填写官网链接，与官网 schema sameAs 互链",
        "同步开通视频号，覆盖微信生态内的多媒体内容",
    ]

    return result


def check_other_platforms(brand_name: str) -> dict:
    """检查品牌在其他国内社区平台上的存在感。"""
    result = {
        "platform": "其他平台",
        "weight": "15%",
        "platforms_checked": {},
        "recommendations": [],
    }

    platforms = {
        "CSDN": f"https://so.csdn.net/so/search?q={quote_plus(brand_name)}",
        "掘金": f"https://juejin.cn/search?query={quote_plus(brand_name)}",
        "V2EX": f"https://v2ex.com/search?q={quote_plus(brand_name)}",
        "Gitee": f"https://search.gitee.com/?q={quote_plus(brand_name)}",
        "小红书": f"https://www.xiaohongshu.com/search_result?keyword={quote_plus(brand_name)}",
        "GitHub": f"https://github.com/search?q={quote_plus(brand_name)}",
    }

    result["platforms_checked"] = {
        name: {
            "search_url": url,
            "check_instruction": f"在{name}上搜索「{brand_name}」，检查品牌相关内容和讨论",
        }
        for name, url in platforms.items()
    }

    result["check_instructions"] = [
        "以上平台多数有反爬或登录墙，请逐一打开搜索 URL 人工/浏览器验证：",
        "技术类品牌重点：CSDN、掘金、V2EX、Gitee、GitHub",
        "消费类品牌重点：小红书（笔记常被国内 AI 引用）",
        "备注：技术品牌如有出海需求，Stack Overflow（stackoverflow.com/search?q=）仍值得检查。",
    ]

    result["recommendations"] = [
        "技术品牌：在 CSDN/掘金发布技术文章，被国内 AI 引用概率高",
        "有开源项目的品牌：维护好 GitHub 和 Gitee 双仓库，README 写清品牌信息",
        "消费品牌：运营小红书企业号，鼓励用户发布真实测评笔记",
        "V2EX 适合开发者向品牌的口碑建设（社区反感硬广，注意方式）",
        "各平台账号资料保持品牌名、官网链接一致（NAP 一致性）",
        "在官网 schema markup 的 sameAs 中汇总所有平台主页链接",
    ]

    return result


def generate_brand_report(brand_name: str, domain: str = None) -> dict:
    """生成完整的品牌提及检查报告（国内版）。

    参数: brand_name - 品牌名；domain - 官网域名（可选）
    返回值: dict - 含各平台检查结果的完整报告
    """
    import datetime

    report = {
        "brand_name": brand_name,
        "domain": domain,
        "analysis_date": datetime.date.today().isoformat(),
        "key_insight": "品牌提及与 AI 可见度的相关性约为外链的 3 倍（Ahrefs 2025.12，7.5 万品牌，国外数据）；国内平台权重为基于公开信息的合理推断值",
        "platforms": {},
        "overall_recommendations": [],
    }

    # 检查所有平台
    report["platforms"]["bilibili"] = check_bilibili_presence(brand_name)
    report["platforms"]["zhihu"] = check_zhihu_presence(brand_name)
    report["platforms"]["baike"] = check_wikipedia_presence(brand_name)
    report["platforms"]["wechat"] = check_wechat_presence(brand_name)
    report["platforms"]["other"] = check_other_platforms(brand_name)

    # 总体建议
    report["overall_recommendations"] = [
        "优先级 1：知乎 — 国内 AI 助手高频引用源。注册机构号，发布专业长文，参与行业讨论。",
        "优先级 2：B站 — 视频文字内容（标题/简介/字幕）可被 AI 索引。发布教程和行业内容。",
        "优先级 3：百科 — 先完善百度百科词条（需权威新闻源支撑），再补中文维基和 Wikidata。",
        "优先级 4：微信公众号 — 元宝 AI 的独家内容源。保持规律更新，文章自然包含品牌名。",
        "优先级 5：社区矩阵 — 技术品牌重 CSDN/掘金/GitHub/Gitee，消费品牌重小红书。",
        "跨平台：所有平台保持品牌名、官网链接一致（NAP 一致性）。",
        "Schema 标记：官网添加 sameAs 属性，链接到所有平台官方主页。",
        "监测：在各平台设置品牌提及提醒，定期复查。",
        "反爬提示：知乎/B站/小红书/搜狗微信均有反爬拦截，本清单中的搜索 URL 需浏览器或人工打开验证。",
    ]

    return report


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("用法: python brand_scanner.py <品牌名> [域名]")
        print("示例: python brand_scanner.py '某公司' example.com")
        sys.exit(1)

    brand = sys.argv[1]
    domain = sys.argv[2] if len(sys.argv) > 2 else None

    result = generate_brand_report(brand, domain)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

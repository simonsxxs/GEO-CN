#!/usr/bin/env python3
"""
中文引用性评分器（Citability Scorer）— 分析中文内容块的 AI 引用就绪度。

针对中文网页内容打分，评估段落被国产 AI 搜索（Kimi、DeepSeek、豆包、
元宝、通义、百度 AI 搜索等）引用的可能性。

中文适配要点（相对英文原版的改动）：
- 计量单位从单词数改为字符数（去空白），中文无空格分词
- 最优段落长度 200-350 字（推断值，按 1 英文词 ≈ 1.5-2 中文字换算，
  原版为 134-167 词，后续用实测数据校准）
- 定义句式、代词、句子切分、金额、具名来源等识别模式全部中文化
- 不引入 jieba 等分词依赖，具名实体用启发式识别（零新第三方依赖）
"""

import sys
import json
import re
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Required packages not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


def count_chars(text: str) -> int:
    """
    功能：统计文本的字符数（去除所有空白字符后的长度）。
    参数：text — 待统计的文本字符串。
    返回值：int，去空白后的字符数。
    """
    return len(re.sub(r"\s", "", text))


def split_sentences(text: str) -> list:
    """
    功能：按中文标点切分句子（保留英文句点作为兜底）。
    参数：text — 待切分的文本字符串。
    返回值：list，非空句子列表。
    """
    parts = re.split(r"[。！？!?.；;]+", text)
    return [s for s in parts if count_chars(s) > 0]


def score_passage(text: str, heading: Optional[str] = None) -> dict:
    """
    功能：对单个中文段落进行 AI 引用性评分（0-100 分，五个维度加权）。
    参数：text — 段落文本；heading — 段落所属标题（可为 None）。
    返回值：dict，包含标题、字符数、总分、等级、中文等级标签、
            五维度分明细和段落预览。
    """
    char_count = count_chars(text)
    sentences = split_sentences(text)

    scores = {
        "answer_block_quality": 0,
        "self_containment": 0,
        "structural_readability": 0,
        "statistical_density": 0,
        "uniqueness_signals": 0,
    }

    # === 维度 1：答案块质量（满分 30） ===
    abq_score = 0

    # 含定义句式（"是指""简单来说""换句话说"等）
    definition_patterns = [
        r"是指",
        r"指的是",
        r"意为",
        r"定义为",
        r"所谓[^。！？]{1,30}是指",
        r"简单来说",
        r"简而言之",
        r"换句话说",
        r"也就是说",
        r"[^。！？]{1,20}是(?:一种|一个|一项|一类)",
    ]
    for pattern in definition_patterns:
        if re.search(pattern, text):
            abq_score += 15
            break

    # 答案前置：前 100 字（推断值，原版为前 60 词）内含判断词或数字
    front_window = re.sub(r"\s", "", text)[:100]
    if re.search(r"[是为指]", front_window) or re.search(
        r"[\d%％]|元|万|亿", front_window
    ):
        abq_score += 15

    # 问句标题加分（中英文问号均可）
    if heading and heading.rstrip().endswith(("？", "?")):
        abq_score += 10

    # 短句清晰度：8-40 字的句子占比 × 10（按中文标点切句后统计）
    if sentences:
        short_clear = sum(1 for s in sentences if 8 <= count_chars(s) <= 40)
        clarity_ratio = short_clear / len(sentences)
        abq_score += int(clarity_ratio * 10)

    # 含具名引用（"据…显示/报告/研究""研究表明""实测"等）
    if re.search(
        r"(?:据[^。！？]{1,20}(?:显示|报告|研究|统计)|根据[^。！？]{1,20}(?:数据|报告|研究|统计)|研究表明|实测)",
        text,
    ):
        abq_score += 10

    scores["answer_block_quality"] = min(abq_score, 30)

    # === 维度 2：自包含性（满分 25） ===
    sc_score = 0

    # 字数区间评分（推断值，按 1 英文词 ≈ 1.5-2 中文字换算）：
    # 最优 200-350 字 +10；良好 120-500 字 +7；一般 60-800 字 +4；
    # 过短（<60 字）或过长（>800 字）零分
    if 200 <= char_count <= 350:
        sc_score += 10
    elif 120 <= char_count <= 500:
        sc_score += 7
    elif 60 <= char_count <= 800:
        sc_score += 4

    # 代词密度：代词出现数 ÷ 总字符数，越低说明段落越自包含
    pronoun_count = len(re.findall(r"它们|这些|那些|[它他她这那此该其]", text))
    if char_count > 0:
        pronoun_ratio = pronoun_count / char_count
        if pronoun_ratio < 0.01:
            sc_score += 8
        elif pronoun_ratio < 0.02:
            sc_score += 5
        elif pronoun_ratio < 0.03:
            sc_score += 3

    # 具名实体（启发式识别，不引入分词依赖，精度有损失）：
    # 大写拉丁词（如 Kimi、iPhone）、《书名号》内容、引号「」/“”内容
    entity_count = len(re.findall(r"[A-Z][A-Za-z0-9]+", text))
    entity_count += len(re.findall(r"《[^》]+》", text))
    entity_count += len(re.findall(r"[「“][^」”]{1,20}[」”]", text))
    if entity_count >= 3:
        sc_score += 7
    elif entity_count >= 1:
        sc_score += 4

    scores["self_containment"] = min(sc_score, 25)

    # === 维度 3：结构可读性（满分 20） ===
    sr_score = 0

    # 平均句长：12-30 字 +8，8-40 字 +5（推断值，按中文表达习惯设定）
    if sentences:
        avg_sentence_length = char_count / len(sentences)
        if 12 <= avg_sentence_length <= 30:
            sr_score += 8
        elif 8 <= avg_sentence_length <= 40:
            sr_score += 5
        else:
            sr_score += 2

    # 含列举连接词
    if re.search(r"首先|其次|再次|最后|第一|第二|第三|另外|此外", text):
        sr_score += 4

    # 含编号结构（"1.""1、""第一步""第二点"等）
    if re.search(r"\d+[、.．]|第[一二三四五六七八九十][步点]", text):
        sr_score += 4

    # 含段落换行（说明有结构分层）
    if "\n" in text:
        sr_score += 4

    scores["structural_readability"] = min(sr_score, 20)

    # === 维度 4：数据密度（满分 15） ===
    sd_score = 0

    # 百分比（每个 +3，封顶 6），兼容全角百分号
    pct_count = len(re.findall(r"\d+(?:\.\d+)?\s*(?:%|％)", text))
    sd_score += min(pct_count * 3, 6)

    # 金额（每个 +3，封顶 5）：人民币符号或"元/万元/亿元"
    money_count = len(re.findall(r"[¥￥]\s*\d", text))
    money_count += len(re.findall(r"\d+(?:\.\d+)?\s*(?:万元|亿元|元)", text))
    sd_score += min(money_count * 3, 5)

    # 数字+中文量词（每个 +2，封顶 4）；兼容中文数字（三项、五种）
    quantifier_count = len(
        re.findall(r"(?:\d+|[一二三四五六七八九十百千万两])\s*(?:个|家|款|次|倍|位|名|篇|条|项|种|类|步)", text)
    )
    sd_score += min(quantifier_count * 2, 4)

    # 含年份（体现时效性）
    if re.search(r"(?:19|20)\d{2}\s*年?", text):
        sd_score += 2

    # 具名来源（每类 +2，最多 6）：据/根据/来自 + 机构 + 数据/报告/研究/统计
    source_patterns = [
        r"据[^。！？]{1,20}(?:数据|报告|研究|统计|显示)",
        r"根据[^。！？]{1,20}(?:数据|报告|研究|统计)",
        r"来自[^。！？]{1,20}(?:数据|报告|研究|统计)",
    ]
    for pattern in source_patterns:
        if re.search(pattern, text):
            sd_score += 2

    scores["statistical_density"] = min(sd_score, 15)

    # === 维度 5：独特性（满分 10） ===
    us_score = 0

    # 原创数据声明（"我们的实测""笔者统计""亲测""踩坑"等）
    if re.search(
        r"(?:我们|我|笔者|团队)的?(?:研究|实测|测试|数据|案例|统计|经验)|亲测|踩坑",
        text,
    ):
        us_score += 5

    # 案例举证
    if re.search(r"案例|举个例子|例如|比如|以[^。！？]{1,20}为例", text):
        us_score += 3

    # 具体工具/产品提及（拉丁品牌词或《》书名号内容）
    if re.search(r"[A-Z][A-Za-z0-9]+|《[^》]+》", text):
        us_score += 2

    scores["uniqueness_signals"] = min(us_score, 10)

    # === 汇总总分与等级 ===
    total = sum(scores.values())

    # 等级映射与原版一致（A ≥80 / B ≥65 / C ≥50 / D ≥35 / F <35），label 改中文
    if total >= 80:
        grade = "A"
        label = "高度可引用"
    elif total >= 65:
        grade = "B"
        label = "引用性良好"
    elif total >= 50:
        grade = "C"
        label = "引用性中等"
    elif total >= 35:
        grade = "D"
        label = "引用性较低"
    else:
        grade = "F"
        label = "引用性差"

    preview_source = re.sub(r"\s", "", text)
    return {
        "heading": heading,
        "char_count": char_count,
        "total_score": total,
        "grade": grade,
        "label": label,
        "breakdown": scores,
        "preview": preview_source[:60] + ("..." if len(preview_source) > 60 else ""),
    }


def analyze_page_citability(url: str) -> dict:
    """
    功能：抓取网页并分析页面上所有内容块的引用性得分，输出页面级汇总。
    参数：url — 待分析的网页地址（http/https）。
    返回值：dict，包含分析块数、平均分、最优长度段落数、等级分布、
            Top5/Bottom5 段落和全部段落明细；抓取失败返回 error 字段。
    """
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
            timeout=30,
        )
        response.raise_for_status()
        # 中文站点常省略 charset 声明，requests 会误判为 ISO-8859-1 导致乱码，
        # 这里按内容自动探测编码，避免中文文本被错误解码后大面积零分误判
        response.encoding = response.apparent_encoding or response.encoding
    except Exception as e:
        return {"error": f"Failed to fetch page: {str(e)}"}

    soup = BeautifulSoup(response.text, "lxml")

    # 剔除非正文元素
    for element in soup.find_all(
        ["script", "style", "nav", "footer", "header", "aside", "form"]
    ):
        element.decompose()

    # 按 h1-h4 标题分块提取内容
    blocks = []
    current_heading = "页面开头"
    current_paragraphs = []

    for element in soup.find_all(["h1", "h2", "h3", "h4", "p", "ul", "ol", "table"]):
        if element.name.startswith("h"):
            # 保存上一个块
            if current_paragraphs:
                combined = " ".join(current_paragraphs)
                if count_chars(combined) >= 20:
                    blocks.append(
                        {"heading": current_heading, "content": combined}
                    )
            current_heading = element.get_text(strip=True)
            current_paragraphs = []
        else:
            text = element.get_text(strip=True)
            if text and count_chars(text) >= 10:
                current_paragraphs.append(text)

    # 收尾最后一个块
    if current_paragraphs:
        combined = " ".join(current_paragraphs)
        if count_chars(combined) >= 20:
            blocks.append({"heading": current_heading, "content": combined})

    # 逐块评分
    scored_blocks = []
    for block in blocks:
        score = score_passage(block["content"], block["heading"])
        scored_blocks.append(score)

    # 页面级汇总指标
    if scored_blocks:
        avg_score = sum(b["total_score"] for b in scored_blocks) / len(scored_blocks)
        top_blocks = sorted(scored_blocks, key=lambda x: x["total_score"], reverse=True)[:5]
        bottom_blocks = sorted(scored_blocks, key=lambda x: x["total_score"])[:5]

        # 最优长度段落数（200-350 字，推断值）
        optimal_count = sum(
            1 for b in scored_blocks if 200 <= b["char_count"] <= 350
        )
    else:
        avg_score = 0
        top_blocks = []
        bottom_blocks = []
        optimal_count = 0

    # 等级分布
    grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for block in scored_blocks:
        grade_dist[block["grade"]] += 1

    return {
        "url": url,
        "total_blocks_analyzed": len(scored_blocks),
        "average_citability_score": round(avg_score, 1),
        "optimal_length_passages": optimal_count,
        "grade_distribution": grade_dist,
        "top_5_citable": top_blocks,
        "bottom_5_citable": bottom_blocks,
        "all_blocks": scored_blocks,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: python citability_scorer.py <url>")
        print("Returns JSON with citability analysis for all content blocks.")
        sys.exit(1)

    url = sys.argv[1]
    result = analyze_page_citability(url)
    print(json.dumps(result, indent=2, default=str, ensure_ascii=False))

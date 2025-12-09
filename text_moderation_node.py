import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import re


def load_moderation_keywords():
    """
    加载敏感词列表
    可以从文件、数据库或直接定义
    """
    # 这里定义一些基本的敏感词分类
    # 在实际应用中，建议从外部文件或数据库加载
    moderation_keywords = {
        "violence": ["杀", "死", "暴力", "打斗", "血腥", "战争", "恐怖", "威胁"],
        "adult": ["色情", "成人", "性", "裸露", "露骨", "色情内容"],
        "illegal": ["毒品", "赌博", "诈骗", "违法", "犯罪", "走私", "盗版"],
        "hate": ["歧视", "种族", "仇恨", "辱骂", "侮辱", "诽谤"],
        "politics": ["政治", "政府", "领导人", "敏感政治话题"]  # 根据需要调整
    }
    return moderation_keywords


def moderate_text_with_llm(text: str) -> Dict[str, Any]:
    """
    使用LLM进行文本内容审查

    Args:
        text: 待审查的文本

    Returns:
        审查结果字典
    """
    load_dotenv()

    chatLLM = ChatOpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DASHSCOPE_API_URL"),
        model="qwen-plus",  # 可以使用通文本模型如 qwen-plus
        temperature=0.1  # 降低温度以获得更一致的判断
    )

    system_prompt = """你是一个专业的文本内容审核员。请审核用户输入的文本内容是否包含不当信息。

审核标准包括但不限于：
1. 暴力、血腥内容
2. 色情、成人内容
3. 违法犯罪相关内容
4. 仇恨言论、歧视内容
5. 其他违反社区准则的内容

请以JSON格式回复，包含以下字段：
- is_safe: boolean (true表示安全，false表示不安全)
- risk_level: string ("low", "medium", "high")
- categories: array (检测到的风险类别，如["violence", "adult"])
- reasons: array (具体原因说明)
- confidence: number (0-1之间的置信度)

示例回复：
{
  "is_safe": false,
  "risk_level": "high",
  "categories": ["violence"],
  "reasons": ["文本包含暴力内容"],
  "confidence": 0.95
}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请审核以下文本内容：\n\n{text}"}
    ]

    try:
        response = chatLLM.invoke(messages)
        # 解析LLM的回复
        content = response.content

        # 尝试提取JSON内容
        import json
        # 如果回复包含markdown格式的JSON，提取JSON部分
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_content = content[json_start:json_end].strip()
            result = json.loads(json_content)
        else:
            # 尝试直接解析
            result = json.loads(content)

        return result
    except Exception as e:
        # 如果LLM解析失败，返回到关键词检测
        print(f"LLM文本解析失败: {e}")
        return moderate_text_with_keywords(text)


def moderate_text_with_keywords(text: str) -> Dict[str, Any]:
    """
    使用关键词匹配进行文本审查（备用方案）

    Args:
        text: 待审查的文本

    Returns:
        审查结果字典
    """
    moderation_keywords = load_moderation_keywords()
    text_lower = text.lower()

    detected_categories = []
    detected_keywords = []

    for category, keywords in moderation_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                detected_categories.append(category)
                detected_keywords.append(keyword)

    is_safe = len(detected_categories) == 0
    risk_level = "low" if is_safe else ("high" if len(detected_categories) >= 3 else "medium")

    return {
        "is_safe": is_safe,
        "risk_level": risk_level,
        "categories": detected_categories,
        "reasons": [f"检测到敏感词: {', '.join(detected_keywords)}"] if detected_keywords else [],
        "confidence": 0.8 if detected_keywords else 1.0,
        "detected_keywords": detected_keywords
    }


def text_moderation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    文本审查节点函数

    Args:
        state: 状态字典，包含文本内容和其他上下文

    Returns:
        包含审查结果的字典
    """
    # 从状态中获取文本内容
    text_content = state.get("text_content", "")

    if not text_content or not text_content.strip():
        return {
            "text_moderation_result": {
                "is_safe": True,
                "risk_level": "low",
                "categories": [],
                "reasons": ["无文本内容"],
                "confidence": 1.0,
                "method": "empty_content"
            },
            "error": None
        }

    try:
        # 优先使用LLM进行审查
        result = moderate_text_with_llm(text_content)
        result["method"] = "llm_analysis"

        return {
            "text_moderation_result": result,
            "error": None
        }
    except Exception as e:
        # 如果LLM审查失败，使用关键词检测作为备用
        try:
            result = moderate_text_with_keywords(text_content)
            result["method"] = "keyword_analysis"

            return {
                "text_moderation_result": result,
                "error": None
            }
        except Exception as e2:
            return {
                "text_moderation_result": None,
                "error": f"文本审查失败: {str(e2)}"
            }


def moderate_multiple_texts(texts: List[str]) -> Dict[str, Any]:
    """
    批量审查多个文本

    Args:
        texts: 文本列表

    Returns:
        批量审查结果
    """
    results = []
    overall_safe = True
    highest_risk = "low"

    for text in texts:
        result = moderate_text_with_llm(text) if text else {"is_safe": True, "risk_level": "low"}
        results.append(result)

        if not result.get("is_safe", True):
            overall_safe = False

        # 更新最高风险级别
        risk = result.get("risk_level", "low")
        if risk == "high":
            highest_risk = "high"
        elif risk == "medium" and highest_risk == "low":
            highest_risk = "medium"

    return {
        "overall_safe": overall_safe,
        "highest_risk_level": highest_risk,
        "individual_results": results,
        "total_texts": len(texts)
    }


# 测试函数
if __name__ == "__main__":
    # 测试文本审查
    test_texts = [
        "今天天气很好",
        "这是一段包含暴力的内容",
        "正常的商业交流内容",
        "测试敏感内容检测"
    ]

    for text in test_texts:
        print(f"审查文本: {text}")
        result = moderate_text_with_llm(text)
        print(f"审查结果: {result}")
        print("-" * 50)
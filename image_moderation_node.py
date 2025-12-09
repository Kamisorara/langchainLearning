import os
import base64
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


def moderate_image_with_llm(image_base64: str) -> Dict[str, Any]:
    """
    使用LLM进行图片内容审查

    Args:
        image_base64: 图片的base64编码

    Returns:
        图片审查结果字典
    """
    load_dotenv()

    chatLLM = ChatOpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DASHSCOPE_API_URL"),
        model="qwen3-vl-plus",  # 使用视觉模型
        temperature=0.1
    )

    system_prompt = """你是一个专业的图片内容审核员。请审核图片是否包含不当信息。

审核标准包括但不限于：
1. 暴力、血腥内容：如武器、血迹、打斗场面、虐待等
2. 色情、成人内容：如裸露、性行为、性暗示等
3. 违法犯罪内容：如毒品、赌博、诈骗工具等
4. 仇恨、歧视内容：如种族歧视、宗教歧视等
5. 不适宜内容：如令人恶心、恐怖的内容

请以JSON格式回复，包含以下字段：
- is_safe: boolean (true表示安全，false表示不安全)
- risk_level: string ("low", "medium", "high")
- categories: array (检测到的风险类别，如["violence", "adult"])
- reasons: array (具体原因说明)
- confidence: number (0-1之间的置信度)
- description: string (图片内容描述，用于记录)

示例回复：
{
  "is_safe": false,
  "risk_level": "high",
  "categories": ["violence"],
  "reasons": ["图片包含武器和暴力场面"],
  "confidence": 0.95,
  "description": "图片显示一个人持有武器"
}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": [
            {"type": "text", "text": "请审核这张图片的内容是否安全"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpg;base64,{image_base64}"}}
        ]}
    ]

    try:
        response = chatLLM.invoke(messages)
        content = response.content

        # 尝试提取JSON内容
        import json
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_content = content[json_start:json_end].strip()
            result = json.loads(json_content)
        else:
            result = json.loads(content)

        return result
    except Exception as e:
        print(f"LLM图片解析失败: {e}")
        # 如果解析失败，返回保守结果（假设不安全）
        return {
            "is_safe": False,
            "risk_level": "medium",
            "categories": ["unknown"],
            "reasons": ["图片分析失败，需要人工审核"],
            "confidence": 0.5,
            "description": "无法分析图片内容",
            "method": "analysis_failed"
        }


def analyze_image_content(image_base64: str) -> Dict[str, Any]:
    """
    分析图片内容（非审核用途）

    Args:
        image_base64: 图片的base64编码

    Returns:
        图片分析结果
    """
    load_dotenv()

    chatLLM = ChatOpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DASHSCOPE_API_URL"),
        model="qwen3-vl-plus",
        temperature=0.3
    )

    messages = [
        {"role": "system", "content": "你是一个专业的图片分析师，请客观描述图片中的内容。"},
        {"role": "user", "content": [
            {"type": "text", "text": "请详细描述这张图片的内容"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpg;base64,{image_base64}"}}
        ]}
    ]

    try:
        response = chatLLM.invoke(messages)
        return {
            "description": response.content,
            "success": True,
            "method": "llm_analysis"
        }
    except Exception as e:
        return {
            "description": f"图片分析失败: {str(e)}",
            "success": False,
            "method": "analysis_failed"
        }


def image_moderation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    图片审查节点函数

    Args:
        state: 状态字典，包含图片base64数据和其他上下文

    Returns:
        包含图片审查结果的字典
    """
    # 从状态中获取图片base64数据
    image_base64 = state.get("image_base64", None)

    if not image_base64:
        return {
            "image_moderation_result": {
                "is_safe": True,
                "risk_level": "low",
                "categories": [],
                "reasons": ["无图片内容"],
                "confidence": 1.0,
                "description": "未提供图片",
                "method": "no_content"
            },
            "image_analysis_result": "",
            "error": None
        }

    try:
        # 进行图片内容审查
        moderation_result = moderate_image_with_llm(image_base64)

        # 同时进行图片内容分析（用于记录）
        analysis_result = analyze_image_content(image_base64)

        return {
            "image_moderation_result": moderation_result,
            "image_analysis_result": analysis_result.get("description", ""),
            "error": None
        }
    except Exception as e:
        return {
            "image_moderation_result": None,
            "image_analysis_result": "",
            "error": f"图片审查失败: {str(e)}"
        }


# 测试函数
if __name__ == "__main__":
    from llm_node import load_image_as_base64

    try:
        # 测试图片审查
        image_base64 = load_image_as_base64("./images/image1.jpg")
        print("开始图片内容审查...")

        # 进行审查
        result = image_moderation_node({"image_base64": image_base64})

        print("审查结果:")
        print(f"错误: {result.get('error')}")
        print(f"审查结果: {result.get('image_moderation_result')}")
        print(f"分析结果: {result.get('image_analysis_result')[:200]}...")

    except Exception as e:
        print(f"测试失败: {e}")

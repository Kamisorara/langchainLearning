from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, MessagesState, END, START
from llm_node import llm_node, llm_node_legacy
from text_moderation_node import text_moderation_node
from image_moderation_node import image_moderation_node

# 定义自定义状态类型，用于图片处理
class ImageProcessingState(TypedDict):
    """图片处理状态定义"""
    image_base64: str  # 图片的base64编码
    messages: list     # 消息列表
    result: str        # 处理结果（字符串格式）
    error: str         # 错误信息

# 定义综合内容审查状态类型
class ContentModerationState(TypedDict):
    """综合内容审查状态定义"""
    image_base64: str              # 图片的base64编码（可选）
    text_content: str              # 文本内容（可选）
    text_moderation_result: dict   # 文本审查结果
    image_moderation_result: dict  # 图片审查结果
    image_analysis_result: str     # 图片分析结果（描述）
    overall_safe: bool             # 综合安全性判断
    risk_level: str                # 风险级别
    recommendations: List[str]     # 建议列表
    error: str                     # 错误信息

def should_process_image(state: ContentModerationState) -> bool:
    """判断是否需要处理图片"""
    return bool(state.get("image_base64"))

def should_process_text(state: ContentModerationState) -> bool:
    """判断是否需要处理文本"""
    return bool(state.get("text_content"))

def combine_moderation_results(state: ContentModerationState) -> ContentModerationState:
    """综合文本和图片审查结果"""
    text_result = state.get("text_moderation_result", {})
    image_moderation_result = state.get("image_moderation_result", {})
    image_analysis_result = state.get("image_analysis_result", "")
  
    # 初始化安全性判断
    overall_safe = True
    risk_level = "low"
    recommendations = []

    # 分析文本审查结果
    if text_result:
        text_safe = text_result.get("is_safe", True)
        text_risk = text_result.get("risk_level", "low")
        text_categories = text_result.get("categories", [])

        if not text_safe:
            overall_safe = False
            risk_level = max(risk_level, text_risk, key=lambda x: ["low", "medium", "high"].index(x))

            if text_categories:
                recommendations.append(f"文本包含{', '.join(text_categories)}类内容")

    # 分析图片审查结果
    if image_moderation_result:
        image_safe = image_moderation_result.get("is_safe", True)
        image_risk = image_moderation_result.get("risk_level", "low")
        image_categories = image_moderation_result.get("categories", [])

        if not image_safe:
            overall_safe = False
            risk_level = max(risk_level, image_risk, key=lambda x: ["low", "medium", "high"].index(x))

            if image_categories:
                recommendations.append(f"图片包含{', '.join(image_categories)}类内容")
        else:
            recommendations.append("图片内容安全")

    # 分析图片内容描述（如果存在）
    if image_analysis_result:
        recommendations.append("图片已分析描述")

    # 生成综合建议
    if not overall_safe:
        recommendations.insert(0, "内容审核不通过，建议修改")
    else:
        recommendations.insert(0, "内容审核通过")

    return {
        **state,
        "overall_safe": overall_safe,
        "risk_level": risk_level,
        "recommendations": recommendations,
        "error": None
    }

# 创建综合内容审查的graph
def create_content_moderation_graph():
    """创建用于综合内容审查的graph"""
    graph = StateGraph(ContentModerationState)

    # 添加节点
    graph.add_node("text_moderator", text_moderation_node)
    graph.add_node("image_moderator", image_moderation_node)
    graph.add_node("result_combiner", combine_moderation_results)

    # 设置入口和流程
    graph.add_edge(START, "text_moderator")

    # 条件边：如果有图片则进行图片审查
    graph.add_conditional_edges(
        "text_moderator",
        should_process_image,
        {
            True: "image_moderator",
            False: "result_combiner"
        }
    ) 

    # 图片审查完后合并结果
    graph.add_edge("image_moderator", "result_combiner")
    graph.add_edge("result_combiner", END)

    return graph.compile()


# 创建纯图片内容审查的graph
def create_image_moderation_graph():
    """创建用于纯图片内容审查的graph"""
    graph = StateGraph(ContentModerationState)

    # 添加节点
    graph.add_node("image_moderator", image_moderation_node)

    graph.add_edge(START, "image_moderator")
    graph.add_edge("image_moderator", END)

    return graph.compile()

# 创建图片处理的graph（保持原有功能）
def create_image_processing_graph():
    """创建用于图片处理的graph"""
    graph = StateGraph(ImageProcessingState)
    graph.add_node("image_processor", llm_node)

    graph.add_edge(START, "image_processor")
    graph.add_edge("image_processor", END)

    return graph.compile()

# 创建原有的graph（保持向后兼容）
def create_legacy_graph():
    """创建原有的graph用于向后兼容"""
    graph = StateGraph(MessagesState)
    graph.add_node("llm_node", llm_node_legacy)

    graph.add_edge(START, "llm_node")
    graph.add_edge("llm_node", END)

    return graph.compile()

# 实例化graphs
content_moderation_graph = create_content_moderation_graph()
image_moderation_graph = create_image_moderation_graph()
image_graph = create_image_processing_graph()
legacy_graph = create_legacy_graph()

# 保持原有的graph变量用于向后兼容
graph = legacy_graph

# 便捷函数
def process_image_moderation(image_base64: str) -> Dict[str, Any]:
    """
    使用纯图片内容审查graph处理图片

    Args:
        image_base64: 图片的base64编码

    Returns:
        图片审查结果
    """
    # 检查是否有图片数据
    if not image_base64:
        return {
            "success": False,
            "data": None,
            "error": "No image provided"
        }

    initial_state = {
        "text_content": "",
        "image_base64": image_base64,
        "text_moderation_result": {},
        "image_moderation_result": {},
        "image_analysis_result": "",
        "overall_safe": True,
        "risk_level": "low",
        "recommendations": [],
        "error": None
    }

    try:
        result = image_moderation_graph.invoke(initial_state)

        # 检查处理结果
        if result.get("error"):
            return {
                "success": False,
                "data": None,
                "error": result.get("error")
            }

        return {
            "success": True,
            "data": {
                "overall_safe": result.get("overall_safe"),
                "risk_level": result.get("risk_level"),
                "recommendations": result.get("recommendations", []),
                "image_moderation": result.get("image_moderation_result"),
                "image_analysis": result.get("image_analysis_result")
            },
            "error": result.get("error")
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }

def process_content_moderation(text_content: str = "", image_base64: str = "") -> Dict[str, Any]:
    """
    使用综合内容审查graph处理文本和图片

    Args:
        text_content: 文本内容（可选）
        image_base64: 图片的base64编码（可选）

    Returns:
        综合审查结果
    """
    # 检查是否有内容
    if not text_content and not image_base64:
        return {
            "success": False,
            "data": None,
            "error": "No content provided"
        }

    initial_state = {
        "text_content": text_content,
        "image_base64": image_base64,
        "text_moderation_result": {},
        "image_moderation_result": {},
        "image_analysis_result": "",
        "overall_safe": True,
        "risk_level": "low",
        "recommendations": [],
        "error": None
    }

    try:
        result = content_moderation_graph.invoke(initial_state)

        # 检查处理结果
        if result.get("error"):
            return {
                "success": False,
                "data": None,
                "error": result.get("error")
            }

        return {
            "success": True,
            "data": {
                "overall_safe": result.get("overall_safe"),
                "risk_level": result.get("risk_level"),
                "recommendations": result.get("recommendations", []),
                "text_moderation": result.get("text_moderation_result"),
                "image_moderation": result.get("image_moderation_result"),
                "image_analysis": result.get("image_analysis_result")
            },
            "error": result.get("error")
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }

def process_image_with_graph(image_base64: str) -> Dict[str, Any]:
    """
    使用graph处理图片的便捷函数

    Args:
        image_base64: 图片的base64编码

    Returns:
        处理结果
    """
    # 检查是否有图片数据
    if not image_base64:
        return {
            "success": False,
            "data": None,
            "error": "No image provided"
        }

    initial_state = {
        "image_base64": image_base64,
        "messages": [],
        "result": None,
        "error": None
    }

    try:
        result = image_graph.invoke(initial_state)

        # 检查处理结果
        if result.get("error"):
            return {
                "success": False,
                "data": None,
                "error": result.get("error")
            }

        return {
            "success": True,
            "data": result.get("result"),
            "error": result.get("error")
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }

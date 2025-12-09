from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, MessagesState, END, START
from llm_node import llm_node, llm_node_legacy

# 定义自定义状态类型，用于图片处理
class ImageProcessingState(TypedDict):
    """图片处理状态定义"""
    image_base64: str  # 图片的base64编码
    messages: list     # 消息列表
    result: str        # 处理结果（字符串格式）
    error: str         # 错误信息

# 创建图片处理的graph
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
image_graph = create_image_processing_graph()
legacy_graph = create_legacy_graph()

# 保持原有的graph变量用于向后兼容
graph = legacy_graph

# 便捷函数
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

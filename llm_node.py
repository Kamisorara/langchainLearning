import os
import base64
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState


def load_image_as_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def process_image_base64(image_base64: str) -> str:

    # 加载环境变量
    load_dotenv()

    chatLLM = ChatOpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DASHSCOPE_API_URL"),
        model="qwen3-vl-plus",
        streaming=True
        # other params...
    )
    messages = [
        {"role": "system", "content": "你是一个专业的图片审核员，回复你在图片中看到了什么。"},
        {"role": "user", "content": [
            {"type": "text", "text": "请描述图片中的内容"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpg;base64,{image_base64}"}}
        ]}
    ]
    response = chatLLM.invoke(messages)

    json_response = response.model_dump_json()
    print(json_response)
    return json_response


def llm_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LLM节点处理函数，从状态中获取图片数据并进行处理

    Args:
        state: 状态字典，包含图片数据和处理上下文

    Returns:
        包含处理结果的字典
    """
    # 从状态中获取图片base64数据
    image_base64 = state.get("image_base64", None)

    if not image_base64:
        # 如果没有传入图片，直接返回，不进行任何处理
        return {
            "error": "No image provided",
            "result": None
        }

    # 处理图片
    try:
        result = process_image_base64(image_base64)
        return {
            "result": result,
            "error": None
        }
    except Exception as e:
        return {
            "error": str(e),
            "result": None
        }


# 保持原有的向后兼容性
def llm_node_legacy(state: MessagesState) -> str:
    """保持向后兼容的原始函数"""
    image_1_base64 = load_image_as_base64("./images/image1.jpg")
    result = process_image_base64(image_1_base64)
    return result
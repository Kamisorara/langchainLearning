import os
import base64
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

def load_image_as_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


image_1_base64 = load_image_as_base64("./images/image1.jpg")

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
        {"type": "image_url", "image_url": {"url": f"data:image/jpg;base64,{image_1_base64}"}}
    ]}
]
response = chatLLM.invoke(messages)

json_response = response.model_dump_json()

print(json_response)
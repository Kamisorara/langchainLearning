"""
测试综合内容审查功能
"""
import base64
from main import process_content_moderation
from llm_node import load_image_as_base64

def test_text_only_moderation():
    """测试纯文本审查"""
    print("=== 测试纯文本审查 ===")

    test_cases = [
        ("今天天气很好，适合出门散步", "正常文本"),
        ("这是一段包含暴力和血腥的内容", "包含暴力内容"),
        ("正常的商业交流内容", "正常商务文本"),
        ("测试色情和成人内容检测", "包含敏感内容"),
        ("", "空文本")
    ]

    for text, description in test_cases:
        print(f"\n测试内容: {description}")
        print(f"文本: {text}")
        result = process_content_moderation(text_content=text)
        print(f"审查结果: {result}")
        print("-" * 50)

def test_image_only_moderation():
    """测试纯图片审查"""
    print("\n=== 测试纯图片审查 ===")

    try:
        # 加载测试图片
        image_base64 = load_image_as_base64("./images/image1.jpg")
        result = process_content_moderation(image_base64=image_base64)
        print(f"图片审查结果: {result}")
    except Exception as e:
        print(f"图片审查失败: {e}")

def test_combined_moderation():
    """测试文本+图片综合审查"""
    print("\n=== 测试文本+图片综合审查 ===")

    test_cases = [
        ("请描述这张图片的内容", "正常请求"),
        ("分析图片中的暴力元素", "包含敏感词请求"),
        ("这是一张风景照片", "正常描述"),
        ("检测图片中的成人内容", "敏感请求")
    ]

    try:
        image_base64 = load_image_as_base64("./images/image1.jpg")

        for text, description in test_cases:
            print(f"\n测试内容: {description}")
            print(f"文本: {text}")
            result = process_content_moderation(text_content=text, image_base64=image_base64)
            print(f"综合审查结果: {result}")
            print("-" * 50)

    except Exception as e:
        print(f"综合审查失败: {e}")

def test_edge_cases():
    """测试边界情况"""
    print("\n=== 测试边界情况 ===")

    # 空内容
    print("测试空内容:")
    result = process_content_moderation()
    print(f"结果: {result}")

    # 只有空格的文本
    print("\n测试只有空格的文本:")
    result = process_content_moderation(text_content="   ")
    print(f"结果: {result}")

    # 很长的文本
    print("\n测试长文本:")
    long_text = "正常内容 " * 100
    result = process_content_moderation(text_content=long_text)
    print(f"结果: {result.get('success', False)}, 风险级别: {result.get('data', {}).get('risk_level', 'unknown')}")

if __name__ == "__main__":
    print("开始测试综合内容审查功能...")

    # 运行各种测试
    test_text_only_moderation()
    test_image_only_moderation()
    test_combined_moderation()
    test_edge_cases()

    print("\n测试完成!")
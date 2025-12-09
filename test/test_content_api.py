"""
测试内容审查API
"""
import requests
import json

BASE_URL = "http://localhost:8080"

def test_text_moderation_api():
    """测试文本审查API"""
    print("=== 测试文本审查API ===")

    test_cases = [
        {"text_content": "今天天气很好", "description": "正常文本"},
        {"text_content": "这是一段包含暴力和血腥的内容", "description": "敏感文本"},
        {"text_content": "正常的商业交流", "description": "商务文本"}
    ]

    for case in test_cases:
        print(f"\n测试: {case['description']}")
        print(f"文本: {case['text_content']}")

        try:
            response = requests.post(
                f"{BASE_URL}/moderate-text",
                json=case
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ API调用成功")
                print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            else:
                print(f"❌ API调用失败: {response.status_code}")
                print(f"错误: {response.text}")

        except Exception as e:
            print(f"❌ 请求异常: {e}")

        print("-" * 60)

def test_health_check():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")

    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print("✅ 健康检查通过")
            print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")

def test_api_info():
    """测试API信息"""
    print("\n=== 测试API信息 ===")

    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            result = response.json()
            print("✅ API信息获取成功")
            print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ API信息获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API信息获取异常: {e}")

if __name__ == "__main__":
    print("开始测试内容审查API...")
    print("请确保API服务器已启动 (python app.py)")
    print("=" * 60)

    # 运行测试
    test_api_info()
    test_health_check()
    test_text_moderation_api()

    print("\n测试完成!")
    print("如需测试图片上传功能，请使用 http://localhost:8080/docs 中的交互式文档")
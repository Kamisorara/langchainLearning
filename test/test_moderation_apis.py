"""
测试所有内容审查API端点
"""
import requests
import json

BASE_URL = "http://localhost:8080"

def test_api_info():
    """测试API信息"""
    print("=== 测试API信息 ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            result = response.json()
            print("[OK] API信息获取成功")
            endpoints = result.get('data', {}).get('endpoints', {})
            for name, endpoint in endpoints.items():
                print(f"  {name}: {endpoint}")
        else:
            print(f"[ERROR] API信息获取失败: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] API信息获取异常: {e}")

def test_health_check():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print("[OK] 健康检查通过")
            print(f"  状态: {result.get('data', {}).get('status')}")
        else:
            print(f"[ERROR] 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] 健康检查异常: {e}")

def test_text_moderation_api():
    """测试文本审查API"""
    print("\n=== 测试文本审查API ===")

    test_cases = [
        {"text_content": "今天天气很好", "description": "正常文本"},
        {"text_content": "这是一段包含暴力和血腥的内容", "description": "敏感文本"}
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
                print("[OK] 文本审查API调用成功")
                data = result.get('data', {})
                print(f"  整体安全: {data.get('overall_safe')}")
                print(f"  风险级别: {data.get('risk_level')}")
                print(f"  建议: {data.get('recommendations', [])[:2]}")
            else:
                print(f"[ERROR] 文本审查API调用失败: {response.status_code}")
                print(f"  错误: {response.text}")

        except Exception as e:
            print(f"[ERROR] 文本审查请求异常: {e}")

        print("-" * 50)

def test_image_moderation_api():
    """测试图片审查API"""
    print("\n=== 测试图片审查API ===")

    try:
        # 使用测试图片
        with open("../images/image1.jpg", "rb") as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            response = requests.post(f"{BASE_URL}/moderate-image", files=files)

            if response.status_code == 200:
                result = response.json()
                print("[OK] 图片审查API调用成功")
                data = result.get('data', {})
                print(f"  整体安全: {data.get('overall_safe')}")
                print(f"  风险级别: {data.get('risk_level')}")
                print(f"  建议: {data.get('recommendations', [])[:2]}")

                if data.get('image_moderation'):
                    img_mod = data['image_moderation']
                    print(f"  图片审查置信度: {img_mod.get('confidence', 0)}")
                    print(f"  描述: {img_mod.get('description', 'N/A')[:50]}...")
            else:
                print(f"[ERROR] 图片审查API调用失败: {response.status_code}")
                print(f"  错误: {response.text}")

    except FileNotFoundError:
        print("[SKIP] 测试图片不存在，跳过图片审查测试")
    except Exception as e:
        print(f"[ERROR] 图片审查请求异常: {e}")

def test_content_moderation_api():
    """测试综合内容审查API"""
    print("\n=== 测试综合内容审查API ===")

    # 测试1: 仅文本
    print("\n测试1: 仅文本内容")
    try:
        data = {"text_content": "请描述这张美丽的风景照片"}
        response = requests.post(
            f"{BASE_URL}/moderate-content",
            data=data
        )

        if response.status_code == 200:
            result = response.json()
            print("[OK] 综合审查(仅文本)成功")
            data = result.get('data', {})
            print(f"  整体安全: {data.get('overall_safe')}")
            print(f"  包含文本审查: {'text_moderation' in data}")
            print(f"  包含图片审查: {'image_moderation' in data}")
        else:
            print(f"[ERROR] 综合审查(仅文本)失败: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] 综合审查(仅文本)异常: {e}")

    # 测试2: 文本+图片
    print("\n测试2: 文本+图片内容")
    try:
        with open("../images/image1.jpg", "rb") as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            data = {"text_content": "请分析这张图片"}
            response = requests.post(
                f"{BASE_URL}/moderate-content",
                files=files,
                data=data
            )

            if response.status_code == 200:
                result = response.json()
                print("[OK] 综合审查(文本+图片)成功")
                data = result.get('data', {})
                print(f"  整体安全: {data.get('overall_safe')}")
                print(f"  风险级别: {data.get('risk_level')}")
                print(f"  包含文本审查: {'text_moderation' in data}")
                print(f"  包含图片审查: {'image_moderation' in data}")
                print(f"  建议: {data.get('recommendations', [])[:3]}")
            else:
                print(f"[ERROR] 综合审查(文本+图片)失败: {response.status_code}")
                print(f"  错误: {response.text}")

    except FileNotFoundError:
        print("[SKIP] 测试图片不存在，跳过综合审查图片测试")
    except Exception as e:
        print(f"[ERROR] 综合审查(文本+图片)异常: {e}")

if __name__ == "__main__":
    print("开始测试内容审查API端点...")
    print("请确保API服务器已启动 (python app.py)")
    print("=" * 60)

    # 运行所有测试
    test_api_info()
    test_health_check()
    test_text_moderation_api()
    test_image_moderation_api()
    test_content_moderation_api()

    print("\n" + "=" * 60)
    print("API测试完成!")
    print("\n可用的API端点:")
    print("- GET  / : API信息")
    print("- GET  /health : 健康检查")
    print("- POST /moderate-text : 文本内容审查")
    print("- POST /moderate-image : 图片内容审查")
    print("- POST /moderate-content : 综合内容审查(文本+图片)")
    print("- POST /upload-image : 图片上传处理")
    print("- POST /process-image-sync : 同步图片处理")
    print("- GET  /status/{task_id} : 查询任务状态")
    print("- GET  /results : 获取所有结果")
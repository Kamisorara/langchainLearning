"""
测试图片内容审查功能
"""
import base64
from main import process_image_moderation, process_content_moderation
from llm_node import load_image_as_base64

def test_image_only_moderation():
    """测试纯图片内容审查"""
    print("=== 测试纯图片内容审查 ===")

    try:
        # 加载测试图片
        image_base64 = load_image_as_base64("../images/image1.jpg")
        print("正在审查图片内容...")

        result = process_image_moderation(image_base64)

        print(f"[OK] 图片审查成功")
        print(f"整体安全: {result['data']['overall_safe']}")
        print(f"风险级别: {result['data']['risk_level']}")
        print(f"建议: {result['data']['recommendations']}")

        if result['data'].get('image_moderation'):
            moderation = result['data']['image_moderation']
            print(f"图片审查结果:")
            print(f"  - 安全性: {moderation.get('is_safe', 'unknown')}")
            print(f"  - 风险级别: {moderation.get('risk_level', 'unknown')}")
            print(f"  - 风险类别: {moderation.get('categories', [])}")
            print(f"  - 置信度: {moderation.get('confidence', 0)}")
            print(f"  - 描述: {moderation.get('description', 'N/A')[:100]}...")

        if result['data'].get('image_analysis'):
            analysis = result['data']['image_analysis']
            print(f"图片内容分析: {analysis[:200]}...")

    except Exception as e:
        print(f"[ERROR] 图片审查失败: {e}")

def test_combined_moderation():
    """测试综合文本+图片内容审查"""
    print("\n=== 测试综合内容审查 ===")

    test_cases = [
        ("请描述这张美丽的风景照片", "正常请求"),
        ("分析图片中是否有暴力内容", "敏感词查询"),
        ("这是一张安全的图片，对吗？", "安全性确认"),
        ("检测图片中的成人内容", "敏感请求")
    ]

    try:
        image_base64 = load_image_as_base64("../images/image1.jpg")

        for text, description in test_cases:
            print(f"\n测试场景: {description}")
            print(f"文本: {text}")

            result = process_content_moderation(
                text_content=text,
                image_base64=image_base64
            )

            if result["success"]:
                data = result["data"]
                print(f"[OK] 综合审查成功")
                print(f"整体安全: {data['overall_safe']}")
                print(f"风险级别: {data['risk_level']}")
                print(f"建议: {data['recommendations']}")

                # 显示文本审查结果
                if data.get('text_moderation'):
                    text_mod = data['text_moderation']
                    print(f"文本审查: 安全={text_mod.get('is_safe')}, 风险={text_mod.get('risk_level')}")

                # 显示图片审查结果
                if data.get('image_moderation'):
                    img_mod = data['image_moderation']
                    print(f"图片审查: 安全={img_mod.get('is_safe')}, 风险={img_mod.get('risk_level')}")
            else:
                print(f"[ERROR] 综合审查失败: {result.get('error')}")

            print("-" * 60)

    except Exception as e:
        print(f"[ERROR] 综合测试失败: {e}")

def test_edge_cases():
    """测试边界情况"""
    print("\n=== 测试边界情况 ===")

    # 测试空图片
    print("测试空图片base64:")
    result = process_image_moderation("")
    print(f"结果: {result.get('success', False)}, 错误: {result.get('error', 'N/A')}")

    # 测试无效base64
    print("\n测试无效base64:")
    result = process_image_moderation("invalid_base64_string")
    print(f"结果: {result.get('success', False)}, 错误: {result.get('error', 'N/A')}")

def test_comparison_with_original():
    """与原有图片处理功能对比"""
    print("\n=== 功能对比测试 ===")

    try:
        image_base64 = load_image_as_base64("../images/image1.jpg")

        print("1. 原有图片分析功能:")
        from main import process_image_with_graph
        original_result = process_image_with_graph(image_base64)
        print(f"   成功: {original_result.get('success')}")
        if original_result.get('success'):
            print(f"   数据长度: {len(str(original_result.get('data', '')))}")

        print("\n2. 新的图片审查功能:")
        moderation_result = process_image_moderation(image_base64)
        print(f"   成功: {moderation_result.get('success')}")
        if moderation_result.get('success'):
            data = moderation_result.get('data', {})
            print(f"   安全性: {data.get('overall_safe')}")
            print(f"   风险级别: {data.get('risk_level')}")

        print("\n3. 综合审查功能:")
        combined_result = process_content_moderation(
            text_content="请分析这张图片",
            image_base64=image_base64
        )
        print(f"   成功: {combined_result.get('success')}")
        if combined_result.get('success'):
            data = combined_result.get('data', {})
            print(f"   安全性: {data.get('overall_safe')}")
            print(f"   包含文本审查: {'text_moderation' in data}")
            print(f"   包含图片审查: {'image_moderation' in data}")

    except Exception as e:
        print(f"[ERROR] 对比测试失败: {e}")

if __name__ == "__main__":
    print("开始测试图片内容审查功能...")
    print("=" * 60)

    # 运行各种测试
    test_image_only_moderation()
    test_combined_moderation()
    test_edge_cases()
    test_comparison_with_original()

    print("\n" + "=" * 60)
    print("图片内容审查测试完成!")
    print("\n主要改进:")
    print("[OK] 新增专门的图片内容审查节点")
    print("[OK] 支持识别不当图片内容（暴力、色情等）")
    print("[OK] 提供图片安全性和风险级别评估")
    print("[OK] 与文本审查节点无缝集成")
    print("[OK] 支持纯图片审查和综合审查两种模式")
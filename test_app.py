#!/usr/bin/env python3
"""SuperTask - 智能任务管理系统 - 测试脚本"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from database import AssignmentDB
from ocr_service import OCRService
from llm_service import LLMService

def test_database():
    print("\n=== 测试SuperTask数据库 ===")
    db = AssignmentDB()
    db.add_assignment("SuperTask数学", "1. 解方程: x²-5x+6=0\n2. 计算面积", "数学老师")
    db.add_assignment("SuperTask英语", "1. 背诵课文\n2. 翻译练习", "英语老师")
    print(f"总任务数: {len(db.get_all())}")
    print(f"待完成: {len(db.get_pending())}")
    all_tasks = db.get_all()
    stats = {"total": len(all_tasks), "pending": len([t for t in all_tasks if not t["completed"]]), "completed": len([t for t in all_tasks if t["completed"]])}
    print(f"统计数据: {stats}")
    db.conn.close()
    return True

def test_ocr():
    print("\n=== 测试SuperTask OCR服务 ===")
    service = OCRService()
    print(f"OCR提供商: {service.current_provider}")
    result = service.recognize_text("non_existent.jpg")
    print(f"识别结果: {result['message']}")
    return True

def test_llm():
    print("\n=== 测试SuperTask大模型服务 ===")
    service = LLMService(provider="mock")
    print(f"大模型提供商: {service.provider}")
    result = service.generate_title("SuperTask数学\n1. 解方程\n2. 计算面积")
    print(f"生成标题: {result['data']['text']}")
    result = service.extract_tasks("SuperTask数学\n1. 解方程\n2. 计算面积")
    print(f"提取任务数: {len(result['data']['tasks'])}")
    return True

if __name__ == "__main__":
    print("SuperTask - 智能任务管理系统 - 测试")
    print("=" * 50)
    try:
        test_database()
        test_ocr()
        test_llm()
        print("\n✅ SuperTask所有测试通过！")
    except Exception as e:
        print(f"\n❌ SuperTask测试失败: {e}")
        import traceback
        traceback.print_exc()

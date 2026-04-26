"""Tests for SuperTask core services."""

import json

from supertask.core import AssignmentDB, LLMService, OCRService


def test_database_uses_explicit_temp_path_and_writes_backup(tmp_path):
    db = AssignmentDB(db_path=tmp_path / "assignments.db")

    try:
        first = db.add_assignment("SuperTask数学", "1. 解方程: x²-5x+6=0\n2. 计算面积", "数学老师")
        second = db.add_assignment("SuperTask英语", "1. 背诵课文\n2. 翻译练习", "英语老师")

        all_tasks = db.get_all()
        assert len(all_tasks) == 2
        assert [task["id"] for task in all_tasks] == [second["id"], first["id"]]
        assert len(db.get_pending()) == 2

        updated = db.toggle_complete(first["id"])
        assert updated["completed"] is True
        assert len(db.get_completed()) == 1

        backup_path = tmp_path / "assignments_backup.json"
        assert backup_path.exists()
        backup_payload = json.loads(backup_path.read_text(encoding="utf-8"))
        assert len(backup_payload) == 2
        assert any(task["completed"] for task in backup_payload)
    finally:
        db.close()


def test_ocr_mock_provider_returns_sample_text():
    service = OCRService()

    result = service.recognize_text("non_existent.jpg")

    assert service.current_provider == "mock"
    assert result["code"] == 0
    assert result["message"] == "模拟识别成功"
    assert result["data"]["text"]
    assert len(result["data"]["words"]) >= 2


def test_llm_mock_extracts_title_and_tasks():
    source_text = "数学作业\n1. 解方程\n2. 计算面积"
    service = LLMService(provider="mock")

    optimized = service.optimize_text(source_text)
    title = service.generate_title(source_text)
    tasks = service.extract_tasks(source_text)

    assert optimized["data"]["text"] == source_text
    assert title["data"]["text"] == "数学作业"
    assert [task["content"] for task in tasks["data"]["tasks"]] == ["1. 解方程", "2. 计算面积"]

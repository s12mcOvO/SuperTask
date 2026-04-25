# 智能作业白板识别系统

## 项目简介
基于Kivy框架的跨平台智能作业白板识别系统，包含教师端（拍照识别+大模型优化）和学生端（Todo List管理）双端功能。

## 功能特性
- 教师端拍照识别白板作业，OCR文字提取
- 云端大模型API优化整理识别结果  
- 一键发送作业给学生
- 学生端Todo List完成状态管理
- 实时统计作业完成率

## 快速开始
```bash
pip install -r requirements.txt
python main.py
```

## 技术架构
- UI框架: Kivy 2.3+
- 数据库: SQLite3 + JSON
- OCR: 百度OCR/Tesseract/模拟
- 大模型: OpenAI/文心一言/智谱AI/模拟

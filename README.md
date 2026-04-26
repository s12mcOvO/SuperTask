# SuperTask - 智能任务管理系统

## 项目简介

基于 Kivy 框架的跨平台智能任务管理系统（原：智能作业白板识别系统）。系统包含教师端（拍照识别+大模型优化）和学生端（Todo List管理）双端功能。

## 功能特性

- 📸 **智能识别**：白板拍照，自动识别文字内容
- 🤖 **大模型优化**：集成云端大模型API，优化识别结果
- 📤 **任务分发**：一键发送任务给学生
- ✅ **Todo管理**：学生端可管理任务完成状态
- 📊 **数据统计**：实时统计任务完成率

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py

# 运行测试
python -m pytest tests/ -v
```

## 项目结构

```
SuperTask/
├── supertask/                  # 主代码包
│   ├── __init__.py
│   ├── main.py                 # 应用主程序
│   ├── config.py               # 配置文件
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── database.py         # 本地数据库（SQLite + JSON）
│   │   ├── ocr_service.py      # OCR识别服务
│   │   ├── llm_service.py      # 大模型API服务
│   │   └── sync_service.py     # 数据同步服务
│   └── ui/                     # UI界面
│       ├── __init__.py
│       └── components.py       # UI组件（教师端/学生端）
├── tests/                      # 测试
│   ├── __init__.py
│   └── test_app.py
├── data/                       # 数据文件
│   └── assignments_backup.json
├── .github/workflows/
│   └── build.yml              # CI/CD跨平台构建
├── requirements.txt            # Python依赖
├── setup.py                    # 安装配置
└── README.md
```

## 技术架构

### 主要模块

- **UI框架**：Kivy 2.3+
- **数据库**：SQLite3 + JSON
- **OCR引擎**：百度OCR / 腾讯OCR / Tesseract / 模拟
- **大模型**：OpenAI GPT / 文心一言 / 智谱AI / 模拟
- **网络请求**：requests

## 使用说明

### 教师端 🍎

1. **切换至教师端标签页**
2. **拍照识别**：点击"📷 拍照识别白板"按钮
3. **查看结果**：识别结果会自动显示并优化
4. **发送任务**：任务会自动添加到学生端

### 学生端 🎓

1. **切换至学生端标签页**
2. **查看任务**：显示所有待完成任务
3. **标记完成**：点击复选框切换完成状态
4. **查看统计**：在"统计"标签页查看完成率

## API集成

### 支持的大模型服务

- **OpenAI GPT-4**：通用型大模型，识别准确率高
- **文心一言**：百度中文大模型，适合中文识别
- **智谱AI**：国产大模型，稳定性好

### OCR服务配置

```python
# 默认使用模拟模式（无需API密钥）
# 如需真实OCR，请配置以下服务：

# 百度OCR（推荐）
service = OCRService(provider="baidu")

# Tesseract本地OCR
service = OCRService(provider="tesseract")

# 自动选择可用服务
service = OCRService(provider="auto")
```

## 字体支持

应用内置中英文字体支持：
- **默认字体**：Noto Sans CJK（支持中文/日文/韩文）
- **次级字体**：Nunito Heavy（优化拉丁字符渲染）

## 许可证

MIT License

## 作者

SuperTask 开发团队

## 更新日志

### v1.0.0 (2026-04-26)

- ✅ 初始版本发布
- ✅ 教师端拍照识别功能
- ✅ 学生端Todo List功能
- ✅ 多端同步支持
- ✅ 统计功能
- ✅ 离线模式支持
- ✅ 项目结构优化（分离核心模块和UI组件）

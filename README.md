# SuperTask - 智能任务管理系统

## 项目简介

基于 Kivy 框架的跨平台任务管理原型。当前仓库用于验证教师端任务录入、学生端 Todo 管理和本地持久化流程。

当前实现状态：
- 教师端拍照识别流程已打通，但 OCR 结果来自模拟服务
- 大模型优化和任务同步接口已预留，当前仍为模拟实现
- 学生端 Todo、完成状态切换和统计功能可本地运行

## 功能特性

- 📸 **识别流程原型**：模拟白板拍照识别并生成任务内容
- 🤖 **大模型接口预留**：保留文本优化和任务提取接口，当前默认使用 mock
- 📤 **任务分发**：一键发送任务给学生
- ✅ **Todo管理**：学生端可管理任务完成状态
- 📊 **数据统计**：实时统计任务完成率

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py

# 或安装后使用命令行入口
supertask

# 运行测试
python -m pytest tests/ -v
```

应用运行时默认将数据写入 Kivy 的 `user_data_dir`。如果直接单独调用 `AssignmentDB()`，开发环境下会回退到仓库内的 `data/` 目录；也可以通过环境变量 `SUPERTASK_DATA_DIR` 强制指定数据目录。

## 项目结构

```
SuperTask/
├── main.py                     # 本地开发入口
├── supertask/                  # 主代码包
│   ├── __init__.py
│   ├── app.py                  # 应用主程序
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── database.py         # 本地数据库（SQLite + JSON）
│   │   ├── ocr_service.py      # OCR模拟服务
│   │   ├── llm_service.py      # 大模型模拟服务
│   │   └── sync_service.py     # 同步模拟服务
│   └── ui/                     # UI界面
│       ├── __init__.py
│       └── components.py       # UI组件（教师端/学生端）
├── tests/                      # 测试
│   ├── __init__.py
│   └── test_app.py
├── data/                       # 开发环境数据目录（运行时生成）
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
- **OCR引擎**：当前为模拟实现
- **大模型**：当前为模拟实现
- **网络请求**：requests

## 使用说明

### 教师端 🍎

1. **切换至教师端标签页**
2. **拍照识别**：点击"📷 拍照识别白板"按钮
3. **查看结果**：当前会从模拟 OCR 返回示例文本并生成标题
4. **发送任务**：任务会自动添加到学生端

### 学生端 🎓

1. **切换至学生端标签页**
2. **查看任务**：显示所有待完成任务
3. **标记完成**：点击复选框切换完成状态
4. **查看统计**：在"统计"标签页查看完成率

## 服务状态

- `OCRService` 当前固定返回内置示例文本，用于验证界面和任务流转。
- `LLMService` 当前执行轻量规则处理，不会调用外部模型 API。
- `SyncService` 当前返回模拟同步结果，不会访问真实服务端。

## 字体支持

应用内置中英文字体支持：
- **默认字体**：Noto Sans CJK（支持中文/日文/韩文）
- **次级字体**：Nunito Heavy（优化拉丁字符渲染）

## 许可证

MIT License

## 作者

SuperTask 开发团队

## 更新日志

### v1.0.0-alpha (2026-04-26)

- ✅ 原型版本发布
- ✅ 教师端拍照识别流程
- ✅ 学生端Todo List功能
- ✅ 本地数据库和 JSON 备份
- ✅ 统计功能
- ✅ OCR / LLM / 同步 mock 接口
- ✅ 项目结构优化（分离核心模块和UI组件）

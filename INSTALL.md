# SuperTask 安装与使用指南

## 本地运行

### 1. 激活虚拟环境
```bash
cd /home/s12mc/CodeSpace/Project/SuperTask
source venv/bin/activate
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行应用
```bash
export PYTHONPATH=.
python main.py
```

## 开发模式

### 运行测试
```bash
python -m pytest tests/ -v
```

### 安装为包
```bash
pip install -e .
supertask
```

## 项目结构
```
SuperTask/
├── main.py              # 本地开发入口
├── supertask/
│   ├── __init__.py
│   ├── app.py           # 应用主程序
│   ├── core/            # 核心模块
│   │   ├── database.py  # SQLite + JSON
│   │   ├── ocr_service.py
│   │   ├── llm_service.py
│   │   └── sync_service.py
│   └── ui/              # UI组件
│       └── components.py
├── tests/               # 单元测试
│   └── test_app.py
├── data/                # 开发数据
└── requirements.txt     # 依赖
```

## 测试

所有单元测试使用 pytest fixtures (tmp_path)，确保：
- ✅ 无全局状态污染
- ✅ 可并行运行
- ✅ 高重现性

运行测试：
```bash
python -m pytest tests/ -v
```

预期输出：
```
3 passed in 0.01s
```

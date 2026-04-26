class LLMService:
    def __init__(self, provider="mock"):
        self.provider = provider
    
    def optimize_text(self, text, prompt=None):
        return {"code": 0, "message": "模拟优化完成", "data": {"text": text, "raw": None}}
    
    def generate_title(self, text):
        lines = text.split('\\n')
        for line in lines:
            line = line.strip()
            if line and ('作业' in line or '练习' in line):
                return {"code": 0, "message": "成功", "data": {"text": line[:20], "raw": None}}
        return {"code": 0, "message": "成功", "data": {"text": "智能识别", "raw": None}}
    
    def extract_tasks(self, text):
        lines = text.split('\\n')
        tasks = []
        tid = 1
        for line in lines:
            line = line.strip()
            if line and any(k in line for k in ['1.', '2.', '3.', '①', '②']):
                tasks.append({"id": tid, "content": line, "type": "作业任务"})
                tid += 1
        return {"code": 0, "message": "成功", "data": {"text": text, "tasks": tasks, "raw": None}}

if __name__ == "__main__":
    llm = LLMService()
    print(llm.generate_title("数学作业\\n1. 解方程"))

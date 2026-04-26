class LLMService:
    def __init__(self, provider="mock"):
        self.provider = provider

    @staticmethod
    def _split_lines(text):
        return [line.strip() for line in text.replace("\\n", "\n").splitlines() if line.strip()]
    
    def optimize_text(self, text, prompt=None):
        normalized = text.replace("\\n", "\n")
        return {"code": 0, "message": "模拟优化完成", "data": {"text": normalized, "raw": None}}
    
    def generate_title(self, text):
        for line in self._split_lines(text):
            if line and ('作业' in line or '练习' in line):
                return {"code": 0, "message": "成功", "data": {"text": line[:20], "raw": None}}
        return {"code": 0, "message": "成功", "data": {"text": "智能识别", "raw": None}}
    
    def extract_tasks(self, text):
        tasks = []
        tid = 1
        normalized = text.replace("\\n", "\n")
        for line in self._split_lines(normalized):
            if any(k in line for k in ['1.', '2.', '3.', '4.', '①', '②', '③', '④']):
                tasks.append({"id": tid, "content": line, "type": "作业任务"})
                tid += 1
        return {"code": 0, "message": "成功", "data": {"text": normalized, "tasks": tasks, "raw": None}}

if __name__ == "__main__":
    llm = LLMService()
    print(llm.generate_title("数学作业\\n1. 解方程"))

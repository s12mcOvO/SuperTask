class OCRService:
    def __init__(self, provider="auto"):
        self.provider = provider
        self.current_provider = "mock"

    @staticmethod
    def _normalize_text(text):
        return text.replace("\\n", "\n")
    
    def recognize_text(self, image_path):
        import random
        samples = [
            "数学作业\n1. 解方程: x²-5x+6=0\n2. 计算三角形面积\n3. 证明勾股定理",
            "英语作业\n1. 背诵课文 Unit 3\n2. 翻译练习 p56-58",
            "物理作业\n1. 完成练习册P45-48\n2. 实验报告：摩擦力实验",
        ]
        text = self._normalize_text(random.choice(samples))
        return {"code": 0, "message": "模拟识别成功", "data": {"text": text, "words": text.splitlines()}}

if __name__ == "__main__":
    svc = OCRService()
    print(svc.recognize_text("test.jpg"))

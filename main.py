import json
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock

Window.clearcolor = (0.95, 0.95, 0.95, 1)
Window.size = (400, 600)

class AssignmentDB:
    def __init__(self, db_path="assignments.db"):
        self.db_path = db_path
        self.json_backup_path = "assignments_backup.json"
        self.conn = None
        self.cursor = None
        self._init_db()
    
    def _init_db(self):
        import sqlite3
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                sender TEXT DEFAULT '教师',
                date TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON assignments(date)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_completed ON assignments(completed)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON assignments(status)")
        self.conn.commit()
    
    def add_assignment(self, title, content, sender="教师", metadata=None):
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        metadata_json = json.dumps(metadata or {})
        self.cursor.execute("""
            INSERT INTO assignments (title, content, sender, date, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (title, content, sender, date, metadata_json))
        self.conn.commit()
        assignment_id = self.cursor.lastrowid
        self._backup_to_json()
        return {"id": assignment_id, "title": title, "content": content,
                "sender": sender, "date": date, "completed": False, "status": "pending", "metadata": metadata or {}}
    
    def toggle_complete(self, assignment_id):
        self.cursor.execute("SELECT completed FROM assignments WHERE id = ?", (assignment_id,))
        result = self.cursor.fetchone()
        if not result:
            return None
        new_status = not result[0]
        new_status_text = "completed" if new_status else "pending"
        self.cursor.execute("UPDATE assignments SET completed = ?, status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                          (new_status, new_status_text, assignment_id))
        self.conn.commit()
        self._backup_to_json()
        return self.get_assignment(assignment_id)
    
    def get_assignment(self, assignment_id):
        self.cursor.execute("SELECT id, title, content, sender, date, completed, status, metadata FROM assignments WHERE id = ?", (assignment_id,))
        result = self.cursor.fetchone()
        if result:
            metadata = json.loads(result[7]) if result[7] else {}
            return {"id": result[0], "title": result[1], "content": result[2],
                    "sender": result[3], "date": result[4], "completed": bool(result[5]),
                    "status": result[6], "metadata": metadata}
        return None
    
    def get_all(self, limit=None, offset=0):
        query = "SELECT id, title, content, sender, date, completed, status, metadata FROM assignments ORDER BY date DESC, id DESC"
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        assignments = []
        for row in results:
            metadata = json.loads(row[7]) if row[7] else {}
            assignments.append({"id": row[0], "title": row[1], "content": row[2],
                              "sender": row[3], "date": row[4], "completed": bool(row[5]),
                              "status": row[6], "metadata": metadata})
        return assignments
    
    def get_pending(self):
        self.cursor.execute("SELECT id, title, content, sender, date, completed, status, metadata FROM assignments WHERE completed = 0 ORDER BY date DESC, id DESC")
        results = self.cursor.fetchall()
        return self._parse_results(results)
    
    def get_completed(self):
        self.cursor.execute("SELECT id, title, content, sender, date, completed, status, metadata FROM assignments WHERE completed = 1 ORDER BY date DESC, id DESC")
        results = self.cursor.fetchall()
        return self._parse_results(results)
    
    def search(self, keyword):
        self.cursor.execute("SELECT id, title, content, sender, date, completed, status, metadata FROM assignments WHERE title LIKE ? OR content LIKE ? ORDER BY date DESC, id DESC",
                          (f"%{keyword}%", f"%{keyword}%"))
        results = self.cursor.fetchall()
        return self._parse_results(results)
    
    def _parse_results(self, results):
        assignments = []
        for row in results:
            metadata = json.loads(row[7]) if row[7] else {}
            assignments.append({"id": row[0], "title": row[1], "content": row[2],
                              "sender": row[3], "date": row[4], "completed": bool(row[5]),
                              "status": row[6], "metadata": metadata})
        return assignments
    
    def _backup_to_json(self):
        assignments = self.get_all()
        with open(self.json_backup_path, 'w', encoding='utf-8') as f:
            json.dump(assignments, f, ensure_ascii=False, indent=2)

class OCRService:
    def __init__(self, provider="auto"):
        self.provider = provider
        self.current_provider = "mock"
        print(f"[OCR] 使用模拟模式")
    
    def recognize_text(self, image_path):
        import random
        sample_texts = [
            "数学任务\\n1. 解方程: x² - 5x + 6 = 0\\n2. 计算三角形面积\\n3. 证明勾股定理",
            "英语任务\\n1. 背诵课文 Unit 3\\n2. 翻译练习 p56-58\\n3. 写一篇100字作文",
            "物理任务\\n1. 完成练习册P45-48\\n2. 实验报告：摩擦力实验\\n3. 预习牛顿定律"
        ]
        text = random.choice(sample_texts)
        return {"code": 0, "message": "模拟识别成功", "data": {"text": text, "words": text.split('\\n')}}

class LLMService:
    def __init__(self, provider="mock"):
        self.provider = provider
    
    def optimize_text(self, text, prompt=None):
        return {"code": 0, "message": "模拟优化完成", "data": {"text": text, "raw": None}}
    
    def generate_title(self, text):
        lines = text.split('\\n')
        for line in lines:
            line = line.strip()
            if line and ('任务' in line or '练习' in line or '习题' in line):
                return {"code": 0, "message": "成功", "data": {"text": line[:20], "raw": None}}
        return {"code": 0, "message": "成功", "data": {"text": "智能任务识别", "raw": None}}
    
    def extract_tasks(self, text):
        lines = text.split('\\n')
        tasks = []
        task_id = 1
        for line in lines:
            line = line.strip()
            if line and any(kw in line for kw in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '①', '②', '③']):
                tasks.append({"id": task_id, "content": line, "type": "任务任务"})
                task_id += 1
        if not tasks and lines:
            for line in lines:
                line = line.strip()
                if line:
                    tasks.append({"id": task_id, "content": line, "type": "任务任务"})
                    task_id += 1
        return {"code": 0, "message": "成功", "data": {"text": text, "tasks": tasks, "raw": None}}

class TeacherCamera(BoxLayout):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.callback = callback
        self.spacing = 10
        self.size_hint_y = None
        self.height = 200
        self.add_widget(Label(text="[教师端] 拍照识别白板", font_size=16, bold=True, size_hint_y=None, height=30))
        self.capture_btn = Button(text="📷 拍照识别白板", background_color=(0.2, 0.6, 0.8, 1),
                                 color=(1, 1, 1, 1), font_size=16, size_hint_y=None, height=50)
        self.capture_btn.bind(on_press=self.on_capture)
        self.add_widget(self.capture_btn)
        self.status_label = Label(text="准备就绪", size_hint_y=None, height=30, color=(0.5, 0.5, 0.5, 1))
        self.add_widget(self.status_label)
    
    def on_capture(self, instance):
        self.status_label.text = "正在识别..."
        self.status_label.color = (0.8, 0.6, 0.2, 1)
        Clock.schedule_once(self._process_capture, 1)
    
    def _process_capture(self, dt):
        ocr = OCRService()
        llm = LLMService()
        result = ocr.recognize_text("whiteboard.jpg")
        raw_text = result['data']['text']
        optimized = llm.optimize_text(raw_text)
        title = llm.generate_title(raw_text)
        self.status_label.text = "识别完成！"
        self.status_label.color = (0.2, 0.7, 0.2, 1)
        if self.callback:
            self.callback(title['data']['text'], optimized['data']['text'])

class StudentTodo(BoxLayout):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.orientation = 'vertical'
        self.spacing = 10
        self.add_widget(Label(text="[学生端] 任务Todo List", font_size=16, bold=True, size_hint_y=None, height=30))
        self.stats_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        self.pending_label = Label(text="待完成: 0", color=(0.8, 0.3, 0.3, 1))
        self.completed_label = Label(text="已完成: 0", color=(0.2, 0.7, 0.2, 1))
        self.stats_layout.add_widget(self.pending_label)
        self.stats_layout.add_widget(self.completed_label)
        self.add_widget(self.stats_layout)
        scroll = ScrollView(size_hint=(1, 1))
        self.todo_layout = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=5)
        self.todo_layout.bind(minimum_height=self.todo_layout.setter('height'))
        scroll.add_widget(self.todo_layout)
        self.add_widget(scroll)
        self.refresh_todos()
    
    def refresh_todos(self):
        self.todo_layout.clear_widgets()
        todos = self.db.get_all()
        pending_count = len(self.db.get_pending())
        completed_count = len(self.db.get_completed())
        self.pending_label.text = f"待完成: {pending_count}"
        self.completed_label.text = f"已完成: {completed_count}"
        if not todos:
            self.todo_layout.add_widget(Label(text="暂无任务", color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=40))
            return
        for todo in reversed(todos):
            self.add_todo_item(todo)
    
    def add_todo_item(self, todo):
        bg_color = (0.9, 0.9, 0.95, 1) if todo["completed"] else (1, 1, 1, 1)
        border_color = (0.2, 0.7, 0.2, 1) if todo["completed"] else (0.8, 0.8, 0.8, 1)
        item = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, spacing=10)
        check_btn = Button(text="✓" if todo["completed"] else "○", background_color=border_color,
                          color=(1, 1, 1, 1) if todo["completed"] else (0.5, 0.5, 0.5, 1),
                          font_size=20, bold=True, size_hint_x=None, width=40)
        check_btn.todo_id = todo["id"]
        check_btn.bind(on_press=self.on_toggle)
        content = BoxLayout(orientation='vertical', padding=(10, 5))
        title_label = Label(text=todo["title"], font_size=14, bold=not todo["completed"],
                          halign='left', text_size=(200, None), size_hint_y=None, height=25)
        content.add_widget(title_label)
        date_label = Label(text=f"{todo['date']} | {todo['sender']}", font_size=11,
                         color=(0.5, 0.5, 0.5, 1), halign='left', size_hint_y=None, height=15)
        content.add_widget(date_label)
        content_label = Label(text=todo["content"][:50] + ("..." if len(todo["content"]) > 50 else ""),
                            font_size=12, color=(0.3, 0.3, 0.3, 1), halign='left',
                            text_size=(200, None), size_hint_y=None, height=35)
        content.add_widget(content_label)
        item.add_widget(check_btn)
        item.add_widget(content)
        self.todo_layout.add_widget(item)
    
    def on_toggle(self, instance):
        self.db.toggle_complete(instance.todo_id)
        self.refresh_todos()

class SuperTaskApp(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = AssignmentDB()
        self.do_default_tab = False
        self.tab_pos = 'top_left'
        teacher_tab = TabbedPanelHeader(text='教师端')
        teacher_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        teacher_content.add_widget(Label(text="SuperTask - 智能任务管理系统", font_size=20, bold=True, size_hint_y=None, height=40))
        teacher_content.add_widget(TeacherCamera(self.add_assignment))
        teacher_content.add_widget(Label(text="已发送任务", font_size=14, bold=True, size_hint_y=None, height=25))
        self.teacher_scroll = ScrollView(size_hint=(1, 1))
        self.teacher_layout = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=5)
        self.teacher_layout.bind(minimum_height=self.teacher_layout.setter('height'))
        self.teacher_scroll.add_widget(self.teacher_layout)
        teacher_content.add_widget(self.teacher_scroll)
        teacher_tab.content = teacher_content
        self.add_widget(teacher_tab)
        student_tab = TabbedPanelHeader(text='学生端')
        student_content = BoxLayout(orientation='vertical', padding=10)
        student_content.add_widget(StudentTodo(self.db))
        student_tab.content = student_content
        self.add_widget(student_tab)
        stats_tab = TabbedPanelHeader(text='统计')
        stats_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.stats_label = Label(text="", font_size=16, halign='center', valign='middle')
        self.stats_label.bind(size=self.stats_label.setter('text_size'))
        stats_content.add_widget(self.stats_label)
        stats_tab.content = stats_content
        self.add_widget(stats_tab)
        Clock.schedule_once(lambda dt: self.refresh_teacher_list(), 0.5)
    
    def add_assignment(self, title, content):
        assignment = self.db.add_assignment(title, content, sender="教师")
        print(f"[系统] 任务已发送: {title}")
        self.refresh_teacher_list()
        popup = Popup(title='识别成功',
                     content=Label(text=f'任务已识别并发送给学生:\n\n{content[:100]}...'),
                     size_hint=(0.8, 0.6))
        popup.open()
    
    def refresh_teacher_list(self):
        self.teacher_layout.clear_widgets()
        assignments = self.db.get_all()
        pending = len(self.db.get_pending())
        completed = len(self.db.get_completed())
        self.stats_label.text = f"总任务数: {len(assignments)}\\n待完成: {pending} | 已完成: {completed}\\n完成率: {completed/max(len(assignments),1)*100:.0f}%"
        if not assignments:
            self.teacher_layout.add_widget(Label(text="暂无已发送任务", size_hint_y=None, height=40))
            return
        for a in reversed(assignments):
            item = BoxLayout(orientation='vertical', size_hint_y=None, height=60, spacing=5)
            status_icon = "✓" if a["completed"] else "●"
            status_color = (0.2, 0.7, 0.2, 1) if a["completed"] else (0.8, 0.5, 0.2, 1)
            item.add_widget(Label(text=f"{status_icon} {a['title']}", font_size=13, bold=True,
                                halign='left', color=status_color, size_hint_y=None, height=18))
            item.add_widget(Label(text=f"{a['date']} | {a['content'][:40]}...", font_size=11,
                                color=(0.5, 0.5, 0.5, 1), halign='left', size_hint_y=None, height=15))
            self.teacher_layout.add_widget(item)

class SuperTaskAppMain(App):
    def build(self):
        self.title = "SuperTask - 智能任务管理系统"
        return SuperTaskApp()

if __name__ == "__main__":
    SuperTaskAppMain().run()

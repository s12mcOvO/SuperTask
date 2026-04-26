"""UI Components for SuperTask"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock

# Import services from core module
from ..core.ocr_service import OCRService
from ..core.llm_service import LLMService


Window.clearcolor = (0.95, 0.95, 0.95, 1)
Window.size = (400, 600)

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
        try:
            # 重用服务实例
            if not hasattr(self, '_ocr'):
                self._ocr = OCRService()
                self._llm = LLMService()
            
            result = self._ocr.recognize_text("whiteboard.jpg")
            if result.get('code') != 0:
                self.status_label.text = f"识别失败: {result.get('message', '未知错误')}"
                self.status_label.color = (0.8, 0.2, 0.2, 1)
                return
                
            raw_text = result['data']['text']
            optimized = self._llm.optimize_text(raw_text)
            title = self._llm.generate_title(raw_text)
            
            self.status_label.text = "识别完成！"
            self.status_label.color = (0.2, 0.7, 0.2, 1)
            
            if self.callback:
                self.callback(title['data']['text'], optimized['data']['text'])
        except Exception as e:
            self.status_label.text = f"错误: {str(e)[:50]}"
            self.status_label.color = (0.8, 0.2, 0.2, 1)
            print(f"[错误] 拍照识别失败: {e}")


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
        self.todo_layout.bind(minimum_height=lambda obj, val: setattr(self.todo_layout, 'height', self.todo_layout.minimum_height))
        scroll.add_widget(self.todo_layout)
        self.add_widget(scroll)
        self.refresh_todos()
    
    def refresh_todos(self):
        todos = self.db.get_all()
        # 一次性计算统计，避免多次查询
        pending_count = len([t for t in todos if not t["completed"]])
        completed_count = len([t for t in todos if t["completed"]])
        self.pending_label.text = f"待完成: {pending_count}"
        self.completed_label.text = f"已完成: {completed_count}"
        
        # 清空并重建
        self.todo_layout.clear_widgets()
        if not todos:
            self.todo_layout.add_widget(Label(text="暂无任务", color=(0.5, 0.5, 0.5, 1), 
                                                         size_hint_y=None, height=40))
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


"""SuperTask - 智能任务管理系统主程序"""

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
from kivy.core.text import LabelBase
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock

# Register fonts with Chinese support
# Primary: Noto Sans CJK for Chinese characters, Nunito Heavy for Latin
try:
    LabelBase.register(name='default', fn_regular='/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc')
except:
    try:
        import glob
        cjk_fonts = (glob.glob('/usr/share/fonts/**/Noto*CJK*.ttc', recursive=True) + 
                     glob.glob('/usr/share/fonts/**/Noto*Sans*.ttc', recursive=True) + 
                     glob.glob('/usr/share/fonts/truetype/wqy/*.ttc', recursive=True))
        if cjk_fonts:
            LabelBase.register(name='default', fn_regular=cjk_fonts[0])
    except:
        try:
            LabelBase.register(name='default', fn_regular='/usr/share/fonts/ttf-nunito/NunitoHeavy-Regular.ttf')
        except:
            pass

try:
    LabelBase.register(name='nunito', 
        fn_regular='/usr/share/fonts/ttf-nunito/Nunito-Regular.ttf', 
        fn_bold='/usr/share/fonts/ttf-nunito/Nunito-Bold.ttf',
        fn_italic='/usr/share/fonts/ttf-nunito/Nunito-Italic.ttf', 
        fn_bolditalic='/usr/share/fonts/ttf-nunito/Nunito-BoldItalic.ttf')
except:
    pass

Window.clearcolor = (0.95, 0.95, 0.95, 1)
Window.size = (400, 600)

# Import core modules
from supertask.core import AssignmentDB, OCRService, LLMService
from supertask.ui.components import TeacherCamera, StudentTodo

class SuperTaskApp(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = AssignmentDB()  # Uses data/assignments.db
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

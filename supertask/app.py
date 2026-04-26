"""Application entrypoint for SuperTask."""

from pathlib import Path
import glob

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelHeader

from supertask.core import AssignmentDB
from supertask.ui.components import TeacherCamera, StudentTodo


Window.clearcolor = (0.95, 0.95, 0.95, 1)
Window.size = (400, 600)


def _register_fonts():
    """Register a font family with reasonable Chinese fallback support."""

    try:
        LabelBase.register(
            name="default",
            fn_regular="/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        )
    except Exception:
        try:
            cjk_fonts = (
                glob.glob("/usr/share/fonts/**/Noto*CJK*.ttc", recursive=True)
                + glob.glob("/usr/share/fonts/**/Noto*Sans*.ttc", recursive=True)
                + glob.glob("/usr/share/fonts/truetype/wqy/*.ttc", recursive=True)
            )
            if cjk_fonts:
                LabelBase.register(name="default", fn_regular=cjk_fonts[0])
            else:
                LabelBase.register(
                    name="default",
                    fn_regular="/usr/share/fonts/ttf-nunito/NunitoHeavy-Regular.ttf",
                )
        except Exception:
            pass

    try:
        LabelBase.register(
            name="nunito",
            fn_regular="/usr/share/fonts/ttf-nunito/Nunito-Regular.ttf",
            fn_bold="/usr/share/fonts/ttf-nunito/Nunito-Bold.ttf",
            fn_italic="/usr/share/fonts/ttf-nunito/Nunito-Italic.ttf",
            fn_bolditalic="/usr/share/fonts/ttf-nunito/Nunito-BoldItalic.ttf",
        )
    except Exception:
        pass


class SuperTaskApp(TabbedPanel):
    def __init__(self, db_path=None, **kwargs):
        super().__init__(**kwargs)
        self.db = None
        self.student_todo = None
        self.do_default_tab = False
        self.tab_pos = "top_left"

        try:
            self.db = AssignmentDB(db_path=db_path)
            print(f"[初始化] 数据库加载成功: {self.db.db_path}")
        except Exception as exc:
            print(f"[错误] 数据库初始化失败: {exc}")

        teacher_tab = TabbedPanelHeader(text="教师端")
        teacher_content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        teacher_content.add_widget(
            Label(
                text="SuperTask - 智能任务管理系统",
                font_size=20,
                bold=True,
                size_hint_y=None,
                height=40,
            )
        )
        teacher_content.add_widget(TeacherCamera(self.add_assignment))
        teacher_content.add_widget(
            Label(text="已发送任务", font_size=14, bold=True, size_hint_y=None, height=25)
        )
        self.teacher_scroll = ScrollView(size_hint=(1, 1))
        self.teacher_layout = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=5)
        self.teacher_layout.bind(
            minimum_height=lambda *_: setattr(
                self.teacher_layout, "height", self.teacher_layout.minimum_height
            )
        )
        self.teacher_scroll.add_widget(self.teacher_layout)
        teacher_content.add_widget(self.teacher_scroll)
        teacher_tab.content = teacher_content
        self.add_widget(teacher_tab)

        student_tab = TabbedPanelHeader(text="学生端")
        student_content = BoxLayout(orientation="vertical", padding=10)
        self.student_todo = StudentTodo(self.db, on_change=self.refresh_teacher_list)
        student_content.add_widget(self.student_todo)
        student_tab.content = student_content
        self.add_widget(student_tab)

        stats_tab = TabbedPanelHeader(text="统计")
        stats_content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.stats_label = Label(text="", font_size=16, halign="center", valign="middle")
        self.stats_label.bind(
            size=lambda *_: setattr(self.stats_label, "text_size", (self.stats_label.width, None))
        )
        stats_content.add_widget(self.stats_label)
        stats_tab.content = stats_content
        self.add_widget(stats_tab)

        Clock.schedule_once(lambda dt: self.refresh_teacher_list(), 0)

    def add_assignment(self, title, content):
        if not self.db:
            Popup(
                title="数据库不可用",
                content=Label(text="任务未保存，请先检查数据库初始化日志。"),
                size_hint=(0.8, 0.4),
            ).open()
            return

        self.db.add_assignment(title, content, sender="教师")
        print(f"[系统] 任务已发送: {title}")

        if self.student_todo:
            self.student_todo.refresh_todos()
        self.refresh_teacher_list()

        preview = content if len(content) <= 100 else f"{content[:100]}..."
        Popup(
            title="识别成功",
            content=Label(text=f"任务已识别并发送给学生:\n\n{preview}"),
            size_hint=(0.8, 0.6),
        ).open()

    def refresh_teacher_list(self):
        assignments = []
        self.teacher_layout.clear_widgets()

        if not self.db:
            self.stats_label.text = "数据库不可用"
            self.teacher_layout.add_widget(
                Label(text="数据库初始化失败，无法加载任务", size_hint_y=None, height=40)
            )
            return

        try:
            assignments = self.db.get_all()
            pending = len([assignment for assignment in assignments if not assignment["completed"]])
            completed = len([assignment for assignment in assignments if assignment["completed"]])
            total = len(assignments)
            rate = (completed / total * 100) if total else 0
            self.stats_label.text = (
                f"总任务数: {total}\n待完成: {pending} | 已完成: {completed}\n完成率: {rate:.0f}%"
            )
        except Exception as exc:
            self.stats_label.text = f"统计加载失败: {str(exc)[:50]}"
            self.teacher_layout.add_widget(
                Label(
                    text=f"加载失败: {str(exc)[:30]}...",
                    color=(0.8, 0.2, 0.2, 1),
                    size_hint_y=None,
                    height=40,
                )
            )
            return

        if not assignments:
            self.teacher_layout.add_widget(Label(text="暂无已发送任务", size_hint_y=None, height=40))
            return

        for assignment in assignments:
            item = BoxLayout(orientation="vertical", size_hint_y=None, height=60, spacing=5)
            status_icon = "✓" if assignment["completed"] else "●"
            status_color = (
                (0.2, 0.7, 0.2, 1) if assignment["completed"] else (0.8, 0.5, 0.2, 1)
            )
            item.add_widget(
                Label(
                    text=f"{status_icon} {assignment['title']}",
                    font_size=13,
                    bold=True,
                    halign="left",
                    color=status_color,
                    size_hint_y=None,
                    height=18,
                )
            )
            item.add_widget(
                Label(
                    text=f"{assignment['date']} | {assignment['content'][:40]}...",
                    font_size=11,
                    color=(0.5, 0.5, 0.5, 1),
                    halign="left",
                    size_hint_y=None,
                    height=15,
                )
            )
            self.teacher_layout.add_widget(item)


class SuperTaskAppMain(App):
    def build(self):
        self.title = "SuperTask - 智能任务管理系统"
        data_dir = Path(self.user_data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        return SuperTaskApp(db_path=data_dir / "assignments.db")


def run_app():
    _register_fonts()
    SuperTaskAppMain().run()


if __name__ == "__main__":
    run_app()

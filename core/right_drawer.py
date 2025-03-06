from kivymd.uix.label import MDLabel  # Use MDLabel from KivyMD
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivy.metrics import dp
from core import task_manager
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from core.task_manager import TaskManager, Task 
from core.subject import Subject  
from kivy.properties import ObjectProperty
from kivy.core.text import LabelBase
from kivy.uix.button import Button


LabelBase.register(name="TimesNewRoman", fn_regular="font/times.ttf")

class RightDrawer(MDNavigationDrawer):
    task_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anchor = "right"
        self.md_bg_color = (1.0, 0.925, 0.611, 1)

        # The TaskManager instance that actually stores tasks
        #self.task_manager = task_manager

        layout = MDBoxLayout(
            orientation="vertical",
            padding="10dp",
            spacing="10dp"
        )

        # Use MDLabel instead of Label so that font_style is valid:
        quote_label = MDLabel(
            text="[i]'Do it for your future self'[/i]",
            markup=True,        
            font_style="H4",    
            font_name="TimesNewRoman",
            halign="center",
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(quote_label)

        self.task_input = TextInput(
            hint_text="Enter new task",
            size_hint_y=None,
            height=dp(40),
        )
        layout.add_widget(self.task_input)

        # Button to add tasks
        add_task_btn = Button(
            text="Add Task",
            size_hint_y=None,
            height=dp(40)
        )
        add_task_btn.bind(on_release=self.add_task)
        layout.add_widget(add_task_btn)
        
        # Scrollable area to display tasks
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.tasks_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None
        )
        self.tasks_layout.bind(minimum_height=self.tasks_layout.setter('height'))
        self.scroll_view.add_widget(self.tasks_layout)
        layout.add_widget(self.scroll_view)

        self.add_widget(layout)

        # Build an optional "toggle button" for opening/closing the drawer
        self.toggle_button = Button(
            size_hint=(None, None),
            size=(40, 40),
            background_color=(0, 0, 0, 0)  # transparent
        )
        self.toggle_button.bind(on_release=self.toggle_drawer)
        self.add_widget(self.toggle_button)

        # Example triangle on the toggle button
        with self.toggle_button.canvas.before:
            from kivy.graphics import Color, Triangle
            Color(1.0, 0.925, 0.611, 1)  # Yellow triangle
            self.triangle = Triangle(points=[0, 0, 40, 20, 0, 40])

        # Bind so the triangle moves with the drawer
        self.bind(pos=self.update_triangle)

        # Finally, load existing tasks from the TaskManager
        self.refresh_task_list()

    def add_task(self, *args):
        """
        Create a new Task and add it to the TaskManager.
        Then refresh the UI to show the new task.
        """
        title = self.task_input.text.strip()
        if title:
            # If you have a Task class:
            self.task_manager.add_task(title, priority=1)
            self.task_input.text = ""
            self.refresh_task_list()

    def refresh_task_list(self):
        """
        Clears the tasks_layout and rebuilds it with the latest tasks.
        """
        self.tasks_layout.clear_widgets()

        all_tasks = self.task_manager.get_all_tasks()
        # For each task in TaskManager, create a row
        for i, task in enumerate(all_tasks):
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))

             # Show task name & status
            label_text = f"{task.title} - {'Done' if task.completed else 'Pending'}"
            task_label = MDLabel(
                text=label_text,
                halign="left",
                size_hint_x=0.8
            )
            row.add_widget(task_label)

            # Button to complete the task
            complete_btn = Button(
                text="Complete",
                size_hint_x=0.2,
                disabled=task.completed
            )
            complete_btn.bind(on_release=lambda btn, t=task: self.complete_task(t))
            row.add_widget(complete_btn)

            self.tasks_layout.add_widget(row)

    def complete_task(self, task):
        """
        Mark the task as completed via TaskManager, then refresh.
        """
        self.task_manager.complete_task(task)
        self.refresh_task_list()

    def toggle_drawer(self, *args):
        self.set_state("toggle")
        self.update_triangle()

    def update_triangle(self, *args):
        if self.state == "open":
            self.toggle_button.pos = (self.x - 40, self.center_y - 20)
            self.triangle.points = [40, 0, 0, 20, 40, 40]  # Right-facing
        else:
            self.toggle_button.pos = (self.x + self.width - 10, self.center_y - 20)
            self.triangle.points = [0, 0, 40, 20, 0, 40]  # Left-facing
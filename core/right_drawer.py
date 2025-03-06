from kivymd.uix.label import MDLabel
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivy.metrics import dp
from core.task_manager import TaskManager, Task
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from core.subject import Subject  
from kivy.properties import ObjectProperty
from kivy.core.text import LabelBase
from kivy.uix.button import Button
from kivymd.uix.dialog import MDDialog
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner

LabelBase.register(name="Munro", fn_regular="font/Munro.ttf")

class RightDrawer(MDNavigationDrawer):
    task_manager = ObjectProperty(None)

    def __init__(self, task_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.anchor = "right"
        self.md_bg_color = (1.0, 0.925, 0.611, 1)

        # Store the TaskManager instance
        self.task_manager = task_manager

        # Only proceed with task-related setup if we have a task manager
        if self.task_manager is None:
            print("Warning: RightDrawer initialized without a TaskManager")
            
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
            font_name="Munro",
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

        # Create input row for task creation
        input_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        
        # Priority dropdown spinner
        self.priority_spinner = Spinner(
            text='Medium',
            values=('Low', 'Medium', 'High'),
            size_hint_x=0.3,
            size_hint_y=None,
            height=dp(40)
        )
        input_row.add_widget(self.priority_spinner)
        
        # Button to add tasks
        add_task_btn = Button(
            text="Add Task",
            size_hint_x=0.7,
            height=dp(40)
        )
        add_task_btn.bind(on_release=self.add_task)
        input_row.add_widget(add_task_btn)
        
        layout.add_widget(input_row)
        
        # Buttons row for clearing tasks
        buttons_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        
        # Button to clear all tasks
        clear_tasks_btn = Button(
            text="Clear All",
            size_hint_x=1.0,
            height=dp(40),
            background_color=(0.8, 0.2, 0.2, 1)  # Red background
        )
        clear_tasks_btn.bind(on_release=self.confirm_clear_tasks)
        buttons_row.add_widget(clear_tasks_btn)
        
        layout.add_widget(buttons_row)
        
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

        # Finally, load existing tasks from the TaskManager, if available
        if self.task_manager is not None:
            self.refresh_task_list()

    def add_task(self, *args):
        """
        Create a new Task and add it to the TaskManager with priority.
        Then refresh the UI to show the new task.
        """
        if self.task_manager is None:
            print("Cannot add task: No TaskManager available")
            return
            
        title = self.task_input.text.strip()
        if title:
            # Get priority from spinner
            priority_text = self.priority_spinner.text
            
            # Convert text priority to Task priority constant
            if priority_text == "Low":
                priority = Task.PRIORITY_LOW
            elif priority_text == "High":
                priority = Task.PRIORITY_HIGH
            else:
                priority = Task.PRIORITY_MEDIUM
                
            # Add task with priority
            self.task_manager.add_task(title, priority)
            self.task_input.text = ""
            self.refresh_task_list()

    def confirm_clear_tasks(self, *args):
        """Show confirmation dialog before clearing all tasks"""
        if self.task_manager is None or not self.task_manager.tasks:
            return
            
        dialog = MDDialog(
            title="Clear All Tasks?",
            text="Are you sure you want to delete all tasks? This cannot be undone.",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    font_name="Munro",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="CLEAR ALL",
                    font_name="Munro",
                    text_color=(0.8, 0.2, 0.2, 1),  # Red text for warning
                    on_release=lambda x: self.clear_all_tasks(dialog)
                )
            ]
        )
        dialog.open()
        
    def clear_all_tasks(self, dialog):
        """Clear all tasks and dismiss dialog"""
        dialog.dismiss()
        if self.task_manager:
            self.task_manager.reset_all_tasks()
            self.refresh_task_list()

    def refresh_task_list(self):
        """
        Clears the tasks_layout and rebuilds it with the latest tasks.
        Tasks are displayed in order of priority (high to low).
        """
        if self.task_manager is None:
            print("Cannot refresh tasks: No TaskManager available")
            return
            
        self.tasks_layout.clear_widgets()

        all_tasks = self.task_manager.get_all_tasks()
        
        # Sort tasks by priority (high to low)
        # Don't use reverse=True because __lt__ already does reverse comparison
        all_tasks.sort()  # Uses Task.__lt__ for sorting
        
        # For each task in TaskManager, create a row
        for task in all_tasks:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))

            # Show task name, priority & status
            priority_label = task.get_priority_label()
            label_text = f"{task.title} [{priority_label}] - {'Done' if task.completed else 'Pending'}"
            task_label = MDLabel(
                text=label_text,
                halign="left",
                size_hint_x=0.6
            )
            row.add_widget(task_label)

            # Buttons container
            buttons_box = BoxLayout(
                orientation='horizontal',
                size_hint_x=0.4,
                spacing=dp(5)
            )
            
            # Button to complete the task
            complete_btn = Button(
                text="Complete",
                size_hint_x=0.6,
                disabled=task.completed
            )
            complete_btn.bind(on_release=lambda btn, t=task: self.complete_task(t))
            buttons_box.add_widget(complete_btn)
            
            # Button to delete the task
            delete_btn = Button(
                text="Delete",
                size_hint_x=0.4,
                background_color=(0.8, 0.2, 0.2, 1)  # Red background
            )
            delete_btn.bind(on_release=lambda btn, t=task: self.delete_task(t))
            buttons_box.add_widget(delete_btn)
            
            row.add_widget(buttons_box)
            self.tasks_layout.add_widget(row)
            
    def complete_task(self, task):
        """
        Mark the task as completed via TaskManager, then refresh.
        """
        if self.task_manager is None:
            return
            
        self.task_manager.complete_task(task)
        self.refresh_task_list()
        
    def delete_task(self, task):
        """
        Delete the task via TaskManager, then refresh.
        """
        if self.task_manager is None:
            return
            
        self.task_manager.delete_task(task)
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
import heapq
from kivy.animation import Animation
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout

from core.subject import Subject
from core.task import Task

class TaskManager(Subject, MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        # Must be a BoxLayout to hold the task items
        self.orientation = "vertical"
        self.spacing = 10

        self.tasks = []

    def add_task(self, title, priority=1):
        """
        Insert task into the list - priority is kept for backward compatibility
        but isn't actually used for sorting anymore
        """
        task = Task(title, priority)
        self.tasks.append(task)  # Just append instead of using heapq
        self.notify("TASK_ADDED", task)
        self.update_display()

    def complete_task(self, task):
        """Mark a Task as completed"""
        if task in self.tasks:
            task.complete()
            self.notify("TASK_COMPLETED", task)
            self.update_display()

    def delete_task(self, task):
        """Remove a task from the list entirely"""
        if task in self.tasks:
            self.tasks.remove(task)
            self.notify("TASK_REMOVED", task)
            self.update_display()

    def reset_all_tasks(self):
        """Clear all tasks"""
        self.tasks = []
        self.notify("TASKS_RESET", None)
        self.update_display()

    def update_display(self):
        """
        Clear existing widgets, rebuild the UI with tasks in order of addition
        """
        # Clear the layout
        self.clear_widgets()

        # Display tasks in order (no priority sorting)
        for task in self.tasks:
            # Create a row for each task
            row_item = self._build_task_row(task)
            self.add_widget(row_item)

    def _build_task_row(self, task):
        """
        Build a UI row for the given task with complete and delete buttons
        """
        row = OneLineAvatarIconListItem(
            text=f"{task.title}{' [DONE]' if task.completed else ''}"
        )
        
        # Create an action buttons container
        actions_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            width=80,
            padding=(0, 0, 10, 0)
        )
        
        # Complete button
        complete_btn = MDIconButton(
            icon="check",
            on_release=lambda btn: self._on_complete_task(row, task)
        )
        # If it's already completed, disable the button
        complete_btn.disabled = task.completed
        
        # Delete button
        delete_btn = MDIconButton(
            icon="delete",
            on_release=lambda btn: self._on_delete_task(row, task)
        )
        
        actions_box.add_widget(complete_btn)
        actions_box.add_widget(delete_btn)
        row.add_widget(actions_box)
        
        return row
    
    def _on_complete_task(self, row_item, task):
        """Animate completion"""
        # Animate fade-out
        anim = Animation(opacity=0.5, duration=0.3)
        anim.bind(on_complete=lambda *args: self.complete_task(task))
        anim.start(row_item)

    def _on_delete_task(self, row_item, task):
        """Animate deletion"""
        # Animate fade-out
        anim = Animation(opacity=0, duration=0.3)
        anim.bind(on_complete=lambda *args: self.delete_task(task))
        anim.start(row_item)

    def get_all_tasks(self):
        """Return the task list"""
        return self.tasks
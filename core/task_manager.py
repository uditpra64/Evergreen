import heapq
from kivy.animation import Animation
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout

from core.subject import Subject
from core.task import Task

"""
    Demonstrates:
    - Inheritance from Subject for the Observer pattern
    - Priority queue (heapq) for tasks
    - Integrated UI approach with MDBoxLayout
    - Animations for removing tasks
    - Automatic refresh of the display in sorted order

"""

"""
    A widget that manages tasks using a min-heap (heapq) for priorities,
    and displays them in sorted order.

    Inherits from Subject to allow other components to observe changes:
      - e.g. self.notify("TASK_ADDED", new_task) or
             self.notify("TASK_COMPLETED", completed_task)
"""

class TaskManager(Subject, MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        # Must be a BoxLayout to hold the task items
        self.orientation = "vertical"
        self.spacing = 10

        self.tasks = []

    def add_task(self, title, priority):
        """Insert task into the priority queue.
        Create a new Task, push it into the heap, and refresh the display.
        Notify observers that a task was added if you want.
        """
        task = Task(title, priority)
        heapq.heappush(self.tasks, task)
        self.notify("TASK_ADDED", task)
        self.update_display()

    def complete_task(self, task):
        """
        Mark a Task as completed, and re-heapify if needed.
        Then refresh the display and optionally notify observers.
        """
        task.complete()
        # Because the priority or 'completed' might change ordering,
        # we can remove from heap and push again or just leave it
        # if 'completed' doesn't affect the __lt__ logic, it's fine.

        # If you want to remove completed tasks from the heap:
        self.tasks.remove(task)  # O(n) removal
        heapq.heapify(self.tasks)

        self.notify("TASK_COMPLETED", task)
        self.update_display()

    def remove_task_completely(self, task):
        """
        Remove the task from the heap entirely (not just mark completed).
        Then refresh display.
        """
        if task in self.tasks:
            self.tasks.remove(task)
            heapq.heapify(self.tasks)
            self.notify("TASK_REMOVED", task)
            self.update_display()

    def update_display(self):
        """
        Clear existing widgets, rebuild the UI in sorted order of tasks.
        This method is called whenever tasks change.
        """
        # Clear the layout
        self.clear_widgets()

        # Convert the heap into a sorted list
        sorted_tasks = sorted(self.tasks)

        for task in sorted_tasks:
            # Create a row for each task
            row_item = self._build_task_row(task)
            self.add_widget(row_item)

    def _build_task_row(self, task):
        """
        Build a UI row for the given task. Includes a label and a "Complete" button.
        """
        row = OneLineAvatarIconListItem(
            text=f"{task.title} (Priority: {task.priority}){' [DONE]' if task.completed else ''}"
        )
        # A small icon button to remove or complete
        complete_btn = MDIconButton(
            icon="check",
            on_release=lambda btn: self._on_complete_task(row, task)
        )
        # If it's already completed, disable the button
        complete_btn.disabled = task.completed

        row.add_widget(complete_btn)
        return row
    
    def _on_complete_task(self, row_item, task):
        """
        Animate removal or mark completed. You can choose either approach:
         - Mark as completed
         - Animate and remove from UI
        """
        # Animate fade-out
        anim = Animation(opacity=0, duration=0.3)
        anim.bind(on_complete=lambda *args: self._finalize_removal(row_item, task))
        anim.start(row_item)

    def _finalize_removal(self, row_item, task):
        """
        Called after animation completes. We can either mark completed or remove from the heap.
        """
        # Option A: Mark the task as completed
        self.complete_task(task)

        # Option B: If you want to remove it entirely:
        # self.remove_task_completely(task)

    def get_all_tasks(self):
        """
        Return a sorted list of tasks if external code needs them.
        """
        return sorted(self.tasks)



    def remove_task(self, task_item):
        """Animate & remove task from UI."""
        animation = Animation(opacity=0, duration=0.3)
        animation.bind(on_complete=lambda *args: self.final_remove(task_item))
        animation.start(task_item)

    def final_remove(self, task_item):
        """Remove task after animation completes."""
        self.remove_widget(task_item)

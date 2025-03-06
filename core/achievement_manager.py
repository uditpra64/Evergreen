from kivy.event import EventDispatcher

class AchievementManager(EventDispatcher):
    """
    Tracks completed tasks & triggers growth.
    Uses Observer Pattern to notify tree growth.
    """

    def __init__(self, observer):
        super().__init__()
        self.completed_tasks_count = 0
        self.tree_observer = observer

    def task_completed(self):
        """Increment completed tasks & notify observer."""
        self.completed_tasks += 1
        print(f"Task Completed: {self.completed_tasks}")
        
        # Notify tree that progress has been made
        self.tree_observer.update_growth(self.completed_tasks)

    def update(self, event, data):
        if event == "TASK_COMPLETED":
            self.completed_tasks_count += 1
            # Check for achievements
            if self.completed_tasks_count == 5:
                print("Achievement Unlocked: 5 tasks completed!")
            if self.completed_tasks_count == 10:
                print("Achievement Unlocked: 10 tasks completed!")

class UIObserver:
    def update(self, event, data):
        if event == "TASK_ADDED":
            print(f"UI: A new task was added: {data.title}")
        elif event == "TASK_COMPLETED":
            print(f"UI: Task completed: {data.title}")

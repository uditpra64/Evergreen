class Task:
    """
    Task with priority levels: low, medium, high
    """
    PRIORITY_LOW = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_HIGH = 3
    
    PRIORITY_LABELS = {
        PRIORITY_LOW: "Low",
        PRIORITY_MEDIUM: "Medium",
        PRIORITY_HIGH: "High"
    }

    def __init__(self, title, priority=PRIORITY_MEDIUM):
        self.title = title
        self.priority = priority  # 1=low, 2=medium, 3=high
        self.completed = False

    def __lt__(self, other):
        """
        Compare tasks by priority (higher priority first)
        """
        # Reverse comparison so higher priority comes first
        return self.priority > other.priority

    def complete(self):
        self.completed = True
        
    def get_priority_label(self):
        return self.PRIORITY_LABELS.get(self.priority, "Medium")

    def __repr__(self):
        return f"Task(title='{self.title}', priority={self.get_priority_label()}, completed={self.completed})"
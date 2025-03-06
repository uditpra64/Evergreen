class Task:
    """
    A simple data class for tasks with priority.
    Priority 1 = lowest priority, higher numbers = higher priority
    or vice versa, as you prefer.
    """

    def __init__(self, title, priority=1):
        self.title = title
        self.priority = priority  # optional, 1 = low, 5 = high
        self.completed = False

    def __lt__(self, other):
        """
            Required for heapq to compare tasks.
            By default, lower priority means 'less than' => pops first.
            If you want highest priority first, invert the comparison.
        """
        return self.priority < other.priority

    def complete(self):
        self.completed = True

    def __repr__(self):
        return f"Task(title='{self.title}', priority={self.priority}, completed={self.completed})"
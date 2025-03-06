"""
tree_growth_observer.py

An observer that listens for events from TaskManager, PomodoroTimer, or StudyData,
and updates a Tree Growth FSM accordingly.
"""

class TreeGrowthObserver:
    """
    Observes events like:
      - "TASK_COMPLETED"
      - "lap_complete"
      - "hours_updated"
    Then calls your TreeGrowthFSM to increment growth accordingly.
    """

    def __init__(self, fsm):
        self.fsm = fsm

    def on_data_updated(self, event, data):
        """
        Called when an observed subject notifies:
         - event: string e.g. "TASK_COMPLETED", "lap_complete", "hours_updated"
         - data:  e.g. number of tasks done, laps completed, total hours
        """
        if event == "TASK_COMPLETED":
            # data might be the task object or the number of tasks completed
            # If you want to increment the FSM by 1 for each completed task:
            self.fsm.update_growth(laps=0, tasks=1)

        elif event == "lap_complete":
            # data might be laps completed or 1 for a single lap
            self.fsm.update_growth(laps=1, tasks=0)

        elif event == "pomodoro_done":
            # data = total laps completed
            # e.g. give an extra boost or final update
            self.fsm.update_growth(laps=data, tasks=0)

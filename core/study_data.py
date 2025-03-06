import json
import os
import threading
from kivy.event import EventDispatcher
from kivy.clock import Clock

    
DATA_FILE = "evergreen_data.json"

class StudyData(EventDispatcher):
    """
    Subject that holds user data (nested dict) and notifies observers on changes.
    """
    __events__ = ("on_data_updated",)  # We'll fire 'on_data_updated' event

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_minutes = 0  # initialize counter
        self._data = {
            "study_hours": {},      # e.g. { "2023-09-01": 1.5, "2023-09-02": 2.0 }
            "tasks_completed": {},  # e.g. { "task_id": True/False }
            "total_hours": 0.0,
        }
        # Load existing data from JSON if available
        self.load_data()
        
        # Schedule the timer ONCE here
        Clock.schedule_interval(self.update_minutes, 60)

    def set_study_hours(self, date_str, hours):
        """
        Set hours for a specific date, update total, and notify.
        """
        self._data["study_hours"][date_str] = hours
        self._data["total_hours"] = sum(self._data["study_hours"].values())
        self._async_save()  # Save in background
        self.dispatch("on_data_updated", self._data)

    def update_minutes(self, dt):
        """
        Called every minute to update the minutes counter.
        Don't schedule another timer here - that causes multiple timers.
        """
        self.current_minutes += 1
        # REMOVED: Clock.schedule_interval(self.update_minutes, 60)

    def reset_minutes(self):
        """Reset the minutes counter"""
        self.current_minutes = 0

    def get_current_minutes(self):
        """Get the current minutes counter value"""
        return self.current_minutes

    def complete_task(self, task_id):
        """
        Mark a task as completed.
        """
        self._data["tasks_completed"][task_id] = True
        self._async_save()
        self.dispatch("on_data_updated", self._data)

    def get_data(self):
        """Return the entire data dictionary"""
        return self._data

    def on_data_updated(self, updated_data):
        """
        Observer event. Observers can bind to this method.
        """
        pass

    def _async_save(self):
        """
        Save data in a background thread to avoid blocking UI.
        """
        def _worker(data_copy):
            try:
                with open(DATA_FILE, "w") as f:
                    json.dump(data_copy, f, indent=4)
            except Exception as e:
                print("Error saving data:", e)

        # Make a copy to avoid concurrency issues
        data_copy = dict(self._data)
        thread = threading.Thread(target=_worker, args=(data_copy,), daemon=True)
        thread.start()

    def load_data(self):
        """
        Load nested dictionary from JSON if exists.
        """
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    file_data = json.load(f)
                self._data.update(file_data)
            except Exception as e:
                print("Error loading data:", e)
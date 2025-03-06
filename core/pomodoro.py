# File: /core/pomodoro.py

from enum import Enum
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty

from core.subject import Subject

class PomodoroState(Enum):
    WORK = 1
    BREAK = 2
    DONE = 3

class PomodoroWidget(Subject, Widget):
    """
    Advanced Pomodoro timer with a Work + Break cycle (25 min + 5 min).
    It computes how many laps fit into study_hours (e.g., 5 hours => 10 laps).
    """

    # If user enters how many hours they plan to study:
    study_hours = NumericProperty(1.0)

    # Work/Break durations (seconds). Example: 25 min / 5 min
    work_duration = NumericProperty(25 * 60)   # 25 minutes
    break_duration = NumericProperty(5 * 60)   # 5 minutes

    # Track progress
    laps_completed = NumericProperty(0)        
    current_block_time_left = NumericProperty(0)

    # For UI display
    time_left_str = StringProperty("25:00")    
    timer_running = False

    # Finite State for the Pomodoro block
    current_state = PomodoroState.WORK        

    def __init__(
        self,
        study_hours=None,
        work_duration=25 * 60,
        break_duration=5 * 60,
        total_laps=None, 
        update_callback=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Store parameters
        self.study_hours = study_hours or 1.0
        self.work_duration = work_duration
        self.break_duration = break_duration

        # If total_laps is not provided, compute from hours
        if total_laps is None:
            self._compute_laps_from_hours()
        else:
            self.total_laps = total_laps

        # External UI callback for tree growth or display
        self.update_callback = update_callback

        # Build the list of blocks (WORK + BREAK pairs)
        self._build_circular_blocks()

        # Start at block index 0
        self.current_block_index = 0
        self._apply_current_block()

        # Initially not running
        self.timer_running = False

    def _compute_laps_from_hours(self):
        """
        We assume 1 Pomodoro cycle = (work_duration + break_duration) = 30 minutes by default.
        If user enters X hours, we compute how many full cycles fit.
        E.g. 5 hours => 5 * 60 = 300 minutes => 300 // 30 = 10 laps.
        """
        total_study_seconds = int(self.study_hours * 3600)
        lap_cycle = self.work_duration + self.break_duration  # e.g. 1500 + 300 = 1800 (30 min)

        possible_laps = total_study_seconds // lap_cycle
        if possible_laps < 1:
            possible_laps = 1  # Ensure at least 1 lap if user input is small

        self.total_laps = possible_laps

    def _build_circular_blocks(self):
        """
        Build a list of (PomodoroState, duration) for each lap:
         - For each lap => WORK + BREAK
        So 5 laps => 10 blocks total.
        """
        self.blocks = []
        for _ in range(self.total_laps):
            self.blocks.append((PomodoroState.WORK, self.work_duration))
            self.blocks.append((PomodoroState.BREAK, self.break_duration))

    def _apply_current_block(self):
        """
        Move to the block at current_block_index, or DONE if we've used them all.
        """
        if self.current_block_index >= len(self.blocks):
            self.current_state = PomodoroState.DONE
            self.current_block_time_left = 0
            self._update_time_str()
            self._notify_done()
            return

        state, duration = self.blocks[self.current_block_index]
        self.current_state = state
        self.current_block_time_left = duration
        self._update_time_str()

    def start_timer(self):
        """Begin counting down if not already running and not DONE."""
        if not self.timer_running and self.current_state != PomodoroState.DONE:
            self.timer_running = True
            Clock.schedule_interval(self._tick, 1)

    def stop_timer(self):
        """Stop the countdown."""
        if self.timer_running:
            self.timer_running = False
            Clock.unschedule(self._tick)

    def reset_timer(self, new_hours=None):
        """
        Resets the Pomodoro logic:
          - stops the timer
          - re-computes laps if new_hours is provided
          - sets laps_completed = 0
          - rebuilds blocks, applies the first block
        """
        self.stop_timer()
        if new_hours is not None:
            self.study_hours = new_hours
            self._compute_laps_from_hours()

        self.laps_completed = 0
        self.current_block_index = 0
        self._build_circular_blocks()
        self._apply_current_block()
        self.timer_running = False

    def _tick(self, dt):
        """Called every second by Kivy's Clock."""
        if self.current_state == PomodoroState.DONE:
            return

        # If we've completed enough laps, mark DONE
        if self.laps_completed >= self.total_laps:
            self.current_state = PomodoroState.DONE
            self._notify_done()
            return

        # Count down
        if self.current_block_time_left > 0:
            self.current_block_time_left -= 1
            self._update_time_str()
            self._notify_update()
        else:
            # The current block ended => move to next
            self._handle_block_end()

    def _handle_block_end(self):
        """Advance from WORK to BREAK, or from BREAK to the next lap."""
        if self.current_state == PomodoroState.WORK:
            # Completed a WORK block => increment laps
            self.laps_completed += 1
            self.notify("lap_complete", 1)
            # If we finished all laps
            if self.laps_completed >= self.total_laps:
                self.current_state = PomodoroState.DONE
                self.current_block_time_left = 0
                self._update_time_str()
                self._notify_done()
                return

        # Move to next block in the list
        self.current_block_index += 1
        if self.current_block_index >= len(self.blocks):
            # Out of blocks => DONE
            self.current_state = PomodoroState.DONE
            self.current_block_time_left = 0
            self._update_time_str()
            self._notify_done()
        else:
            self._apply_current_block()

        self._notify_update()

    def _update_time_str(self):
        """Convert current_block_time_left to mm:ss and store in time_left_str."""
        minutes = self.current_block_time_left // 60
        seconds = self.current_block_time_left % 60
        self.time_left_str = f"{minutes:02d}:{seconds:02d}"

    def _notify_update(self):
        """
        If you have a callback, call it here so your UI can refresh.
        Also dispatch an event for observers if needed.
        """
        if self.update_callback:
            laps_remaining = max(self.total_laps - self.laps_completed, 0)
            block_type = "work" if self.current_state == PomodoroState.WORK else "break"
            self.update_callback(self.time_left_str, block_type, laps_remaining)

        # Notify observers every second (optional)
        self.notify("pomodoro_tick", {"state": self.current_state, "time_left": self.time_left_str})

    def _notify_done(self):
        """Called when all laps are finished."""
        self.stop_timer()
        if self.update_callback:
            self.update_callback("Done!", "done", 0)
        self.notify("pomodoro_done", self.laps_completed)

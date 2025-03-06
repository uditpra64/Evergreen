class TreeGrowthFSM:
    tree_images = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png",
        "7.png",
        "8.png",
        "9.png",
        "10.png",
        "11.png"
        ]

    def __init__(self):
        """
        Initialize the FSM with:
          - current_stage: which index of tree_images we're at
          - growth_score: a running total of all points from hours, laps, tasks
        """
        self.current_stage = 0
        self.growth_score = 0.0  # cumulative points from all user activity
        self.total_stages = len(self.tree_images)
        self.points_per_stage = 10.0  # Default value, will be adjusted based on study hours
        
    def set_study_hours(self, hours):
        """
        Adjust points_per_stage based on total study hours so tree fully
        grows by the time all pomodoros are completed
        
        Args:
            hours: Total study hours planned
        """
        # Calculate how many points would be earned by completing all pomodoros
        # Assume 2 points per hour of study
        total_expected_points = hours * 2.0
        
        # We want the tree to reach the final stage (11) by the time
        # all study hours are completed
        # Number of growth stages = total_stages - 1 (since we start at stage 0)
        if total_expected_points > 0:
            self.points_per_stage = total_expected_points / (self.total_stages - 1)
        else:
            # Default if hours is 0
            self.points_per_stage = 10.0
            
        # Ensure minimum value
        if self.points_per_stage < 1.0:
            self.points_per_stage = 1.0
            
        print(f"Set points_per_stage to {self.points_per_stage} for {hours} hours")
        
    def update_growth(self, hours=0.0, laps=0, tasks=0):
        """Update tree growth based on study activity"""
        WEIGHT_HOURS = 2.0   # each hour studied is worth 2 points
        WEIGHT_LAPS = 0.5    # each pomodoro lap is 0.5 point
        WEIGHT_TASKS = 1.0   # each completed task is 1 point

        points = (hours * WEIGHT_HOURS) + (laps * WEIGHT_LAPS) + (tasks * WEIGHT_TASKS)
        self.growth_score += points

        # Compute the new stage
        new_stage = min(int(self.growth_score // self.points_per_stage), self.total_stages - 1)
        
        # If the stage actually advanced, update and show
        if new_stage > self.current_stage:
            old_stage = self.current_stage
            self.current_stage = new_stage
            self.display_tree()
            return True
            
        return False

    def display_tree(self):
        """
        Called whenever the tree advances to a new stage.
        """
        stage_name = self.tree_images[self.current_stage]
        print(f"The tree advanced to stage: {stage_name}")

    def get_current_stage(self):
        """
        Returns the current stage index
        """
        return self.current_stage
        
    def get_growth_percent(self):
        """
        Returns percentage of growth to the next stage (0-100)
        """
        if self.current_stage >= self.total_stages - 1:
            return 100.0  # Already at max stage
            
        current_stage_points = self.current_stage * self.points_per_stage
        next_stage_points = (self.current_stage + 1) * self.points_per_stage
        
        # Calculate percentage to next stage
        points_in_current_stage = self.growth_score - current_stage_points
        points_needed_for_stage = next_stage_points - current_stage_points
        
        if points_needed_for_stage > 0:
            percent = (points_in_current_stage / points_needed_for_stage) * 100
            return min(percent, 100.0)
        else:
            return 100.0

    def get_growth_score(self):
        """
        Optional helper if you need to show the raw score for debugging.
        """
        return self.growth_score
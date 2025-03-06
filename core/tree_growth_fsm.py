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
        # Add this line to define points_per_stage
        self.points_per_stage = 10.0  # Points needed to advance to next stage

    def update_growth(self, hours=0.0, laps=0, tasks=0):
        WEIGHT_HOURS = 2.0   # each hour studied is worth 2 points
        WEIGHT_LAPS = 1.0    # each pomodoro lap is 1 point
        WEIGHT_TASKS = 3.0   # each completed task is 3 points

        points = (hours * WEIGHT_HOURS) + (laps * WEIGHT_LAPS) + (tasks * WEIGHT_TASKS)
        self.growth_score += points

        # Compute the new stage
        new_stage = int(self.growth_score // self.points_per_stage)
        if new_stage >= self.total_stages:
            new_stage = self.total_stages - 1

        # If the stage actually advanced, update and show
        if new_stage > self.current_stage:
            self.current_stage = new_stage
            self.display_tree()

    def display_tree(self):
        """
        Called whenever the tree advances to a new stage.
        In a real app, you'd do something like:
          - Reload the tree image in TreeScreen
          - Animate the growth
          - Show a congratulatory popup
        """
        stage_name = self.tree_images[self.current_stage]
        print(f"The tree advanced to stage: {stage_name}")

    def get_current_stage(self):
        """
        Returns the string name of the current stage,
        """
        return self.current_stage

    def get_growth_score(self):
        """
        Optional helper if you need to show the raw score for debugging.
        """
        return self.growth_score
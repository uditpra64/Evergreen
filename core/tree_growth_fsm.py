class TreeGrowthFSM:
    """
    Simplified Tree Growth Finite State Machine
    
    This class manages the current growth stage of the tree.
    Growth is purely time-based and managed by TreeScreen.
    """
    
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
        """
        self.current_stage = 0
        self.total_stages = len(self.tree_images)
        
    def set_stage(self, stage_index):
        """
        Set the tree to a specific growth stage
        
        Args:
            stage_index: The index of the stage to set (0-based)
        
        Returns:
            True if the stage changed, False otherwise
        """
        # Make sure stage is within valid range
        stage_index = max(0, min(stage_index, self.total_stages - 1))
        
        # Check if stage actually changed
        if stage_index != self.current_stage:
            old_stage = self.current_stage
            self.current_stage = stage_index
            self.display_tree()
            return True
            
        return False

    def display_tree(self):
        """
        Called whenever the tree advances to a new stage.
        This is just for logging - actual display is handled by TreeScreen.
        """
        stage_name = self.tree_images[self.current_stage]
        print(f"The tree advanced to stage: {stage_name}")

    def get_current_stage(self):
        """
        Returns the current stage index
        """
        return self.current_stage
import random
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.core.window import Window

class Cloud(Image):
    def __init__(self, size_factor=None, speed=None, **kwargs):
        super().__init__(**kwargs)

        # Randomize cloud size for more natural look
        self.size_factor = size_factor if size_factor is not None else random.uniform(0.5, 1.5)
        
        # Apply size factor to cloud dimensions
        base_width, base_height = 100, 60
        self.size = (base_width * self.size_factor, base_height * self.size_factor)
        
        # Adjust opacity based on size (smaller clouds appear more distant)
        self.opacity = 0.5 + (0.5 * self.size_factor)
        
        # Store the speed parameter (using a slower default range)
        self.speed = speed if speed is not None else random.uniform(15, 35)

        # Start the cloud animation
        self.animate_cloud()

    def animate_cloud(self):
        # Calculate duration based on speed (slower speed = longer duration)
        duration = Window.width / self.speed
        
        # Create animation to move cloud across screen
        anim = Animation(x=Window.width, duration=duration)
        anim.bind(on_complete=lambda *args: self.reset_and_animate())
        anim.start(self)

    def reset_and_animate(self):
        # Reset the cloud's position to start again from the left
        # Position vertically in the top portion of the screen
        
        # Calculate vertical positioning range (top third of screen)
        # Convert to integers for randint
        top_position = int(Window.height - 20)
        bottom_position = int(Window.height // 2)  # Middle of screen
        
        # Make sure bottom_position is less than top_position
        if bottom_position >= top_position:
            bottom_position = top_position - 50
            
        # Set random Y position
        self.y = random.randint(bottom_position, top_position)
        
        # Reset X position to left of screen
        self.x = -self.width
        
        # Randomize speed for next pass
        self.speed = random.uniform(15, 35)
        
        # Start animation again
        self.animate_cloud()
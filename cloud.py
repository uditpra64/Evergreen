import random
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.core.window import Window

class Cloud(Image):
    def __init__(self, speed=None, **kwargs):
        super().__init__(**kwargs)

        # Store the speed parameter (default to random if not set)
        self.speed = speed if speed is not None else random.uniform(30, 80)

        # Start the cloud animation
        self.animate_cloud()

    def animate_cloud(self):
        duration = self._pick_duration() 
        anim = Animation(x=Window.width, duration=self.speed)
        anim.bind(on_complete=lambda *args: self.reset_and_animate()) # When the animation completes, reset the cloud's position and animate again.
        anim.start(self)

    def reset_and_animate(self):
        # Reset the cloud's position to start again from the left.
        from kivy.core.window import Window
        # random Y near top half
        self.y = random.randint(Window.height // 2, Window.height - self.height)
        self.x = -self.width
        self.animate_cloud()
    
    def _pick_duration(self):
        return random.uniform(8, 15)
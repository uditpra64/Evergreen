from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDRaisedButton
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.image import Image
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage

# Load the image and set the window size to the image's size
img = CoreImage("images/home_screen.png")
Window.size = img.texture.size  # Set the window size to match the image dimensions

# Register Times New Roman font
LabelBase.register(name="TimesNewRoman", fn_regular="font/times.ttf")
LabelBase.register(name="Munro", fn_regular="font/Munro.ttf")

class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_layout = FloatLayout()
        self.add_widget(self.main_layout)

        self.bg_image = Image(
            source="images/home_screen.png",   
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        # Add background image first so it remains behind other widgets
        self.main_layout.add_widget(self.bg_image)

        self.title_label = Label(
            text="EverGreen",
            font_name="Munro",
            font_size="100sp",
            color=(1, 1, 1, 1),
            halign="center",
            pos_hint={"center_x": 0.5, "top": 1.1} 
        )
        self.main_layout.add_widget(self.title_label)

        self.start_button = MDRaisedButton(
            text="Start Game",
            font_name="Munro",
            size_hint=(None, None),
            width=300,
            height=60,
            font_size="30sp",
            pos_hint={"center_x": 0.5, "y": 0.15},  # ~15% from bottom
            md_bg_color=(0.3, 0.6, 0.3, 1),  # greenish
        )
        self.start_button.bind(on_release=self.on_start)
        self.main_layout.add_widget(self.start_button)

        self.quit_button = MDRaisedButton(
            text="Quit",
            font_name="Munro",
            size_hint=(None, None),
            width=300,
            height=60,
            font_size="30sp",
            pos_hint={"center_x": 0.5, "y": 0.05},  # ~5% from bottom
            md_bg_color=(0.7, 0.2, 0.2, 1) # reddish
        )
        self.quit_button.bind(on_release=self.on_quit)
        self.main_layout.add_widget(self.quit_button)

    def on_start(self, instance):
        """Start Game button logic."""
        # Switch to your 'study_screen' or 'game_screen'
        self.manager.current = "study_screen"

    def on_quit(self, instance):
        """Quit button logic."""
        # Gracefully exit the app
        App.get_running_app().stop()
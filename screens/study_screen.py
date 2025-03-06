from kivymd.uix.screen import MDScreen
from kivy.animation import Animation
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivy.uix.label import Label
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.graphics import Color, Rectangle
from datetime import date 
from core.study_data import StudyData
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout

# Load the image and set the window size to the image's size
img = CoreImage("images/home_screen.png")
Window.size = img.texture.size  # Set the window size to match the image dimensions

LabelBase.register(name="Munro", fn_regular="font/Munro.ttf")

#show hours studied in the week 

class StudyScreen(MDScreen):

    def __init__(self, study_data: StudyData, **kwargs):
        super().__init__(**kwargs)
        self.study_data = study_data

        # 1) Create background image with self.bg_rect
        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(
                source="images/home_screen.png",
                size=self.size,
                pos=self.pos
            )
        self.bind(size=self.update_rect, pos=self.update_rect)

        # 1) AnchorLayout to center everything on the screen
        anchor_layout = AnchorLayout(
            anchor_x="center",
            anchor_y="center"
        )
        self.add_widget(anchor_layout)

        # Create an overlay MDBoxLayout for interactive widgets
        self.interactive_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20),
            width=dp(400),   # Adjust as desired
            height=dp(300)   # Adjust as desired
        )
        anchor_layout.add_widget(self.interactive_layout)

        self.label = Label(
            text="Please enter the number of hours you wish to study to proceed...",
            font_name="Munro",
            font_size="28sp",
            halign="center",
            bold=True, 
            color=(1, 0, 0, 1), 
            size_hint=(1, None),
            width=dp(380),
            height=dp(60)
        )
        # Ensure the label sizes to its text
        self.label.bind(texture_size=self.label.setter('size'))
        self.interactive_layout.add_widget(self.label)

        # 4) Input row for text field
        self.input_row = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10)
        )
        self.interactive_layout.add_widget(self.input_row)

        # 5) White text box with black border
        self.input_field = MDTextField(
            hint_text="Enter hours",
            size_hint=(None, None),
            width=dp(300),
            height=dp(60),
            mode="rectangle",  
            line_color_focus=(1, 1, 1, 1),  # Black border when active
            line_color_normal=(1, 1, 1, 1),  # Black border when inactive
            foreground_color=(1, 1, 1, 1),  # Black text color
            background_color=(1, 1, 1, 1), # White background
            font_size="30sp",
            font_name="Munro",
        )
        self.input_row.add_widget(self.input_field)

        # 6) Submit button
        self.submit_button = MDRaisedButton(
            text="Submit",
            font_name="Munro",
            width=dp(200),
            height=dp(50),
            font_size="30sp",
            on_release=self.on_submit
        )
        self.interactive_layout.add_widget(self.submit_button)

        # 7) Confirmation Label (for feedback)
        self.confirmation_label = MDLabel(
            text="",
            halign="center",
            font_style="Subtitle1",
            font_size="20sp",
            pos_hint={"center_x": 0.5, "center_y": 0.65},
            opacity=0  
        )
        self.interactive_layout.add_widget(self.confirmation_label)

    def update_rect(self, *args):
        """Keep the background rectangle size in sync with the screen."""
        self.bg_rect.size = self.size     
        self.bg_rect.pos = self.pos

    def on_submit(self, instance):
        hours_text = self.input_field.text.strip()
        if not hours_text:
            self.show_feedback("Please enter a valid number.", font_name="Munro", color=(1,0,0,1))  # Red error
            return
        
        # Convert to float
        try:
            hours = float(hours_text)
        except ValueError:
            self.show_feedback("Invalid number!", font_name="Munro", color=(1,0,0,1))
            return
        
        # If valid, store in StudyData (nested dictionary) with today's date
        today_str = date.today().isoformat()
        self.study_data.set_study_hours(today_str, hours)

        # Determine the correct wording for "hour" vs. "hours"
        hour_label_text = "hour" if hours == 1 else "hours"
        self.show_feedback(hours, hour_label_text)

        # Possibly navigate to next screen or show success message
        self.show_feedback(f"Recorded {hours} hour(s).", color=(0,1,0,1))

        # Switch to tree screen after a short delay (e.g., 1 second)
        Clock.schedule_once(lambda dt: self.switch_to_tree_screen(), 1)

    def switch_to_tree_screen(self):
        if self.manager:
            self.manager.current = "tree_screen"

    def show_feedback(self, msg, color=(1,1,1,1)):
        """Display a message in confirmation_label with fade-in animation."""
        self.confirmation_label.text = ""
        self.confirmation_label.text_color = [1, 0, 0, 1]
        self.confirmation_label.opacity = 0
        anim = Animation(opacity=1, duration=0.5)
        anim.start(self.confirmation_label)
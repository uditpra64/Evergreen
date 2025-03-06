import kivy
import os
import random
import math
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.label import Label
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.navigationdrawer import MDNavigationLayout
from kivy.core.text import LabelBase
from kivymd.uix.progressbar import MDProgressBar
from kivy.uix.screenmanager import Screen, ScreenManager

from cloud import Cloud
from core.pomodoro import PomodoroWidget
from core.right_drawer import RightDrawer
from core.task_manager import TaskManager
from core.achievement_manager import AchievementManager
from core.tree_growth_observer import TreeGrowthObserver
from core.study_data import StudyData
from core.tree_growth_fsm import TreeGrowthFSM

kivy.require('2.2.0')

LabelBase.register(name="TimesNewRoman", fn_regular="font/times.ttf")
LabelBase.register(name="Munro", fn_regular="font/Munro.ttf")


class PomodoroCard(MDCard):
    def __init__(self, study_hours, **kwargs):
        super().__init__(**kwargs)

        # Smaller fixed size
        self.size_hint = (None, None)
        self.size = (300, 140)
        # Position higher up on the left
        self.pos_hint = {"center_x": 0.2, "top": 0.7}

        self.work_color = (204/255, 84/255, 84/255, 1)  # 25-min block color
        self.break_color = (173/255, 223/255, 255/255, 1)  # 5-min break color
        self.radius = [20, 20, 20, 20]

        # Title label with smaller font & wide text_size
        self.title_label = Label(
            text="Pomodoro Timer",
            font_name="Munro",
            halign="center",
            font_size="20sp",
            size_hint=(1, 0.3),
            text_size=(self.width - 10, None)
        )
        self.add_widget(self.title_label)

        # Timer layout
        self.timer_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, 0.7),
            spacing=2,
            padding=(5, 2),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.add_widget(self.timer_layout)

        # Create the Pomodoro widget
        self.pomo_widget = PomodoroWidget(
            study_hours=study_hours,     # Actual hours from TreeScreen
            update_callback=self.update_timer_display
        )
        self.pomo_widget.size_hint = (1, 1)
        self.timer_layout.add_widget(self.pomo_widget)

        # Default to work color
        self.md_bg_color = self.work_color

    def update_timer_display(self, time_str, block_type, laps_remaining):
        # Clear old display
        self.timer_layout.clear_widgets()

        # If done
        if time_str == "Done!":
            done_label = MDLabel(
                text="Session Complete!",
                halign="center",
                font_style="H6"
            )
            self.timer_layout.add_widget(done_label)
            return

        # Decide background color
        if block_type == "work":
            self.md_bg_color = self.work_color
            self.title_label.text = "Pomodoro Timer"
        else:
            self.md_bg_color = self.break_color
            self.title_label.text = "Break Time!"

        # Build digit labels with smaller boxes
        for ch in time_str:
            digit_container = MDBoxLayout(
                orientation="vertical",
                size_hint=(None, None),
                size=(36, 48),
                md_bg_color=(0.98, 0.98, 0.98, 1),
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            )
            digit_label = MDLabel(
                text=ch,
                halign="center",
                font_style="H5",
                font_size="20sp",
                size_hint=(1, 1)
            )
            digit_container.add_widget(digit_label)
            self.timer_layout.add_widget(digit_container)

        # Lap count label
        lap_label = MDLabel(
            text=f"Sessions left: {laps_remaining}",
            halign="center",
            font_style="Subtitle2",
            size_hint=(None, None),
            size=(100, 30)
        )
        self.timer_layout.add_widget(lap_label)


class TreeScreen(MDScreen):
    def __init__(self, study_data: StudyData, **kwargs):
        super().__init__(**kwargs)
        self.study_data = study_data
        self.study_data.bind(on_data_updated=self.on_study_update)

        self.task_manager = TaskManager()
        self.fsm = TreeGrowthFSM()
        self.tree_observer = TreeGrowthObserver(self.fsm)

        # Bind the FSM observer to data changes
        self.study_data.bind(on_data_updated=self.tree_observer.on_data_updated)
        self.task_manager.bind(on_data_updated=self.tree_observer.on_data_updated)
        self.achievement_manager = AchievementManager(observer=self.tree_observer)

        # FloatLayout for main content
        self.layout = FloatLayout()

        # Progress Bar
        self.progress_bar = MDProgressBar(
            value=0,
            max=2,
            size_hint=(0.8, None),
            height=20,
            pos_hint={"center_x": 0.5, "top": 0.95}
        )
        self.layout.add_widget(self.progress_bar)

        # Load stored study hours from StudyData
        self.total_study_hours = self.study_data.get_data()["total_hours"]

        # Tree images
        self.tree_folder = os.path.join(os.path.dirname(__file__), "..", "images", "tree_images")
        self.image_paths = [os.path.join(self.tree_folder, f"{i}.png") for i in range(1, 6)]
        self.image_index = 0
        self.tree_image = Image(
            source=self.image_paths[self.image_index],
            size_hint=(None, None),
            size=(300, 400),
            pos_hint={"center_x": 0.5, "center_y": 0.4}
        )
        self.layout.add_widget(self.tree_image)
        self.update_tree_growth()

        # Back button
        self.back_button = MDRaisedButton(
            text="Back",
            pos_hint={"right": 0.95, "top": 0.95},
            on_release=self.show_reset_dialog,
            size_hint=(None, None),
            size=(150, 60),
            font_size="20sp",
            width=200,
        )
        self.layout.add_widget(self.back_button)

        # Create PomodoroCard using the actual total_study_hours
        self.pomodoro_card = PomodoroCard(self.total_study_hours)
        self.layout.add_widget(self.pomodoro_card)
        # Start the Pomodoro timer
        self.pomodoro_card.pomo_widget.start_timer()

        # Clouds
        Clock.schedule_once(self.spawn_one_cloud_randomly, 2)

        # Sky-blue background
        with self.layout.canvas.before:
            Color(0.53, 0.81, 0.98, 1)
            self.bg_rect = Rectangle(pos=self.layout.pos, size=self.layout.size)
        self.layout.bind(pos=self.reposition_tree, size=self.reposition_tree)
        self.layout.bind(pos=self._update_bg, size=self._update_bg)

        # Wrap FloatLayout in a Screen + ScreenManager
        self.screen_manager = ScreenManager()
        content_screen = Screen(name="tree_content")
        content_screen.add_widget(self.layout)
        self.screen_manager.add_widget(content_screen)

        # MDNavigationLayout
        self.nav_layout = MDNavigationLayout()
        self.nav_layout.add_widget(self.screen_manager)

        # Right Drawer
        self.right_drawer = RightDrawer(task_manager=self.task_manager, width=Window.width * 0.50)
        self.nav_layout.add_widget(self.right_drawer)

        # Add nav_layout to MDScreen
        self.add_widget(self.nav_layout)

        Window.bind(on_resize=self.update_drawer_width)

        # Drawer toggle button
        self.arrow_button = MDIconButton(
            icon="chevron-left",
            pos_hint={"center_x": 0.95, "center_y": 0.8},
            font_size="40sp",
            on_release=self.toggle_drawer
        )
        self.add_widget(self.arrow_button)

        # Update progress bar every minute
        Clock.schedule_interval(self.update_progress_bar, 60)

    def update_drawer_width(self, instance, width, height):
        self.right_drawer.width = width * 0.40

    def toggle_drawer(self, instance):
        self.right_drawer.set_state("toggle")
        self.right_drawer.update_triangle()

    def reposition_tree(self, instance=None, value=None):
        # Place the tree to the right of the Pomodoro card
        self.tree_image.pos = (
            self.pomodoro_card.x + self.pomodoro_card.width + 100,
            self.pomodoro_card.y
        )

    def _update_bg(self, *args):
        self.bg_rect.pos = self.layout.pos
        self.bg_rect.size = self.layout.size
        self.add_background_elements()

    def on_study_update(self, instance, data):
        self.total_study_hours = data["total_hours"]
        self.update_tree_growth()

    def update_tree_growth(self):
        self.image_index = self.fsm.get_current_stage()
        self.tree_image.source = self.image_paths[self.image_index]
        self.tree_image.reload()
        print(f"Tree Growth Updated: {self.image_paths[self.image_index]} - based on observer events")

    def update_progress_bar(self, dt):
        current_minutes = self.study_data.get_current_minutes()
        self.progress_bar.value = current_minutes % 60
        self.progress_bar.max = 60

    def show_reset_dialog(self, *args):
        self.dialog = MDDialog(
            title="Reset progress?",
            text="Do you want to reset your progress and go back?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    font_name="Munro",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="RESET",
                    font_name="Munro",
                    on_release=lambda x: self.reset_and_go_back()
                )
            ]
        )
        self.dialog.open()

    def reset_and_go_back(self):
        # Instead of resetting to 1.0, reset to the actual hours or a new user input
        self.dialog.dismiss()
        self.pomodoro_card.pomo_widget.start_timer()  # if you want to restart timer
        self.manager.current = "study_screen"

    def add_background_elements(self):
        base_image_path = os.path.join(os.path.dirname(__file__), "..", "images")
        floor_path = os.path.join(base_image_path, "floor.png")
        grass_path = os.path.join(base_image_path, "grass.png")

        floor_width = 48
        floor_height = 96
        num_floor = math.ceil(Window.width / floor_width) + 1
        for i in range(num_floor):
            floor = Image(
                source=floor_path,
                allow_stretch=False,
                keep_ratio=True,
                size_hint=(None, None),
                size=(floor_width, floor_height),
                pos=(i * floor_width, 0)
            )
            self.layout.add_widget(floor)

        grass_width = 128
        grass_height = 64
        num_grass = math.ceil(Window.width / grass_width) + 1
        for i in range(num_grass):
            grass = Image(
                source=grass_path,
                size_hint=(None, None),
                allow_stretch=False,
                keep_ratio=True,
                size=(grass_width, grass_height),
                pos=(i * grass_width, floor_height)
            )
            self.layout.add_widget(grass)

    def spawn_one_cloud_randomly(self, dt):
        cloud_path = os.path.join(os.path.dirname(__file__), "..", "images", "cloud.png")
        cloud = Cloud(source=cloud_path, speed=random.uniform(30, 80))
        cloud.size_hint = (None, None)

        top_band = 100
        cloud.y = random.randint(Window.height - top_band, Window.height - 100)
        cloud.x = -cloud.width

        self.layout.add_widget(cloud)
        next_delay = random.uniform(2, 5)
        Clock.schedule_once(self.spawn_one_cloud_randomly, next_delay)

    def reset_pomodoro_and_tree(self, new_hours):
        # If you want a custom reset, e.g., re-init with new_hours
        self.pomodoro_card.pomo_widget.study_hours = new_hours
        self.pomodoro_card.pomo_widget.reset_timer(new_hours)
        self.pomodoro_card.pomo_widget.start_timer()

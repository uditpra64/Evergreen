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
from kivy.metrics import dp
from kivy.animation import Animation

from cloud import Cloud
from core.pomodoro import PomodoroWidget, PomodoroState
from core.right_drawer import RightDrawer
from core.task_manager import TaskManager
from core.tree_growth_observer import TreeGrowthObserver
from core.study_data import StudyData
from core.tree_growth_fsm import TreeGrowthFSM

kivy.require('2.2.0')

LabelBase.register(name="TimesNewRoman", fn_regular="font/times.ttf")
LabelBase.register(name="Munro", fn_regular="font/Munro.ttf")


class PomodoroCard(MDCard):
    def __init__(self, study_hours, **kwargs):
        super().__init__(**kwargs)

        # Fixed size and position
        self.size_hint = (None, None)
        self.size = (300, 180)  # Increased height to fit all content
        self.pos_hint = {"center_x": 0.2, "top": 0.7}
        self.padding = [15, 15, 15, 15]  # Add padding to prevent content overflow

        # Rounded corners and colors
        self.work_color = (204/255, 84/255, 84/255, 1)  # 25-min block color
        self.break_color = (173/255, 223/255, 255/255, 1)  # 5-min break color
        self.radius = [20, 20, 20, 20]
        self.md_bg_color = self.work_color
        
        # Create main vertical layout
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint=(1, 1)
        )
        
        # Title label at TOP
        self.title_label = Label(
            text="Pomodoro Timer",
            font_name="Munro",
            halign="center",
            font_size="20sp",
            size_hint=(1, 0.2),
            color=(1, 1, 1, 1)  # White text
        )
        main_layout.add_widget(self.title_label)

        # Timer display
        self.timer_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(2),
            size_hint=(1, 0.6),
            pos_hint={"center_x": 0.5}
        )
        main_layout.add_widget(self.timer_layout)

        # Sessions left indicator
        self.sessions_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, 0.2),
            pos_hint={"center_x": 0.5}
        )
        
        self.sessions_label = Label(
            text="Sessions left: 0",
            font_name="Munro",
            halign="center",
            font_size="16sp",
            color=(1, 1, 1, 1)  # White text
        )
        self.sessions_layout.add_widget(self.sessions_label)
        main_layout.add_widget(self.sessions_layout)

        # Add the main layout to the card
        self.add_widget(main_layout)

        # Create the Pomodoro widget
        self.pomo_widget = PomodoroWidget(
            study_hours=study_hours,     # Actual hours from TreeScreen
            update_callback=self.update_timer_display
        )
        self.pomo_widget.size_hint = (1, 1)

    def update_timer_display(self, time_str, block_type, laps_remaining):
        # Clear old display
        self.timer_layout.clear_widgets()

        # If done
        if time_str == "Done!":
            done_label = MDLabel(
                text="Session Complete!",
                halign="center",
                font_style="H6",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1)  # White text
            )
            self.timer_layout.add_widget(done_label)
            self.sessions_label.text = "All sessions completed!"
            
            # Notify parent screen (TreeScreen) that Pomodoro is done
            if hasattr(self, 'parent') and self.parent:
                parent_screen = self.get_parent_screen()
                if parent_screen and hasattr(parent_screen, 'show_completion_popup'):
                    parent_screen.show_completion_popup()
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
                pos_hint={"center_y": 0.5}
            )
            digit_label = MDLabel(
                text=ch,
                halign="center",
                font_style="H5",
                font_size="20sp",
                theme_text_color="Custom",
                text_color=(0.1, 0.1, 0.1, 1),  # Dark text on light background
                size_hint=(1, 1)
            )
            digit_container.add_widget(digit_label)
            self.timer_layout.add_widget(digit_container)

        # Fix for laps display - display actual remaining laps without +1
        self.sessions_label.text = f"Sessions left: {laps_remaining}"
    
    def get_parent_screen(self):
        """Find the parent TreeScreen"""
        current = self.parent
        while current:
            if isinstance(current, TreeScreen):
                return current
            current = current.parent
        return None


class TreeScreen(MDScreen):
    def __init__(self, study_data: StudyData, **kwargs):
        super().__init__(**kwargs)
        self.study_data = study_data
        self.study_data.bind(on_data_updated=self.on_study_update)

        self.task_manager = TaskManager()
        self.fsm = TreeGrowthFSM()
        
        # Set the study hours for time-based tree growth
        self.total_study_hours = self.study_data.get_data()["total_hours"]
        self.total_minutes = self.total_study_hours * 60
        self.tree_stages = 11  # Total number of tree images
        
        # Calculate minutes per stage
        self.minutes_per_stage = max(self.total_minutes / self.tree_stages, 1)
        print(f"Time-based growth: {self.minutes_per_stage:.1f} minutes per stage")
        
        # Track elapsed minutes
        self.elapsed_minutes = 0
        
        self.tree_observer = TreeGrowthObserver(self.fsm)

        # FloatLayout for main content
        self.layout = FloatLayout()

        # Status label for current state
        self.status_label = MDLabel(
            text="Ready to start your session",
            font_name="Munro",
            halign="center",
            size_hint=(0.8, None),
            height=dp(30),
            pos_hint={"center_x": 0.5, "top": 0.98}
        )
        self.layout.add_widget(self.status_label)

        # Progress Bar
        self.progress_bar = MDProgressBar(
            value=0,
            max=30,  # Set to default work_duration in minutes
            size_hint=(0.8, None),
            height=dp(12),
            pos_hint={"center_x": 0.5, "top": 0.95},
            color=(0.2, 0.7, 0.2, 1)  # Green color
        )
        self.layout.add_widget(self.progress_bar)
        
        # Reset the minutes counter when screen initializes
        self.study_data.reset_minutes()

        # Load stored study hours from StudyData
        self.total_study_hours = self.study_data.get_data()["total_hours"]

        # Tree images - update to include all 11 images
        self.tree_folder = os.path.join(os.path.dirname(__file__), "..", "images", "tree_images")
        self.image_paths = [os.path.join(self.tree_folder, f"{i}.png") for i in range(1, 12)]
        self.image_index = 0

        # Create the tree image - DON'T set pos_hint
        self.tree_image = Image(
            source=self.image_paths[self.image_index],
            size_hint=(None, None),
            size=(300, 400)
        )
        self.layout.add_widget(self.tree_image)
        # Position will be set in reposition_tree
        
        # Update tree growth initially
        self.update_tree_image()

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
        # Timer will start in on_enter

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

        # Update progress bar every second
        Clock.schedule_interval(self.update_progress_bar, 1)
        
        # Schedule tree growth check every minute
        Clock.schedule_interval(self.check_tree_growth, 60)
        
        # Position the tree after layout is complete
        Clock.schedule_once(lambda dt: self.reposition_tree(), 0)
        
        # Store the completion popup so we only show it once
        self.completion_popup_shown = False
    
    def on_enter(self):
        """Called when the screen is entered (becomes active)"""
        # Start the Pomodoro timer when screen is actually displayed
        if not self.pomodoro_card.pomo_widget.timer_running:
            self.pomodoro_card.pomo_widget.reset_timer(self.total_study_hours)
            self.pomodoro_card.pomo_widget.start_timer()
            print("Timer started on screen entry")
            
        # Reset the completion popup flag
        self.completion_popup_shown = False
            
        # Make sure tree is properly positioned
        self.reposition_tree()

    def update_drawer_width(self, instance, width, height):
        self.right_drawer.width = width * 0.40

    def toggle_drawer(self, instance):
        self.right_drawer.set_state("toggle")
        self.right_drawer.update_triangle()

    def reposition_tree(self, instance=None, value=None):
        """Position the tree at the center of the screen over the ground"""
        # Get base dimensions for positioning
        floor_height = 96  # Height of floor.png
        grass_height = 64  # Height of grass.png
        
        # Calculate ground level (top of grass)
        ground_level = floor_height + grass_height
        
        # Always center the tree horizontally
        window_center = Window.width // 2
        tree_x = window_center - (self.tree_image.width // 2)
        
        # Calculate the y position to plant the tree in the ground
        tree_y = ground_level - 40
        
        # Set the tree position absolutely
        self.tree_image.pos = (tree_x, tree_y)
        print(f"Tree positioned at ({tree_x}, {tree_y})")

    def _update_bg(self, *args):
        self.bg_rect.pos = self.layout.pos
        self.bg_rect.size = self.layout.size
        self.add_background_elements()

    def on_study_update(self, instance, data):
        """When study data changes, update the tree and reset pomodoro"""
        old_hours = self.total_study_hours
        self.total_study_hours = data["total_hours"]
        self.total_minutes = self.total_study_hours * 60
        
        # Recalculate minutes per stage with new hours
        self.minutes_per_stage = max(self.total_minutes / self.tree_stages, 1)
        print(f"Updated time-based growth: {self.minutes_per_stage:.1f} minutes per stage")
        
        # Reset elapsed minutes
        self.elapsed_minutes = 0
        
        # Only reset the timer if hours actually changed
        if old_hours != self.total_study_hours:
            # Reset the pomodoro timer with new hours
            self.pomodoro_card.pomo_widget.reset_timer(self.total_study_hours)
            # Start the timer
            self.pomodoro_card.pomo_widget.start_timer()
        
        # Reset tree to first stage
        self.image_index = 0
        self.update_tree_image()
        
        # Reset the completion popup flag
        self.completion_popup_shown = False

    def check_tree_growth(self, dt):
        """Check if it's time to grow the tree (called every minute)"""
        # Increment elapsed minutes
        self.elapsed_minutes += 1
        
        # Calculate which stage we should be at based on elapsed minutes
        if self.minutes_per_stage > 0:
            new_stage = min(int(self.elapsed_minutes / self.minutes_per_stage), self.tree_stages - 1)
            
            # If we need to advance to a new stage
            if new_stage > self.image_index:
                self.image_index = new_stage
                print(f"Tree growing to stage {new_stage+1} after {self.elapsed_minutes} minutes")
                self.update_tree_image(animate=True)

    def update_tree_image(self, animate=False):
        """Update the tree image and optionally animate the growth"""
        # Ensure image_index is within bounds
        if self.image_index < 0:
            self.image_index = 0
        elif self.image_index >= len(self.image_paths):
            self.image_index = len(self.image_paths) - 1
            
        # Update image
        self.tree_image.source = self.image_paths[self.image_index]
        self.tree_image.reload()
        
        # If animation requested
        if animate:
            # Remember the original size so we can animate correctly
            orig_size = self.tree_image.size
            orig_pos = self.tree_image.pos
            
            # First slightly grow the tree
            grow_anim = Animation(size=(orig_size[0] * 1.2, orig_size[1] * 1.2), 
                                duration=0.3)
            # Then return to normal size
            grow_anim += Animation(size=orig_size, 
                                 duration=0.3)
            grow_anim.start(self.tree_image)
            
            # Show a notification
            self.show_tree_growth_notification(f"Your tree has grown to stage {self.image_index + 1}!")
            
            # Make sure tree stays in position after animation
            Clock.schedule_once(lambda dt: self.reposition_tree(), 0.7)
        
        print(f"Tree image updated: {self.image_paths[self.image_index]}")
        
        # Make sure tree is properly positioned
        self.reposition_tree()

    def update_progress_bar(self, dt):
        """Update progress bar to match Pomodoro timer"""
        # Get current block time left from Pomodoro
        time_left = self.pomodoro_card.pomo_widget.current_block_time_left
        total_time = 0
        
        # Check which block we're in
        if self.pomodoro_card.pomo_widget.current_state == PomodoroState.WORK:
            total_time = self.pomodoro_card.pomo_widget.work_duration
            state_text = "Work"
        elif self.pomodoro_card.pomo_widget.current_state == PomodoroState.BREAK:
            total_time = self.pomodoro_card.pomo_widget.break_duration
            state_text = "Break"
        else:
            state_text = "Done"
            
        # Set max to match current block total time
        if total_time > 0:
            self.progress_bar.max = total_time
            
            # Set value to time remaining (inverted for progress feel)
            self.progress_bar.value = total_time - time_left
        
        # Update status label
        if self.pomodoro_card.pomo_widget.current_state != PomodoroState.DONE:
            laps_text = f"Lap {self.pomodoro_card.pomo_widget.laps_completed + 1}/{self.pomodoro_card.pomo_widget.total_laps}"
            self.status_label.text = f"{state_text} Session - {laps_text}"
        else:
            self.status_label.text = "All sessions completed!"

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
        """Reset timer and go back to study screen"""
        self.dialog.dismiss()
        # Stop the timer before navigating
        self.pomodoro_card.pomo_widget.stop_timer()
        # Don't restart timer - let the user enter new hours
        self.manager.current = "study_screen"

    def add_background_elements(self):
        # Remove old elements first to avoid duplication
        for child in list(self.layout.children):
            if isinstance(child, Image) and (child.source.endswith('floor.png') or 
                                          child.source.endswith('grass.png')):
                self.layout.remove_widget(child)
        
        base_image_path = os.path.join(os.path.dirname(__file__), "..", "images")
        floor_path = os.path.join(base_image_path, "floor.png")
        grass_path = os.path.join(base_image_path, "grass.png")

        floor_width = 48
        floor_height = 96
        num_floor = math.ceil(Window.width / floor_width) + 1
        for i in range(num_floor):
            floor = Image(
                source=floor_path,
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
                size=(grass_width, grass_height),
                pos=(i * grass_width, floor_height)
            )
            self.layout.add_widget(grass)

    def spawn_one_cloud_randomly(self, dt):
        """Spawn a cloud with random size and speed"""
        # Check if we have too many clouds already
        cloud_count = sum(1 for child in self.layout.children if isinstance(child, Cloud))
        
        if cloud_count > 5:  # Limit total clouds to 5
            # Still schedule next spawn, but don't create a new cloud
            next_delay = random.uniform(5, 10)  # Longer delay between spawns
            Clock.schedule_once(self.spawn_one_cloud_randomly, next_delay)
            return
        
        cloud_path = os.path.join(os.path.dirname(__file__), "..", "images", "cloud.png")
        
        # Use slower speed range
        speed = random.uniform(15, 35)
        
        # Vary cloud size
        size_factor = random.uniform(0.5, 1.5)
        
        # Create the cloud with random speed and size
        cloud = Cloud(
            source=cloud_path, 
            speed=speed,
            size_factor=size_factor
        )
        
        # Position cloud off-screen to the left
        cloud.size_hint = (None, None)
        
        # Vary vertical position more
        height_range = Window.height // 3
        cloud.y = random.randint(Window.height - height_range, Window.height - 20)
        cloud.x = -cloud.width
        
        self.layout.add_widget(cloud)
        
        # Use longer delays between spawns
        next_delay = random.uniform(5, 15)  # 5-15 seconds between clouds
        Clock.schedule_once(self.spawn_one_cloud_randomly, next_delay)

    def show_tree_growth_notification(self, message):
        """Show a temporary notification for tree growth"""
        notification = MDLabel(
            text=message,
            halign="center",
            font_name="Munro",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.1, 0.7, 0.1, 1),
            size_hint=(None, None),
            size=(400, 50),
            pos_hint={"center_x": 0.5, "top": 0.9},
            opacity=0
        )
        
        self.layout.add_widget(notification)
        
        # Fade in, stay, fade out
        anim = Animation(opacity=1, duration=0.5) + \
               Animation(opacity=1, duration=2.0) + \
               Animation(opacity=0, duration=0.5)
        
        # Remove notification when animation completes
        def remove_notification(anim, widget):
            self.layout.remove_widget(widget)
        
        anim.bind(on_complete=remove_notification)
        anim.start(notification)

    def show_completion_popup(self):
        """Show a congratulations popup when study session is complete"""
        if not self.completion_popup_shown:
            self.completion_popup_shown = True
            
            dialog = MDDialog(
                title="Congratulations!",
                text="You have completed your study session! Great work!",
                buttons=[
                    MDFlatButton(
                        text="THANKS!",
                        font_name="Munro",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()

    def reset_pomodoro_and_tree(self, new_hours):
        # If you want a custom reset, e.g., re-init with new_hours
        self.pomodoro_card.pomo_widget.study_hours = new_hours
        self.pomodoro_card.pomo_widget.reset_timer(new_hours)
        self.pomodoro_card.pomo_widget.start_timer()
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from screens.home_screen import HomeScreen
from screens.study_screen import StudyScreen
from screens.tree_screen import TreeScreen
from core.study_data import StudyData 

class EvergreenApp(MDApp):
    def build(self):
        sm = ScreenManager()

        study_data = StudyData() 
        sm.add_widget(StudyScreen(name="study_screen", study_data=study_data))
        sm.add_widget(TreeScreen(name="tree_screen", study_data=study_data))
        sm.add_widget(HomeScreen(name="home_screen"))

        sm.current = "home_screen"
        
        return sm
    
if __name__ == "__main__":
    EvergreenApp().run()
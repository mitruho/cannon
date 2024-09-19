from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from cannon_constants import SCREEN_WIDTH, SCREEN_HEIGHT
from ui import *

class CannonApp(App):
    def build(self):
        Window.size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        Window.resizable = False
        Window.borderless = '1'
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(ScoreboardScreen(name='scoreboard'))
        sm.add_widget(SavesScreen(name='saves'))
        sm.add_widget(HelpScreen(name='help'))
        sm.add_widget(ObstaclesScreen(name='obstacles'))
        sm.add_widget(ProjectilesScreen(name='projectiles'))
        sm.add_widget(NicknameScreen(name='nickname'))
        return sm
if __name__ == '__main__':
    CannonApp().run()

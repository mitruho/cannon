from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty, StringProperty, ReferenceListProperty, ObjectProperty
import math
from cannon_constants import *

class Cannon(Widget):
    angle = NumericProperty(0)
    cannon_height = NumericProperty(50)

    def __init__(self, **kwargs):
        super(Cannon, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        mouse_x, mouse_y = args[1]
        dx = mouse_x - self.x
        dy = mouse_y - (self.y + self.height / 2)
        angle = Vector(dx, dy).angle(Vector(1, 0))
        self.angle = max(0, min(90, angle))

    @property
    def end_x(self):
        return self.x + self.cannon_height * math.cos(math.radians(self.angle))

    @property
    def end_y(self):
        return self.y + self.cannon_height * math.sin(math.radians(self.angle))

class Target(Widget):
    pass

BULLET_SIZE = (BULLET_RADIUS*2, BULLET_RADIUS*2)
BOMB_SIZE = (BOMB_RADIUS*2, BOMB_RADIUS*2)

class Projectile(Widget):
    projectile_type = NumericProperty(0)
    projectile_height = NumericProperty(BULLET_SIZE[1])
    projectile_width = NumericProperty(BULLET_SIZE[0])
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)
    vel = ReferenceListProperty(vel_x, vel_y)
    gravity_x = NumericProperty(0)
    gravity_y = NumericProperty(-9.8)
    acceleration = ReferenceListProperty(gravity_x, gravity_y)
    launch_speed = NumericProperty(BOMB_MAX_VEL)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.launch_angle_radians = 0
        self._clock_event = None
        self.x = -100
        self.y = -100
        self.update_size()

    def on_projectile_type(self, instance, value):
        self.reset_movement()
        self.update_size()

    def update_size(self):
        if self.projectile_type == 0:
            self.projectile_width, self.projectile_height = BULLET_SIZE
            self.launch_speed = BULLET_MAX_VEL
            self.gravity_y = -9.8
        elif self.projectile_type == 1:
            self.projectile_width, self.projectile_height = BOMB_SIZE
            self.launch_speed = BOMB_MAX_VEL
            self.gravity_y = -9.8
        elif self.projectile_type == 2:
            self.projectile_width, self.projectile_height = (5, 5)
            self.launch_speed = LASER_VEL
            self.gravity_y = 0

    def start_moving(self, launch_angle, start_x, start_y):
        self.reset_movement()
        self.launch_angle_radians = math.radians(launch_angle)
        self.vel_x = self.launch_speed * math.cos(self.launch_angle_radians)
        self.vel_y = self.launch_speed * math.sin(self.launch_angle_radians)
        self.x = start_x
        self.y = start_y
        self._clock_event = Clock.schedule_interval(self.move, 1 / FPS)

    def stop_moving(self):
        if self._clock_event:
            Clock.unschedule(self._clock_event)
            self._clock_event = None

    def reset_movement(self):
        self.stop_moving()
        self.x = -100
        self.y = -100
        self.vel_x = 0
        self.vel_y = 0

    def move(self, dt):
        self.vel = Vector(*self.vel) + Vector(*self.acceleration) * dt
        self.pos = Vector(*self.pos) + Vector(*self.vel) * dt

        print(self.vel_y)

        if self.y < 0:
            self.y = 0
            self.vel_y = 0
            self.vel_x = 0

class CannonGame(Widget):
    projectile = ObjectProperty(None)
    cannon = ObjectProperty(None)
    target = ObjectProperty(None)
    times_launched = 0

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.times_launched == 0:
                self.projectile.start_moving(self.cannon.angle, self.cannon.end_x, self.cannon.end_y)
                self.times_launched += 1
        return super().on_touch_down(touch)

class ScoreboardScreen(Screen):
    def __init__(self, **kwargs):
        super(ScoreboardScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        top_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15)
        back_button = Button(text='Back', size_hint=(1, None))
        back_button.bind(on_release=self.go_back)
        top_layout.add_widget(back_button)
        top_layout.add_widget(Label(text='Scoreboard'))
        self.layout.add_widget(top_layout)
        self.layout.add_widget(Label(text='scores'))

        self.add_widget(self.layout)

    def go_back(self, *args):
        self.manager.current = 'menu'

class NicknameScreen(Screen):
    def __init__(self, **kwargs):
        super(NicknameScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        self.layout.add_widget(Label(text='Set Your Nickname'))

        input_layout = BoxLayout(orientation='vertical', padding=50)  # Wrapper layout with padding
        self.nickname_input = TextInput(multiline=False)
        input_layout.add_widget(self.nickname_input)
        self.layout.add_widget(input_layout)

        buttons_layout = BoxLayout(orientation='horizontal')
        back_button = Button(text='Back')
        back_button.bind(on_release=self.go_back)
        buttons_layout.add_widget(back_button)
        self.layout.add_widget(buttons_layout)


        set_button = Button(text='Set Nickname')
        set_button.bind(on_release=self.set_nickname)
        buttons_layout.add_widget(set_button)

        self.add_widget(self.layout)

    def set_nickname(self, *args):
        nickname = self.nickname_input.text
        print(f"Nickname set to: {nickname}")
        # Implement any additional logic to store or use the nickname

    def go_back(self, *args):
        self.manager.current = 'menu'

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)
        self.dropdown = DropDown()

        btn_bullet = Button(text='Switch to Bullet', size_hint_y=None, height=44)
        btn_bullet.bind(on_release=self.switch_to_bullet)
        self.dropdown.add_widget(btn_bullet)

        btn_bomb = Button(text='Switch to Bomb', size_hint_y=None, height=44)
        btn_bomb.bind(on_release=self.switch_to_bomb)
        self.dropdown.add_widget(btn_bomb)

        btn_laser = Button(text='Switch to Laser', size_hint_y=None, height=44)
        btn_laser.bind(on_release=self.switch_to_laser)
        self.dropdown.add_widget(btn_laser)

        main_button = Button(text='Type of projectile', size_hint=(None, 1), width=150)
        main_button.bind(on_release=self.dropdown.open)
        self.layout.add_widget(main_button)

        best_players_button = Button(text='Best Players', size_hint=(None, 1), width=150)
        best_players_button.bind(on_release=self.show_best_players)
        self.layout.add_widget(best_players_button)

        set_nickname_button = Button(text='Set Nickname', size_hint=(None, 1), width=150)
        set_nickname_button.bind(on_release=self.show_set_nickname)
        self.layout.add_widget(set_nickname_button)

        self.main_layout = BoxLayout(orientation='vertical')
        self.main_layout.add_widget(self.layout)
        self.cannon_game = CannonGame()
        self.main_layout.add_widget(self.cannon_game)

        self.add_widget(self.main_layout)

    def toggle_single_window(self, *args):
        Window.size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.dropdown.dismiss()

    def switch_to_bullet(self, *args):
        game = self.cannon_game
        game.projectile.projectile_type = 0
        game.projectile.update_size()
        game.times_launched = 0
        self.dropdown.dismiss()

    def switch_to_bomb(self, *args):
        game = self.cannon_game
        game.projectile.projectile_type = 1
        game.projectile.update_size()
        game.times_launched = 0
        self.dropdown.dismiss()

    def switch_to_laser(self, *args):
        game = self.cannon_game
        game.projectile.projectile_type = 2
        game.projectile.update_size()
        game.times_launched = 0
        self.dropdown.dismiss()

    def show_best_players(self, *args):
        self.manager.current = 'scoreboard'

    def show_set_nickname(self, *args):
        self.manager.current = 'nickname'

class CannonApp(App):
    def build(self):
        Window.size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(ScoreboardScreen(name='scoreboard'))
        sm.add_widget(NicknameScreen(name='nickname'))
        return sm

if __name__ == '__main__':
    CannonApp().run()

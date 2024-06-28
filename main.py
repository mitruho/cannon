from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
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
        self.update_size()

    def update_size(self):
        if self.projectile_type == 0:
            self.projectile_width, self.projectile_height = BULLET_SIZE
            self.launch_speed = BULLET_MAX_VEL
        elif self.projectile_type == 1:
            self.projectile_width, self.projectile_height = BOMB_SIZE
            self.launch_speed = BOMB_MAX_VEL
        elif self.projectile_type == 2:
            self.projectile_width, self.projectile_height = (5, 5)
            self.launch_speed = LASER_VEL

    def start_moving(self, launch_angle, start_x, start_y):
        self.reset_movement()
        self.launch_angle_radians = math.radians(launch_angle)
        self.vel_x = self.launch_speed * math.cos(self.launch_angle_radians)
        self.vel_y = self.launch_speed * math.sin(self.launch_angle_radians)
        self.x = start_x
        self.y = start_y
        self.visible = True
        self._clock_event = Clock.schedule_interval(self.move, 1 / FPS)  # Update at FPS rate

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
        self.visible = False

    def move(self, dt):
        # Update velocity with acceleration (gravity)
        self.vel = Vector(*self.vel) + Vector(*self.acceleration) * dt
        # Update position with velocity
        self.pos = Vector(*self.pos) + Vector(*self.vel) * dt

        # Update the widget's position on the screen
        if self.y < 0:
            self.y = 0
            self.vel_y = 0
            self.vel_x = 0

class CannonGame(Widget):
    projectile = ObjectProperty(None)
    cannon = ObjectProperty(None)
    times_launched = 0

    def on_touch_down(self, touch):
        # Check if the touch is within the bounds of the CannonGame widget
        if self.collide_point(*touch.pos):
            if self.times_launched == 0:
                self.projectile.start_moving(self.cannon.angle, self.cannon.end_x, self.cannon.end_y)
                self.times_launched += 1
        return super().on_touch_down(touch)

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        self.dropdown = DropDown()
        
        # Button to toggle Single Window Mode
        btn_single_window = Button(text='Single Window Mode', size_hint_y=None, height=44)
        btn_single_window.bind(on_release=self.toggle_single_window)
        self.dropdown.add_widget(btn_single_window)

        # Button to switch to Bullet
        btn_bullet = Button(text='Switch to Bullet', size_hint_y=None, height=44)
        btn_bullet.bind(on_release=self.switch_to_bullet)
        self.dropdown.add_widget(btn_bullet)

        # Button to switch to Bomb
        btn_bomb = Button(text='Switch to Bomb', size_hint_y=None, height=44)
        btn_bomb.bind(on_release=self.switch_to_bomb)
        self.dropdown.add_widget(btn_bomb)

        main_button = Button(text='Menu', size_hint=(None, None), height=44)
        main_button.bind(on_release=self.dropdown.open)
        self.layout.add_widget(main_button)

        self.layout.add_widget(CannonGame())
        self.add_widget(self.layout)

    def toggle_single_window(self, *args):
        Window.size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.dropdown.dismiss()

    def switch_to_bullet(self, *args):
        game = self.layout.children[0]
        game.projectile.projectile_type = 0
        game.projectile.update_size()
        game.times_launched = 0
        self.dropdown.dismiss()

    def switch_to_bomb(self, *args):
        game = self.layout.children[0]
        game.projectile.projectile_type = 1
        game.projectile.update_size()
        game.times_launched = 0
        self.dropdown.dismiss()

class CannonApp(App):
    def build(self):
        Window.size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        return sm

if __name__ == '__main__':
    CannonApp().run()

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty
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

class Projectile(Widget):
    projectile_height = BULLET_RADIUS * 2
    projectile_width = BULLET_RADIUS * 2
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)
    vel = ReferenceListProperty(vel_x, vel_y)
    gravity_x = NumericProperty(0)
    gravity_y = NumericProperty(-9.8)
    acceleration = ReferenceListProperty(gravity_x, gravity_y)
    launch_speed = BOMB_MAX_VEL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.launch_angle_radians = 0
        self._clock_event = None
        self.visible = False
        self.x = -100  # Start off-screen
        self.y = -100  # Start off-screen

    def start_moving(self, launch_angle, start_x, start_y):
        self.launch_angle_radians = math.radians(launch_angle)
        self.vel_x = self.launch_speed * math.cos(self.launch_angle_radians)
        self.vel_y = self.launch_speed * math.sin(self.launch_angle_radians)
        self.x = start_x
        self.y = start_y
        self.visible = True
        self._clock_event = Clock.schedule_interval(self.move, 1/FPS)  # Update 60 times per second

    def stop_moving(self):
        if self._clock_event:
            Clock.unschedule(self._clock_event)
            self._clock_event = None

    def move(self, dt):
         # Update velocity with acceleration (gravity)
        self.vel = Vector(*self.vel) + Vector(*self.acceleration) * dt
        print(self.vel)
        # Update position with velocity
        self.pos = Vector(*self.pos) + Vector(*self.vel) * dt
        print(self.x)

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
        if self.times_launched == 0:
            self.projectile.start_moving(self.cannon.angle, self.cannon.end_x, self.cannon.end_y)
            self.times_launched += 1
            return super().on_touch_down(touch)

class CannonApp(App):
    def build(self):
        game = CannonGame()
        Window.size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        return game

CannonApp().run()

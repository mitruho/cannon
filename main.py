from kivy.app import App
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
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
    x_velocity = NumericProperty(0)
    y_velocity = NumericProperty(0)
    gravity = 9.81  # gravitational acceleration in m/s^2
    time = 0
    launch_speed = BULLET_MAX_VEL
    visible = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.launch_angle_radians = 0
        self._clock_event = None
        self.visible = False
        self.x = -100  # Start off-screen
        self.y = -100  # Start off-screen

    def start_moving(self, launch_angle, start_x, start_y):
        self.launch_angle_radians = math.radians(launch_angle)
        self.x_velocity = self.launch_speed * math.cos(self.launch_angle_radians)
        self.y_velocity = self.launch_speed * math.sin(self.launch_angle_radians)
        self.time = 0  # reset time
        self.x = start_x
        self.y = start_y
        self.visible = True
        self._clock_event = Clock.schedule_interval(self.move, 1/FPS)  # Update 60 times per second

    def stop_moving(self):
        if self._clock_event:
            Clock.unschedule(self._clock_event)
            self._clock_event = None

    def move(self, dt):
        self.time += dt

        # Update position based on velocity and time
        new_x = self.x_velocity * self.time
        new_y = self.y_velocity * self.time - 0.5 * (self.gravity * (self.time ** 2))

        # Check if the projectile hits the ground
        if new_y < 0:
            new_y = 0
            self.stop_moving()

        self.x += new_x
        self.y += new_y

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

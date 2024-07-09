import math
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ReferenceListProperty, NumericProperty
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
    height = NumericProperty(50)
    width = NumericProperty(50)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.x = Window.width * 4/5
        self.y = 100

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
        print(f'y velocity: {self.vel_y}, x velocity: {self.vel_x}')

        if self.parent and self.parent.check_collision(self):
            self.stop_moving()

        if self.y < 0:
            self.y = 0
            self.vel_y = 0
            self.vel_x = 0

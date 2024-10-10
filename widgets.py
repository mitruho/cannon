import math
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ReferenceListProperty, NumericProperty, BooleanProperty, ObjectProperty, StringProperty
from cannon_constants import *
from kivy.graphics import Rectangle, Color, PushMatrix, PopMatrix, Rotate
from kivy.core.image import Image as CoreImage

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
        self.x = SCREEN_WIDTH * 4/5
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
    penetration_depth = NumericProperty(BOMB_DRILL)
    texture_source = StringProperty('assets/bullet_texture.png')
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.launch_angle_radians = 0
        self._clock_event = None
        self.x = -100
        self.y = -100
        self.update_size()
        self.laser_timer = None

        with self.canvas:
            PushMatrix()
            self.rotation = Rotate()
            self.rect = Rectangle(size=self.size, pos=self.pos,
                                  texture=CoreImage(self.texture_source).texture)
            PopMatrix()

        self.bind(pos=self.update_graphics, size=self.update_graphics, angle=self.update_graphics)
        self.bind(texture_source=self.on_texture_source)

    def on_texture_source(self, instance, value):
        self.rect.texture = CoreImage(self.texture_source).texture

    def update_graphics(self, *args):
        self.canvas.clear()
        with self.canvas:
            PushMatrix()
            self.rotation = Rotate(angle=self.angle, origin=self.center)
            self.rect = Rectangle(size=self.size, pos=self.pos, texture=CoreImage(self.texture_source).texture)
            PopMatrix()


    def on_projectile_type(self, instance, value):
        self.reset_movement()
        self.update_size()

    def update_size(self):
        if self.projectile_type == 0:
            self.projectile_width, self.projectile_height = BULLET_SIZE
            self.launch_speed = BULLET_MAX_VEL
            self.gravity_y = -9.8
            self.texture_source = 'assets/bullet_texture.png'
        elif self.projectile_type == 1:
            self.projectile_width, self.projectile_height = BOMB_SIZE
            self.launch_speed = BOMB_MAX_VEL
            self.gravity_y = -9.8
            self.penetration_depth = BOMB_DRILL
            self.texture_source = 'assets/bomb_texture.png'
        elif self.projectile_type == 2:
            self.projectile_width, self.projectile_height = (20, 50)
            self.launch_speed = LASER_VEL
            self.gravity_y = 0
            self.penetration_depth = LASER_IMPULSE
            self.texture_source = 'assets/laser_texture.png'

    def update_angle(self, instance, value):
        if len(self.vel) == 2:
            velocity_vector = Vector(self.vel)
            if velocity_vector.length() > 0:
                self.angle = velocity_vector.angle(Vector(1, 0))

    def start_moving(self, launch_angle, start_x, start_y):
        self.reset_movement()
        self.reset_penetration_depth()
        self.launch_angle_radians = math.radians(launch_angle)
        self.vel_x = self.launch_speed * math.cos(self.launch_angle_radians)
        self.vel_y = self.launch_speed * math.sin(self.launch_angle_radians)
        self.x = start_x
        self.y = start_y
        self.update_angle(None, None)
        self._clock_event = Clock.schedule_interval(self.move, 1 / FPS)

        if self.projectile_type == 2:
            self.laser_timer = Clock.schedule_once(self.reset_movement, LASER_IMPULSE)

    def stop_moving(self, dt=None):
        if self._clock_event:
            Clock.unschedule(self._clock_event)
            self._clock_event = None
        if self.laser_timer:
            Clock.unschedule(self.laser_timer)
            self.laser_timer = None

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

        velocity_vector = Vector(*self.vel)
        if velocity_vector.length() > 0:
            self.angle = velocity_vector.angle(Vector(1, 0))
        if self.parent:
            if self.projectile_type in (1, 2) and not self.parent.perpetio.check_collision(self) and not (self.projectile_type == 1 and self.parent.mirror.check_collision(self)):
                self.handle_drill()
            else:
                if self.parent.check_collision(self):
                    self.reset_movement()

        if self.y < 0:
            self.y = 0
            self.vel_y = 0
            self.vel_x = 0

    def handle_drill(self):
        if self.parent.check_collision(self):
            self.penetration_depth -= 1
            if self.penetration_depth <= 0:
                self.reset_movement()

    def reset_penetration_depth(self):
        if self.projectile_type == 1:  # Bomb
            self.penetration_depth = BOMB_DRILL
        elif self.projectile_type == 2:  # Laser
            self.penetration_depth = LASER_IMPULSE


class Brick(Widget):
    destroyed = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(Brick, self).__init__(**kwargs)
        
        self.texture = CoreImage('assets/brick_texture.png').texture

        with self.canvas:
            self.rect = Rectangle(size=self.size, pos=self.pos, texture=self.texture)
        
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def destroy(self):
        self.destroyed = True
        self.canvas.clear()

class Perpetio(Widget):
    width = NumericProperty(0)
    height = NumericProperty(0)
    pos_x = NumericProperty(0)
    pos_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Perpetio, self).__init__(**kwargs)

        self.texture = CoreImage('assets/perpetio_texture.jpg').texture

        with self.canvas:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=(self.width, self.height), pos=(self.pos_x, self.pos_y), texture=self.texture)

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def check_collision(self, projectile):
        collision_detected = False
        if self.collide_widget(projectile):
            collision_detected = True
        return collision_detected

class Mirror(Widget):
    width = NumericProperty(0)
    height = NumericProperty(0)
    pos_x = NumericProperty(0)
    pos_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Mirror, self).__init__(**kwargs)

        self.texture = CoreImage('assets/mirror_texture.jpg').texture

        with self.canvas:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=(self.width, self.height), pos=(self.pos_x, self.pos_y), texture=self.texture)

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def check_collision(self, projectile):
        collision_detected = False
        if self.collide_widget(projectile):
            if projectile.projectile_type == 2:
                if projectile.y <= self.y + self.height/2:
                    projectile.vel_y = -projectile.vel_y
                else:
                    projectile.vel_x = -projectile.vel_x
            else:
                collision_detected = True
        return collision_detected
    
class Wall(Widget):
    rows = NumericProperty(15)
    columns = NumericProperty(0)
    brick_width = NumericProperty(20)
    brick_height = NumericProperty(10)
    brick_gap = NumericProperty(5)
    bricks = ObjectProperty([])

    def __init__(self, **kwargs):
        super(Wall, self).__init__(**kwargs)
        self.build_wall()

    def build_wall(self):
        self.clear_widgets()
        self.bricks = []
        for row in range(self.rows):
            for col in range(self.columns):
                brick = Brick(size=(self.brick_width, self.brick_height))
                # gap
                brick.pos = (self.x + col * (self.brick_width + self.brick_gap), 
                             self.y + row * (self.brick_height + self.brick_gap))
                self.bricks.append(brick)
                self.add_widget(brick)

    def check_collision(self, projectile):
        collision_detected = False
        for brick in self.bricks:
            if not brick.destroyed and brick.collide_widget(projectile):
                brick.destroy()
                collision_detected = True
                if projectile.projectile_type in (1, 2) :
                    projectile.penetration_depth -= 1
                    if projectile.penetration_depth <= 0:
                        return True
        return collision_detected

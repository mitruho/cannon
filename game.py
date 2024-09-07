import math
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from kivy.app import App
from widgets import *

class CannonGame(Widget):
    projectile = ObjectProperty(None)
    cannon = ObjectProperty(None)
    target = ObjectProperty(None)
    wall = ObjectProperty(None)
    attempts = 3
    score = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CannonGame, self).__init__(**kwargs)
        self.background = Image(source='background.jpg', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background, index=len(self.children))
        self.bind(size=self._update_background)
        self.wall = Wall(pos=(self.width * 5, 0))
        self.perpetio = Perpetio(pos=(self.width * 3, 0))
        self.mirror = Mirror(pos=(self.width * 3, 300), size=(0, 0)) # disabled
        self.add_widget(self.wall)
        self.add_widget(self.perpetio)
        self.add_widget(self.mirror)

    def _update_background(self, *args):
        self.background.size = self.size
        self.background.pos = self.pos

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.attempts > 0:
                self.projectile.start_moving(self.cannon.angle, self.cannon.end_x, self.cannon.end_y)
                self.attempts -= 1
                self.parent.parent.update_attempts(self.attempts)
        return super().on_touch_down(touch)

    def check_collision(self, projectile):
        if self.wall.check_collision(projectile):
            return True
        elif self.perpetio.check_collision(projectile):
            return True
        elif self.mirror.check_collision(projectile):
            return True

        projectile_center_x = projectile.x + projectile.width / 2
        projectile_center_y = projectile.y + projectile.height / 2
        projectile_radius = projectile.width / 2

        target_center_x = self.target.x + self.target.width / 2
        target_center_y = self.target.y + self.target.height / 2
        target_radius = self.target.width / 2

        distance = math.sqrt((target_center_x - projectile_center_x) ** 2 +
                             (target_center_y - projectile_center_y) ** 2)

        if distance < (projectile_radius + target_radius):
            self.on_collision()
            return True
        return False

    def levels(self, score):
        if score == 1:
            self.wall.columns = 1
        elif score == 2:
            self.wall.columns = 3
        elif score == 3:
            self.wall.columns = 6
        elif score == 4:
            self.wall.columns = 9
        elif score == 5:
            self.wall.columns = 9
            self.perpetio.height = 50
            self.perpetio.width = 10
        elif score == 6:
            self.wall.columns = 9
            self.perpetio.height = 60
            self.perpetio.width = 10
        self.wall.build_wall()

    def on_collision(self):
        print("Collision detected!")
        self.score += 1
        self.levels(self.score)
        self.reset_game(True)

    def get_score(self):
        return self.score

    def reset_game(self, victory):
        self.attempts = 3
        if not victory:
            self.score = 0
        self.projectile.reset_movement()
        self.parent.parent.update_attempts(self.attempts)
        self.levels(self.score)

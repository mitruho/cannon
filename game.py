import math
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
        # Set the position of the wall (x, y). Adjust these values as needed.
        self.wall = Wall(pos=(self.width * 5, 0))  # Example position
        self.add_widget(self.wall)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.attempts > 0:
                self.projectile.start_moving(self.cannon.angle, self.cannon.end_x, self.cannon.end_y)
                self.attempts -= 1
                self.parent.parent.update_attempts(self.attempts)  # Call the update_attempts method
        return super().on_touch_down(touch)

    def check_collision(self, projectile):
        if self.wall.check_collision(projectile):
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

    def on_collision(self):
        print("Collision detected!")
        self.score += 1
        self.wall.set_columns_based_on_score(self.score)  # Adjust the wall columns based on score
        self.reset_game(True)

    def get_score(self):
        return self.score

    def reset_game(self, victory):
        self.attempts = 3
        if not victory:
            self.score = 0
        self.projectile.reset_movement()
        self.parent.parent.update_attempts(self.attempts)
        self.wall.set_columns_based_on_score(self.score)  # Adjust the wall columns based on score

import math
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from save_manager import save_game, load_game, delete_save
from widgets import *
from levels import *

class CannonGame(Widget):
    projectile = ObjectProperty(None)
    cannon = ObjectProperty(None)
    target = ObjectProperty(None)
    wall = ObjectProperty(None)
    attempts = NumericProperty(3)
    score = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CannonGame, self).__init__(**kwargs)
        self.background = Image(source='assets/background.png', allow_stretch=False, keep_ratio=True, fit_mode="fill")
        self.add_widget(self.background, index=len(self.children))
        self.bind(size=self._update_background)
        self.wall = Wall(pos=(self.width * 5, 0))
        self.perpetio = Perpetio()
        self.mirror = Mirror()
        self.add_widget(self.wall)
        self.add_widget(self.perpetio)
        self.add_widget(self.mirror)
        Clock.schedule_interval(self.check_game_lost, 1 / 10)

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

    def on_collision(self):
        print("Collision detected!")
        self.score += 1
        levels(self, self.score)
        self.reset_game(True)

    def get_score(self):
        return self.score

    def reset_game(self, victory):
        self.attempts = 3
        if not victory:
            self.score = 0
            levels(self, 0)
        self.projectile.reset_movement()
        self.parent.parent.update_attempts(self.attempts)
        levels(self, self.score)

    def save(self, slot):
        player_data = {
            'score': self.score,
            'nickname': self.parent.parent.current_nickname  # Access nickname from MenuScreen
        }
        return save_game(slot, player_data)

    def load(self, slot):
        player_data = load_game(slot)
        if player_data:
            # Load the score and update nickname
            self.parent.parent.set_nickname(player_data['nickname'])  # Update the nickname
            
            # Set the game state based on the loaded score
            self.score = player_data['score']
            levels(self, self.score)
            
            # Confirm the load was successful
            return True
        return False

    def delete_save(self, slot):
        return delete_save(slot)

    def check_game_lost(self, dt=None):
        """
        Check if the game is lost. The game is lost if attempts are 0 and
        the projectile is outside the screen bounds.
        """
        if self.attempts == 0 and (self.projectile.vel_x < 1 or (self.projectile.x > SCREEN_WIDTH or self.projectile.y > SCREEN_HEIGHT)):
            print("Game Over: The projectile is out of bounds.")
            self.reset_game(False)

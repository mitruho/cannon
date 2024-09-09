from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from game import *
from cannon_constants import SCREEN_WIDTH, SCREEN_HEIGHT

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
        self.scores_label = Label(text='')
        self.layout.add_widget(self.scores_label)

        self.add_widget(self.layout)

    def go_back(self, *args):
        self.manager.current = 'menu'

    def update_scores(self, scores):
        self.scores_label.text = '\n'.join([f'{nickname}: {score}' for nickname, score in scores])

class HelpScreen(Screen):
    def __init__(self, **kwargs):
        super(HelpScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15)
        back_button = Button(text='Back', size_hint=(1, None))
        back_button.bind(on_release=self.go_back)

        top_layout.add_widget(back_button)
        top_layout.add_widget(Label(text='Help'))
        self.layout.add_widget(top_layout)
        
        with open('assets/help_text.txt', 'r') as file:
            help_text = file.read()
        
        help_text_label = Label(
            text=help_text,
            text_size=(SCREEN_WIDTH, None),
            halign='center')

        self.layout.add_widget(help_text_label)

        self.add_widget(self.layout)

    def go_back(self, *args):
        self.manager.current = 'menu'


class NicknameScreen(Screen):
    def __init__(self, **kwargs):
        super(NicknameScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        self.layout.add_widget(Label(text='Set Your Nickname'))

        input_layout = BoxLayout(orientation='vertical', padding=50)
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
        if not nickname:
            nickname = 'player'
        print(f"Nickname set to: {nickname}")
        self.manager.get_screen('menu').set_nickname(nickname)
        self.go_back()

    def go_back(self, *args):
        self.manager.current = 'menu'

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)

        self.attempts_layout = BoxLayout(orientation='horizontal', size_hint=(None, 1), width=30)
        self.attempts_indicators = [Label(size_hint=(None, 1), width=10, text="|", color=[0, 1, 1, 1], font_size='38sp') for _ in range(3)]
        for indicator in self.attempts_indicators:
            self.attempts_layout.add_widget(indicator)

        self.layout.add_widget(self.attempts_layout)

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

        help_button = Button(text='Help', size_hint=(None, 1), width=150)
        help_button.bind(on_release=self.show_help)
        self.layout.add_widget(help_button)

        set_nickname_button = Button(text='Set Nickname', size_hint=(None, 1), width=150)
        set_nickname_button.bind(on_release=self.show_set_nickname)
        self.layout.add_widget(set_nickname_button)

        self.nickname_label = Label(text='Nickname: player', size_hint=(None, 1), width=150)  # Nickname label
        self.layout.add_widget(self.nickname_label)

        self.score_label = Label(text='Score: 0', size_hint=(None, 1), width=150)
        self.layout.add_widget(self.score_label)

        self.main_layout = BoxLayout(orientation='vertical')
        self.main_layout.add_widget(self.layout)
        self.cannon_game = CannonGame()
        self.cannon_game.bind(score=self.update_score)
        self.main_layout.add_widget(self.cannon_game)

        self.add_widget(self.main_layout)

        self.scores = []
        self.current_nickname = "player"  # default nickname

    def update_score(self, instance, value):
        self.score_label.text = f'Score: {value}'

    def set_nickname(self, nickname):
        if self.current_nickname:
            self.scores.append((self.current_nickname, self.cannon_game.get_score()))
            self.scores = self.merge_scores(self.scores)

        self.current_nickname = nickname
        self.nickname_label.text = f'Nickname: {nickname}'
        self.cannon_game.reset_game(False)
        self.update_score(self, 0)
        self.update_scoreboard()

    def merge_scores(self, scores):
        merged_scores = {}
        for nickname, score in scores:
            if nickname in merged_scores:
                merged_scores[nickname] = max(merged_scores[nickname], score)
            else:
                merged_scores[nickname] = score
        return list(merged_scores.items())
    
    def update_attempts(self, attempts):
        for i in range(3):
            if i < attempts:
                self.attempts_indicators[i].color = [0, 1, 1, 1]
            else:
                self.attempts_indicators[i].color = [0.5, 0.5, 0.5, 1]

    def update_scoreboard(self):
        self.manager.get_screen('scoreboard').update_scores(self.scores)

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

    def show_help(self, *args):
        self.manager.current = 'help'

    def show_set_nickname(self, *args):
        self.manager.current = 'nickname'

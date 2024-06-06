from kivy.app import App
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty

class MainUI(BoxLayout):
    pass

class ButtonStack(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        buttons_info = [
            ('Bullet', (75, 50)),
            ('Bombshell', (75, 50)),
            ('Laser', (75, 50)),
            ('Restart', (100, 50)),
            ('Hall of Fame', (100, 50)),
            ('Help', (100, 50)),
        ]
        
        for text, size in buttons_info:
            self.add_widget(self.create_button(text, size))

    def create_button(self, text, size):
        return Button(text=text, size_hint=(None, None), size=(dp(size[0]), dp(size[1])))

class CannonWidget(Widget):
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CannonWidget, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        mouse_x, mouse_y = args[1]
        dx = mouse_x - self.x
        dy = mouse_y - (self.y + self.height / 2)
        angle = Vector(dx, dy).angle(Vector(1, 0))
        self.angle = max(0, min(90, angle))

class CannonApp(App):
    pass



CannonApp().run()
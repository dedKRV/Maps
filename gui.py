import arcade
import sys
import requests
from arcade import get_image
from arcade.gui import UIManager, UIFlatButton, UIInputText
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from pyglet.event import EVENT_HANDLE_STATE

from geocode_coords import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Request"
MAP_FILE = 'map.png'


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture('map.png')

    def update(self):
        self.texture = arcade.load_texture('map.png')


class MyGUIWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.GRAY)
        self.player = Player()
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2
        self.player.width = 500
        self.player.height = 350
        self.all_sprites = arcade.SpriteList()
        self.all_sprites.append(self.player)

        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()

        # Layout для организации — как полки в шкафу
        self.anchor_layout = UIAnchorLayout(y=SCREEN_HEIGHT // 3)  # Центрирует виджеты
        self.box_layout = UIBoxLayout(vertical=False, space_between=10)
        self.setup_widgets()
        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

    def setup_widgets(self):
        # Здесь добавим ВСЕ виджеты — по порядку!
        self.input_text = UIInputText(x=0, y=0, width=200, height=50, text_color=arcade.color.WHITE,
                                      border_color=arcade.color.BLACK,
                                      fon_size=14, text='')
        self.box_layout.add(self.input_text)
        flat_button = UIFlatButton(width=200, height=50, color=arcade.color.BLUE,
                                   text='')
        flat_button.on_click = self.on_button_click
        self.box_layout.add(flat_button)

    def on_button_click(self, event):
        self.ll, self.span = geocode_coords(self.input_text.text)
        get_image(self.ll, self.span)
        self.player.update()

    def on_draw(self):
        self.clear()
        self.all_sprites.draw()
        self.manager.draw()

    def on_key_press(self, key, modifires):
        if key == arcade.key.PAGEUP:
            s1, s2 = map(float, self.span.split(","))
            s1 *= 1.05
            s2 *= 1.05
            self.span = f"{s1},{s2}"
            get_image(self.ll, self.span)
            self.player.update()
        if key == arcade.key.PAGEDOWN:
            s1, s2 = map(float, self.span.split(","))
            s1 *= 0.95
            s2 *= 0.95
            self.span = f"{s1},{s2}"
            get_image(self.ll, self.span)
            self.player.update()
        if key == arcade.key.RIGHT:
            s1, s2 = map(float, self.ll.split(","))
            s1 += 5
            self.ll = f"{s1},{s2}"
            get_image(self.ll, self.span)
            self.player.update()
        if key == arcade.key.LEFT:
            s1, s2 = map(float, self.ll.split(","))
            s1 -= 5
            self.ll = f"{s1},{s2}"
            get_image(self.ll, self.span)
            self.player.update()
        if key == arcade.key.UP:
            s1, s2 = map(float, self.ll.split(","))
            s2 += 5
            self.ll = f"{s1},{s2}"
            get_image(self.ll, self.span)
            self.player.update()
        if key == arcade.key.DOWN:
            s1, s2 = map(float, self.ll.split(","))
            s2 -= 5
            self.ll = f"{s1},{s2}"
            get_image(self.ll, self.span)
            self.player.update()



def get_image(ll, span):
    server_address = 'https://static-maps.yandex.ru/v1?'
    api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
    ll_spn = f'll={ll}&spn={span}'
    # Готовим запрос.

    map_request = f"{server_address}{ll_spn}&apikey={api_key}"
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    with open(MAP_FILE, "wb") as file:
        file.write(response.content)


def setup_game(width=800, height=600, title="Background Color"):
    game = MyGUIWindow(width, height, title)
    return game

def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()

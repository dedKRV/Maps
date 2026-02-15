import arcade
import sys
import requests
from arcade.gui import UIManager, UIFlatButton, UIInputText
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout

from geocode_coords import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "requests"
MAP_FILE = 'map.png'


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.show_black_screen = False
        try:
            self.map_texture = arcade.load_texture('map.png')
            self.black_texture = arcade.load_texture('black_screen.png')
            self.texture = self.map_texture
        except:
            self.texture = None

    def update(self):
        """Обновляет текстуру карты"""
        if self.show_black_screen:
            # Показываем чёрный экран
            self.texture = self.black_texture
        else:
            # Перезагружаем карту
            self.map_texture = arcade.load_texture('map.png')
            self.texture = self.map_texture


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
        self.ll = None
        self.span = None
        self.marker_coords = None
        self.manager = UIManager()
        self.manager.enable()
        self.anchor_layout = UIAnchorLayout(y=SCREEN_HEIGHT // 3)
        self.box_layout = UIBoxLayout(vertical=False, space_between=10)
        self.setup_widgets()
        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

    def setup_widgets(self):
        # Здесь добавим ВСЕ виджеты — по порядку!
        # Поле ввода для поиска
        self.input_text = UIInputText(
            x=0, y=0, width=200, height=50,
            text_color=arcade.color.WHITE,
            border_color=arcade.color.BLACK,
            font_size=14,
            text=''
        )
        self.box_layout.add(self.input_text)

        # Кнопка "Искать"
        search_button = UIFlatButton(
            width=200, height=50,
            color=arcade.color.BLUE,
            text='Искать'
        )
        search_button.on_click = self.on_search_click
        self.box_layout.add(search_button)

        # Кнопка "Сброс"
        reset_button = UIFlatButton(
            width=200, height=50,
            color=arcade.color.RED,
            text='Сброс'
        )
        reset_button.on_click = self.on_reset_click
        self.box_layout.add(reset_button)

    def on_search_click(self, event):
        """Обработка кнопки поиска"""
        search_query = self.input_text.text.strip()
        if not search_query:
            return

        # Получаем координаты объекта
        result = geocode_coords(search_query)
        if result:
            self.ll, self.span = result
            self.marker_coords = self.ll
            get_image(self.ll, self.span, self.marker_coords)

            # Выключаем чёрный экран
            self.player.show_black_screen = False
            self.player.update()

    def on_reset_click(self, event):
        """Обработка кнопки сброса"""
        self.ll = None
        self.span = None
        self.marker_coords = None
        self.player.show_black_screen = True
        self.player.update()

    def on_draw(self):
        self.clear()
        self.all_sprites.draw()
        self.manager.draw()

    def on_key_press(self, key, modifiers):
        if self.ll is None or self.span is None:
            return

        # Поиск по Enter
        if key == arcade.key.ENTER:
            self.on_search_click(None)
            return
        self.player.show_black_screen = False
        if key == arcade.key.PAGEUP:
            s1, s2 = map(float, self.span.split(","))
            s1 *= 1.05
            s2 *= 1.05
            self.span = f"{s1},{s2}"
            get_image(self.ll, self.span, self.marker_coords)
            self.player.update()
        elif key == arcade.key.PAGEDOWN:
            s1, s2 = map(float, self.span.split(","))
            s1 *= 0.95
            s2 *= 0.95
            self.span = f"{s1},{s2}"
            get_image(self.ll, self.span, self.marker_coords)
            self.player.update()
        elif key == arcade.key.RIGHT:
            s1, s2 = map(float, self.ll.split(","))
            s1 += 5
            self.ll = f"{s1},{s2}"
            get_image(self.ll, self.span, self.marker_coords)
            self.player.update()
        elif key == arcade.key.LEFT:
            s1, s2 = map(float, self.ll.split(","))
            s1 -= 5
            self.ll = f"{s1},{s2}"
            get_image(self.ll, self.span, self.marker_coords)
            self.player.update()
        elif key == arcade.key.UP:
            s1, s2 = map(float, self.ll.split(","))
            s2 += 5
            self.ll = f"{s1},{s2}"
            get_image(self.ll, self.span, self.marker_coords)
            self.player.update()
        elif key == arcade.key.DOWN:
            s1, s2 = map(float, self.ll.split(","))
            s2 -= 5
            self.ll = f"{s1},{s2}"
            get_image(self.ll, self.span, self.marker_coords)
            self.player.update()


def get_image(ll, span, marker_coords=None):
    server_address = 'https://static-maps.yandex.ru/v1?'
    api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
    ll_spn = f'll={ll}&spn={span}'
    pt_param = ''
    if marker_coords:
        pt_param = f'&pt={marker_coords},pm2rdm'
    map_request = f"{server_address}{ll_spn}{pt_param}&apikey={api_key}"
    response = requests.get(map_request)
    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
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
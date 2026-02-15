import arcade
import sys
import requests
import pygame
from arcade.gui import UIManager, UIFlatButton, UIInputText, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from arcade.gui.widgets.toggle import UITextureToggle
from geocode_coords import geocode_coords, reverse_geocode

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Map Search"
MAP_FILE = 'map.png'


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.show_black_screen = False
        try:
            self.map_texture = arcade.load_texture('map.png')
            self.black_texture = arcade.load_texture('map0.png')
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
        arcade.set_background_color(arcade.color.DUTCH_WHITE)
        pygame.init()
        self.player = Player()
        self.player.center_x = SCREEN_WIDTH // 2 + 130
        self.player.center_y = SCREEN_HEIGHT // 2 + 130
        self.player.width = 700
        self.player.height = 500
        self.all_sprites = arcade.SpriteList()
        self.all_sprites.append(self.player)
        self.ll = None
        self.span = None
        self.marker_coords = None
        self.full_address = None
        self.postal_code = None
        self.show_postal_code = False
        self.map_theme = 'light'
        self.last_search_query = ""

        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()
        self.v_box = UIBoxLayout(vertical=True, space_between=5)
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)
        self.checkbox_layout = UIBoxLayout(vertical=False, space_between=10)
        self.address_layout = UIBoxLayout(vertical=False, space_between=0)

        self.theme_layout = UIBoxLayout(vertical=True, space_between=5)

        self.setup_widgets()
        self.setup_theme_widgets()

        self.v_box.add(self.box_layout)
        self.v_box.add(self.checkbox_layout)
        self.anchor_layout = UIAnchorLayout()
        self.anchor_layout.add(
            child=self.v_box,
            anchor_x="left",
            anchor_y="top",
            align_y=-20,
            align_x=20
        )

        self.address_anchor = UIAnchorLayout()
        self.address_anchor.add(
            child=self.address_layout,
            anchor_x="left",
            anchor_y="bottom",
            align_y=300,
            align_x=45
        )

        self.theme_anchor = UIAnchorLayout()
        self.theme_anchor.add(
            child=self.theme_layout,
            anchor_x="left",
            anchor_y="bottom",
            align_y=20,
            align_x=45
        )

        self.manager.add(self.anchor_layout)
        self.manager.add(self.address_anchor)
        self.manager.add(self.theme_anchor)

        arcade.schedule_once(self.delayed_reset, 0.01)

    def delayed_reset(self, delta_time):
        """Вызывает сброс после небольшой задержки"""
        self.on_reset_click(None)

    def setup_widgets(self):
        # Поле ввода для поиска
        self.input_text = UIInputText(
            x=0, y=0, width=250, height=50,
            text_color=arcade.color.BLACK_OLIVE,
            border_color=arcade.color.BLACK_OLIVE,
            font_size=14,
            text=''
        )
        self.box_layout.add(self.input_text)

        # Кнопка "Искать"
        search_button = UIFlatButton(
            width=250, height=50,
            color=arcade.color.BLUE,
            text='Искать'
        )
        search_button.on_click = self.on_search_click
        self.box_layout.add(search_button)

        # Кнопка "Сброс"
        reset_button = UIFlatButton(
            width=250, height=50,
            color=arcade.color.RED,
            text='Сброс'
        )
        reset_button.on_click = self.on_reset_click
        self.box_layout.add(reset_button)

        # Чекбокс для почтового индекса
        self.postal_checkbox = UIFlatButton(
            width=200, height=50,
            color=arcade.color.DARK_GRAY,
            text='☐ Показать индекс'
        )
        self.postal_checkbox.on_click = self.on_toggle_postal_code
        self.checkbox_layout.add(self.postal_checkbox)

        self.address_label = UILabel(
            text='',
            width=600,
            height=800,
            font_size=14,
            text_color=arcade.color.BLACK_OLIVE,
            multiline=True
        )
        self.address_layout.add(self.address_label)

    def setup_theme_widgets(self):
        """Создает виджеты для переключения темы карты"""
        # Кнопка для светлой темы
        self.light_theme_button = UIFlatButton(
            width=200, height=50,
            color=arcade.color.LIGHT_GRAY if self.map_theme == 'light' else arcade.color.DARK_GRAY,
            text='Светлая тема'
        )
        self.light_theme_button.on_click = self.on_light_theme_click
        self.theme_layout.add(self.light_theme_button)

        # Кнопка для темной темы
        self.dark_theme_button = UIFlatButton(
            width=200, height=50,
            color=arcade.color.LIGHT_GRAY if self.map_theme == 'dark' else arcade.color.DARK_GRAY,
            text='Темная тема'
        )
        self.dark_theme_button.on_click = self.on_dark_theme_click
        self.theme_layout.add(self.dark_theme_button)

    def update_theme_buttons(self):
        """Обновляет цвета кнопок в зависимости от выбранной темы"""
        if self.map_theme == 'light':
            self.light_theme_button.color = arcade.color.LIGHT_GRAY
            self.dark_theme_button.color = arcade.color.DARK_GRAY
        else:
            self.light_theme_button.color = arcade.color.DARK_GRAY
            self.dark_theme_button.color = arcade.color.LIGHT_GRAY

    def on_light_theme_click(self, event):
        """Обработка выбора светлой темы"""
        if self.map_theme != 'light':
            self.map_theme = 'light'
            self.update_theme_buttons()
            self.refresh_map()

    def on_dark_theme_click(self, event):
        """Обработка выбора темной темы"""
        if self.map_theme != 'dark':
            self.map_theme = 'dark'
            self.update_theme_buttons()
            self.refresh_map()

    def refresh_map(self):
        """Обновляет карту с текущей темой"""
        if self.ll and self.span:
            get_image(self.ll, self.span, self.marker_coords, self.map_theme)
            self.player.update()

    def check_and_search(self):
        """Проверяет изменение текста и выполняет поиск"""
        current_query = self.input_text.text.strip()

        # Если запрос изменился
        if current_query != self.last_search_query:
            self.last_search_query = current_query

            if not current_query:
                self.on_reset_click(None)
            else:
                result = geocode_coords(current_query)
                if result:
                    self.ll, self.span, self.full_address, self.postal_code = result
                    self.marker_coords = self.ll
                    get_image(self.ll, self.span, self.marker_coords, self.map_theme)

                    self.update_address_display()
                    self.player.show_black_screen = False
                    self.player.update()

    def on_search_click(self, event):
        """Обработка кнопки Искать"""
        self.check_and_search()

    def on_toggle_postal_code(self, event):
        """Обработка показа индекса"""
        self.show_postal_code = not self.show_postal_code
        if self.show_postal_code:
            self.postal_checkbox.text = '☑ Показать индекс'
        else:
            self.postal_checkbox.text = '☐ Показать индекс'
        self.update_address_display()

    def update_address_display(self):
        """Обновляет отображение адреса и индекса"""
        if self.full_address:
            if self.show_postal_code and self.postal_code:
                self.address_label.text = f"{self.full_address}    {self.postal_code}"
            else:
                self.address_label.text = self.full_address
        else:
            self.address_label.text = ''

    def on_reset_click(self, event):
        """Обработка кнопки сброс"""
        self.ll = None
        self.span = None
        self.marker_coords = None
        self.full_address = None
        self.postal_code = None
        self.address_label.text = ''
        self.player.show_black_screen = True
        self.player.update()
        self.input_text.text = ''
        self.last_search_query = ''

    def on_draw(self):
        self.clear()
        self.all_sprites.draw()
        self.manager.draw()

    def on_key_press(self, key, modifiers):
        # Обработка специальных клавиш (стрелки, PageUp/PageDown) для навигации по карте
        if self.ll is not None and self.span is not None:
            if key == arcade.key.PAGEUP:
                s1, s2 = map(float, self.span.split(","))
                s1 *= 1.05
                s2 *= 1.05
                self.span = f"{s1},{s2}"
                get_image(self.ll, self.span, self.marker_coords, self.map_theme)
                self.player.update()
                self.player.show_black_screen = False
                return
            elif key == arcade.key.PAGEDOWN:
                s1, s2 = map(float, self.span.split(","))
                s1 *= 0.95
                s2 *= 0.95
                self.span = f"{s1},{s2}"
                get_image(self.ll, self.span, self.marker_coords, self.map_theme)
                self.player.update()
                self.player.show_black_screen = False
                return
            elif key == arcade.key.RIGHT:
                s1, s2 = map(float, self.ll.split(","))
                s1 += 5
                self.ll = f"{s1},{s2}"
                get_image(self.ll, self.span, self.marker_coords, self.map_theme)
                self.player.update()
                self.player.show_black_screen = False
                return
            elif key == arcade.key.LEFT:
                s1, s2 = map(float, self.ll.split(","))
                s1 -= 5
                self.ll = f"{s1},{s2}"
                get_image(self.ll, self.span, self.marker_coords, self.map_theme)
                self.player.update()
                self.player.show_black_screen = False
                return
            elif key == arcade.key.UP:
                s1, s2 = map(float, self.ll.split(","))
                s2 += 5
                self.ll = f"{s1},{s2}"
                get_image(self.ll, self.span, self.marker_coords, self.map_theme)
                self.player.update()
                self.player.show_black_screen = False
                return
            elif key == arcade.key.DOWN:
                s1, s2 = map(float, self.ll.split(","))
                s2 -= 5
                self.ll = f"{s1},{s2}"
                get_image(self.ll, self.span, self.marker_coords, self.map_theme)
                self.player.update()
                self.player.show_black_screen = False
                return

        arcade.unschedule(self.delayed_search)
        arcade.schedule_once(self.delayed_search, 0.3)

    def delayed_search(self, delta_time):
        """Поиск с небольшой задержкой после нажатия клавиши"""
        arcade.unschedule(self.delayed_search)
        self.check_and_search()

    def on_mouse_press(self, x, y, button, modifiers):
        pygame_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (x, self.height - y), 'button': button})
        if button == 1:
            self.map_click(x, y)

    def map_click(self, x, y):
        map_left = self.player.center_x - self.player.width / 2
        map_right = self.player.center_x + self.player.width / 2
        map_bottom = self.player.center_y - self.player.height / 2
        map_top = self.player.center_y + self.player.height / 2
        if (map_left <= x <= map_right and map_bottom <= y <= map_top):
            if self.ll and self.span:
                rel_x = (x - map_left) / self.player.width
                rel_y = (y - map_bottom) / self.player.height
                center_lon, center_lat = map(float, self.ll.split(','))
                span_lon, span_lat = map(float, self.span.split(','))
                click_lon = center_lon + (rel_x - 0.5) * span_lon
                click_lat = center_lat + (rel_y - 0.5) * span_lat
                result = reverse_geocode(click_lon, click_lat)
                if result:
                    coords, span_new, full_address, postal_code = result
                    self.marker_coords = coords
                    self.full_address = full_address
                    self.postal_code = postal_code
                    get_image(self.ll, self.span, self.marker_coords, self.map_theme)
                    self.update_address_display()
                    self.player.show_black_screen = False
                    self.player.update()


def get_image(ll, span, marker_coords=None, theme='light'):
    server_address = 'https://static-maps.yandex.ru/v1?'
    api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'

    # Определяем параметры темы
    if theme == 'dark':
        theme_param = '&theme=dark'
    else:
        theme_param = '&theme=light'
    ll_spn = f'll={ll}&spn={span}'
    pt_param = ''
    if marker_coords:
        pt_param = f'&pt={marker_coords},pm2rdm'
    # Добавляем параметр темы к запросу
    map_request = f"{server_address}{ll_spn}{pt_param}{theme_param}&apikey={api_key}"

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
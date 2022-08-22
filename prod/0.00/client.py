import random
import socket
import subprocess
import time
import requests
from screeninfo import get_monitors
import pygame
import json
import Buttons
import threading
from io import BytesIO

size = [get_monitors()[0].width, get_monitors()[0].height]
clock = pygame.time.Clock()
run = True
sock = None
mouse_left_press = False
key_esc = False
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode(size, pygame.NOFRAME)
room_screen = pygame.display.set_mode(size, pygame.NOFRAME)
pygame.display.set_caption('client')
KILLED_SHIP = (60, 60, 60)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
theme = 0
version = 0


def StartGame():
    global info_sound, killed_sound, missed_sound, wounded_sound
    info_sound = pygame.mixer.Sound(
        BytesIO(requests.get('https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/info.wav?raw=true').content))
    killed_sound = pygame.mixer.Sound(BytesIO(
        requests.get('https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/killed.ogg?raw=true').content))
    missed_sound = pygame.mixer.Sound(BytesIO(
        requests.get('https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/missed.ogg?raw=true').content))
    wounded_sound = pygame.mixer.Sound(BytesIO(
        requests.get('https://github.com/AlexKim0710/OceanShipsWar/blob/main/asets/wounded.ogg?raw=true').content))


threading.Thread(target=StartGame).start()

bsize = size[0] // 27.428571428571427
ships_wh = int(bsize // 7)
left_margin, upper_margin = (size[0] // 2 - bsize * 5), (size[1] // 2 - bsize * 5)
font = pygame.font.SysFont('notosans', int(bsize / 1.5))
infoSurface = pygame.Surface((size[0] // 2 // 1.5, upper_margin // 2), pygame.SRCALPHA)
blocks_pos = []
blocks_corns = []
build_ship = False
build_y = False
ship = 0
doSelect = True
ships = {1: {}, 2: {}, 3: {}, 4: {}}
ships_env = []
quadro_ship = 1
trio_ship = 2
duo_ship = 3
solo_ship = 4
great_build = False
ERRORS = []
legitBuild = True
block_block_num = False
quadro_ship_rect = None
quadro_ship_env = None
# pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
Draw_select = True
BUILD = True
killed_enemy = False
is_adm = None
room = True
create_game = False
join_game = False
settings = False
game = False
win = False
Enemy_die = []
Enemy_die_block = []
Enemy_die_block_rect = []
My_selected_blocks = []
My_selected_blocks_pos = []
My_ships_blocks = {1: {}, 2: {}, 3: {}, 4: {}}
solo, duo, trio, quadro = 0, 0, 0, 0
send_data = {'ships': {1: {}, 2: {}, 3: {}, 4: {}},
             'selects': My_selected_blocks,
             'die': {'blocks': [], 'ships': []},
             'move': 'build',
             'pass': False,
             'event': []}
input_data = {'ships': {1: {}, 2: {}, 3: {}, 4: {}},
              'selects': My_selected_blocks,
              'die': {'blocks': {}, 'ships': {}},
              'move': 'build',
              'pass': False,
              'event': []}
GameSettings = {'Sound': True,
                'NotificationSound': True,
                'NotificationSoundVol': 0.1,
                'GameSound': True,
                'GameSoundVol': 0.1,
                'GameLanguage': 'rus',
                'my socket': ['', 0],
                'enemy socket': ['', 0]}
SettingsButtons = pygame.sprite.Group()
Switches = pygame.sprite.Group()
Lists = pygame.sprite.Group()
Slides = pygame.sprite.Group()
settings_upper_margin = 0.2
settings_wheel = settings_upper_margin
sprites = pygame.sprite.Group()
SystemButtons = pygame.sprite.Group()
CreateGameButtons = pygame.sprite.Group()
JoinGameButtons = pygame.sprite.Group()

for x in range(10):
    for y in range(10):
        blocks_pos.append([[left_margin + x * bsize, upper_margin + y * bsize],
                           [left_margin + ((x + 1) * bsize), upper_margin + ((y + 1) * bsize)]])

        blocks_corns.append([left_margin + x * bsize, upper_margin + y * bsize])


def re_lang(lang='rus'):
    global GameLanguage
    if lang == 'rus':
        GameLanguage = {'start game': 'Создать игру',
                        'join game': 'Присоеденится к игре',
                        'settings': 'Настройки',
                        'theme light': 'Яркая',
                        'theme dark': 'Тёмная',
                        'Settings Sound': 'Звук',
                        'Settings Game Sound': 'Звуки игры',
                        'Settings Notification Sound': 'Звуки уведомлений',
                        'Settings Sound Slide': 'Громкость',
                        'Settings Language': 'Язык',
                        'Exit': 'Выход',
                        'version': f'Версия {version}'}
    else:
        GameLanguage = {'start game': 'Create game',
                        'join game': 'Join to game',
                        'settings': 'Settings',
                        'theme light': 'Light',
                        'theme dark': 'Dark',
                        'Settings Sound': 'Sound',
                        'Settings Game Sound': 'Game Sound',
                        'Settings Notification Sound': 'Notifications Sound',
                        'Settings Sound Slide': 'Volume',
                        'Settings Language': 'Language',
                        'Exit': 'Exit',
                        'version': f'Version {version}'}


re_lang()


def get_rect_ship(var):
    bl = var
    if bl[0][0] != bl[1][0]:
        posit_s = get_pos_block(bl[0])
        rc = [posit_s[0],
              posit_s[1],
              bsize * abs(bl[1][0] + 1 - bl[0][0]),
              bsize
              ]
    elif bl[0][1] != bl[1][1]:
        posit_s = get_pos_block(bl[0])
        rc = [posit_s[0],
              posit_s[1],
              bsize,
              bsize * abs(bl[1][1] + 1 - bl[0][1])
              ]
    elif bl[0][0] == bl[1][0] and bl[0][1] == bl[1][1]:
        posit_s = get_pos_block(bl[0])
        rc = [posit_s[0],
              posit_s[1],
              bsize,
              bsize
              ]
    return rc


def get_pos_block(block_cords):
    if block_cords:
        return blocks_corns[int(str(block_cords[0]) + str(block_cords[1]))]
    else:
        return False


def get_cords_block(block_pos):
    if block_pos in blocks_corns:
        for n, bl in enumerate(blocks_corns):
            if bl == block_pos:
                return [n // 10, n % 10]
    else:
        return


def re_theme():
    global ButtonAdm, ButtonClient, ButtonSettings, ButtonTheme, EscButton, SettingsMainLabel, RoomQuit, \
        CreateGameMainLabel, TextInputCr, CreateGameWaitUser, JoinGameMainLabel, JoinGameWaitUser, BACKGROUND, LINES, KILLED_SHIP, Update
    if theme:
        KILLED_SHIP = (200, 200, 200)
        LINES = (24, 24, 24)
        BACKGROUND = (227, 227, 227)
        Update = Buttons.button((-1, size[1] - bsize // 2, bsize * 2, bsize // 2), str(GameLanguage['version']),
                                (177, 220, 237),
                                (255, 255, 255), (64, 64, 64), (255, 255, 255), (127, 127, 127), (0, 0, 0))
        TextInputCr = Buttons.TextInput(
            (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.2,
             size[1] * 0.1), BACKGROUND, (0, 255, 255), (0, 0, 0), 'create', '192.168.1.1',
            GameSettings['my socket'][0])
        TextInputJn = Buttons.TextInput(
            (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.2,
             size[1] * 0.1), BACKGROUND, (0, 255, 255), (0, 0, 0), 'join', '192.168.1.1',
            GameSettings['my socket'][0])
        CreateGameWaitUser = Buttons.label(
            (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.95 - size[1] * 0.1 // 2, size[0] * 0.2,
             size[1] * 0.1), f'Ждем соперника... Ваш адрес: {GameSettings["my socket"][0]}', BACKGROUND, (0, 255, 255))
        JoinGameWaitUser = Buttons.label(
            (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.95 - size[1] * 0.1 // 2, size[0] * 0.2,
             size[1] * 0.1), f'Ждем соперника... Адрес будущего соперника: {GameSettings["my socket"][0]}', BACKGROUND,
            (255, 0, 255))
        SettingsMainLabel = Buttons.label((size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                                          GameLanguage['settings'], BACKGROUND, LINES)
        CreateGameMainLabel = Buttons.label((size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                                            GameLanguage['start game'], BACKGROUND, LINES)
        JoinGameMainLabel = Buttons.label((size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                                          GameLanguage['join game'], BACKGROUND, LINES)
        RoomQuit = Buttons.button((size[0] - bsize + 1, -1, bsize, bsize),
                                  GameLanguage['Exit'], (177, 220, 237), (255, 255, 255), (64, 64, 64), (255, 255, 255),
                                  (127, 127, 127), (0, 0, 0))
        EscButton = Buttons.button((-1, -1, (bsize + bsize * 0.5) // 2, bsize // 2), 'ESC', (177, 220, 237),
                                   (255, 255, 255), (64, 64, 64), (255, 255, 255), (127, 127, 127), (0, 0, 0))
        ButtonAdm = Buttons.button(
            (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.3 - size[1] * 0.1, size[0] * 0.16,
             size[1] * 0.1),
            GameLanguage['start game'],
            (177, 220, 237), (255, 255, 255), (64, 64, 64), (255, 255, 255), (127, 127, 127), (0, 0, 0))
        ButtonClient = Buttons.button(
            (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.16,
             size[1] * 0.1),
            GameLanguage['join game'],
            (177, 220, 237), (255, 255, 255), (64, 64, 64), (255, 255, 255), (127, 127, 127), (0, 0, 0))
        ButtonSettings = Buttons.button(
            (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.7 - size[1] * 0.1, size[0] * 0.16,
             size[1] * 0.1),
            GameLanguage['settings'],
            (177, 220, 237), (255, 255, 255), (64, 64, 64), (255, 255, 255), (127, 127, 127), (0, 0, 0))
        ButtonTheme = Buttons.button((size[0] - bsize - bsize // 2, size[1] - bsize - bsize // 2, bsize, bsize),
                                     GameLanguage['theme light'], (177, 220, 237), (255, 255, 255), (64, 64, 64),
                                     (255, 255, 255), (127, 127, 127), (0, 0, 0))
    else:
        KILLED_SHIP = (60, 60, 60)
        LINES = (255, 255, 255)
        BACKGROUND = (24, 24, 24)
        TextInputCr = Buttons.TextInput(
            (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.2,
             size[1] * 0.1), BACKGROUND, (0, 0, 100), (255, 255, 255), 'create',
            '192.168.1.1', GameSettings['my socket'][0])
        TextInputJn = Buttons.TextInput(
            (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.2,
             size[1] * 0.1), BACKGROUND, (0, 0, 100), (255, 255, 255), 'join',
            '192.168.1.1', GameSettings['my socket'][0])
        CreateGameWaitUser = Buttons.label(
            (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.95 - size[1] * 0.1 // 2, size[0] * 0.2,
             size[1] * 0.1), f'Ждем соперника... Ваш адрес: {GameSettings["my socket"][0]}', BACKGROUND, (0, 255, 255))
        JoinGameWaitUser = Buttons.label(
            (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.95 - size[1] * 0.1 // 2, size[0] * 0.2,
             size[1] * 0.1), f'Ждем соперника... Адрес будущего соперника: {GameSettings["my socket"][0]}', BACKGROUND,
            (255, 0, 255))
        SettingsMainLabel = Buttons.label((size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                                          GameLanguage['settings'], BACKGROUND, LINES)
        CreateGameMainLabel = Buttons.label((size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                                            GameLanguage['start game'], BACKGROUND, LINES)
        JoinGameMainLabel = Buttons.label((size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                                          GameLanguage['join game'], BACKGROUND, LINES)
        RoomQuit = Buttons.button((size[0] - bsize + 1, -1, bsize, bsize),
                                  GameLanguage['Exit'], (255, 255, 255), (0, 0, 0),
                                  (255, 255, 255), (255, 255, 255), (127, 127, 127), (0, 0, 0))
        Update = Buttons.button((-1, size[1] - bsize // 2, bsize * 2, bsize // 2), str(GameLanguage['version']),
                                (255, 255, 255),
                                (0, 0, 0),
                                (255, 255, 255), (255, 255, 255), (127, 127, 127), (0, 0, 0))
        EscButton = Buttons.button((-1, -1, (bsize + bsize * 0.5) // 2, bsize // 2), 'ESC', (255, 255, 255), (0, 0, 0),
                                   (255, 255, 255), (255, 255, 255), (127, 127, 127), (0, 0, 0))
        ButtonClient = Buttons.button(
            (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.16,
             size[1] * 0.1),
            GameLanguage['join game'],
            (255, 255, 255), (0, 0, 0), (255, 255, 255), (255, 255, 255), (127, 127, 127), (0, 0, 0))
        ButtonSettings = Buttons.button(
            (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.7 - size[1] * 0.1, size[0] * 0.16,
             size[1] * 0.1),
            GameLanguage['settings'],
            (255, 255, 255), (0, 0, 0), (255, 255, 255), (255, 255, 255), (127, 127, 127), (0, 0, 0))
        ButtonAdm = Buttons.button(
            (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.3 - size[1] * 0.1, size[0] * 0.16,
             size[1] * 0.1),
            GameLanguage['start game'], (255, 255, 255), (0, 0, 0), (255, 255, 255), (255, 255, 255), (127, 127, 127),
            (0, 0, 0))
        ButtonTheme = Buttons.button((size[0] - bsize - bsize // 2, size[1] - bsize - bsize // 2, bsize, bsize),
                                     GameLanguage['theme dark'], (255, 255, 255), (0, 0, 0), (255, 255, 255),
                                     (255, 255, 255),
                                     (127, 127, 127), (0, 0, 0))
    sprites.empty()
    SystemButtons.empty()
    CreateGameButtons.empty()
    JoinGameButtons.empty()
    SystemButtons.add(EscButton, SettingsMainLabel, CreateGameMainLabel, CreateGameWaitUser, JoinGameMainLabel,
                      JoinGameWaitUser)
    CreateGameButtons.add(TextInputCr)
    JoinGameButtons.add(TextInputJn)
    sprites.add(ButtonAdm, ButtonClient, ButtonSettings, ButtonTheme, RoomQuit, Update)


re_theme()


def draw_ship_count(s, d, t, q):
    mid = [size[0] // 2 + size[0] // 2 // 1.5, size[1] // 2 - size[1] // 2 // 1.5]
    if q:
        q_color = LINES
    else:
        q_color = KILLED_SHIP

    for l in range(4):
        pygame.draw.rect(screen, q_color, (mid[0] + l * bsize // 2, mid[1], bsize // 2, bsize // 2), 1)
    if t == 2:
        for l in range(7):
            if l == 3:
                t_color = BACKGROUND
            else:
                t_color = LINES
            pygame.draw.rect(screen, t_color, (mid[0] + l * bsize // 2, mid[1] + bsize, bsize // 2, bsize // 2), 1)
    elif t == 1:
        for l in range(7):
            if l <= 3:
                if l == 3:
                    t_color = BACKGROUND
                else:
                    t_color = LINES
            else:
                t_color = KILLED_SHIP
            pygame.draw.rect(screen, t_color, (mid[0] + l * bsize // 2, mid[1] + bsize, bsize // 2, bsize // 2), 1)
    elif t == 0:
        for l in range(7):
            if l == 3:
                t_color = BACKGROUND
            else:
                t_color = KILLED_SHIP
            pygame.draw.rect(screen, t_color, (mid[0] + l * bsize // 2, mid[1] + bsize, bsize // 2, bsize // 2), 1)

    if d == 3:
        for l in range(8):
            if l == 2 or l == 5:
                d_color = BACKGROUND
            else:
                d_color = LINES
            pygame.draw.rect(screen, d_color, (mid[0] + l * bsize // 2, mid[1] + bsize * 2, bsize // 2, bsize // 2), 1)
    elif d == 2:
        for l in range(8):
            if l < 6:
                if l == 2 or l == 5:
                    d_color = BACKGROUND
                else:
                    d_color = LINES
            else:
                d_color = KILLED_SHIP
            pygame.draw.rect(screen, d_color, (mid[0] + l * bsize // 2, mid[1] + bsize * 2, bsize // 2, bsize // 2), 1)
    elif d == 1:
        for l in range(8):
            if l > 2:
                if l == 5:
                    d_color = BACKGROUND
                else:
                    d_color = KILLED_SHIP
            else:
                if l == 2:
                    d_color = BACKGROUND
                else:
                    d_color = LINES
            pygame.draw.rect(screen, d_color, (mid[0] + l * bsize // 2, mid[1] + bsize * 2, bsize // 2, bsize // 2), 1)
    elif d == 0:
        for l in range(8):
            if l == 2 or l == 5:
                d_color = BACKGROUND
            else:
                d_color = KILLED_SHIP
            pygame.draw.rect(screen, d_color, (mid[0] + l * bsize // 2, mid[1] + bsize * 2, bsize // 2, bsize // 2), 1)

    if s == 4:
        for l in range(7):
            if l != 0 and l % 2:
                s_color = BACKGROUND
            else:
                s_color = LINES
            pygame.draw.rect(screen, s_color, (mid[0] + l * bsize // 2, mid[1] + bsize * 3, bsize // 2, bsize // 2), 1)
    elif s == 3:
        for l in range(7):
            if l != 0 and l % 2:
                if l < 7:
                    s_color = BACKGROUND
            else:
                if l < 6:
                    s_color = LINES
                else:
                    s_color = KILLED_SHIP
            pygame.draw.rect(screen, s_color, (mid[0] + l * bsize // 2, mid[1] + bsize * 3, bsize // 2, bsize // 2), 1)
    elif s == 2:
        for l in range(7):
            if l != 0 and l % 2:
                if l < 7:
                    s_color = BACKGROUND
            else:
                if l < 4:
                    s_color = LINES
                else:
                    s_color = KILLED_SHIP

            pygame.draw.rect(screen, s_color, (mid[0] + l * bsize // 2, mid[1] + bsize * 3, bsize // 2, bsize // 2), 1)

    elif s == 1:
        for l in range(7):
            if l != 0 and l % 2:
                if l < 6:
                    s_color = BACKGROUND
            else:
                if l < 2:
                    s_color = LINES
                else:
                    s_color = KILLED_SHIP

            pygame.draw.rect(screen, s_color, (mid[0] + l * bsize // 2, mid[1] + bsize * 3, bsize // 2, bsize // 2), 1)

    elif s == 0:
        for l in range(7):
            if l != 0 and l % 2:
                if l < 6:
                    s_color = BACKGROUND
            else:
                s_color = KILLED_SHIP

            pygame.draw.rect(screen, s_color, (mid[0] + l * bsize // 2, mid[1] + bsize * 3, bsize // 2, bsize // 2), 1)


class grid:
    def __init__(self, lang):
        self.sz = None
        self.ft = None
        self.showInfoText = []
        self.alphaInfo = 0
        self.alphaVect = True
        self.sleepInfo = False
        self.InfoBusy = False
        self.timeStart = 0
        if lang == 'eng':
            self.letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        elif lang == 'rus':
            self.letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И']

    def edit(self, lang):
        if lang == 'eng':
            self.letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        elif lang == 'rus':
            self.letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И']

    def draw(self):
        for it in range(11):
            # Hor grid1
            pygame.draw.line(screen, LINES, (left_margin, upper_margin + it * bsize),
                             (left_margin + 10 * bsize, upper_margin + it * bsize), 1)
            # Vert grid1
            pygame.draw.line(screen, LINES, (left_margin + it * bsize, upper_margin),
                             (left_margin + it * bsize, upper_margin + 10 * bsize), 1)
            if it < 10:
                num = font.render(str(it + 1), True, LINES)
                letter = font.render(self.letters[it], True, LINES)
                num_ver_width = num.get_width()
                num_ver_height = num.get_height()
                letters_hor_width = letter.get_width()

                # Ver num grid1
                screen.blit(num, (left_margin - (bsize // 2 + num_ver_width // 2),
                                  upper_margin + it * bsize + (bsize // 2 - num_ver_height // 2)))
                # Hor letters grid1
                screen.blit(letter, (left_margin + it * bsize + (bsize //
                                                                 2 - letters_hor_width // 2),
                                     upper_margin - font.size(self.letters[it])[1]*1.2))

    def show_info(self, text):
        if text:
            if text not in self.showInfoText:
                self.showInfoText.append(text)

    def show_info_update(self):
        global mouse_left_press
        if self.showInfoText:
            if not self.sleepInfo and self.alphaVect and self.alphaInfo >= 255:
                info_sound.play()
                self.timeStart = time.time()
                self.sleepInfo = True
                st = self.showInfoText[0].split()
                self.showInfoText[0] = [' '.join(st[x:x + 5]) for x in range(0, len(st), 5)]
                st = 0
                for l in self.showInfoText[0]:
                    if len(l) > st:
                        st = len(l)
                        dt = l
                for s in range(1000):
                    self.ft = pygame.font.SysFont('notosans', s)
                    self.sz = self.ft.size(dt)
                    if self.sz[0] > infoSurface.get_rect()[2] - infoSurface.get_rect()[2] * 0.1 or self.sz[1] * len(
                            self.showInfoText[0]) > infoSurface.get_rect()[3]:
                        self.ft = pygame.font.SysFont('notosans', s - 1)
                        self.sz = self.ft.size(dt)
                        break
            elif not self.sleepInfo and self.alphaVect:
                self.alphaInfo += 255
            else:
                if not self.alphaVect and self.alphaInfo <= 0:
                    self.alphaVect = True
                    del self.showInfoText[0]
                elif not self.alphaVect:
                    self.alphaInfo -= 15
            try:
                infoSurface.blit(Buttons.RoundedRect((0, 0, infoSurface.get_rect()[2], infoSurface.get_rect()[3]), (48, 48, 48), 0.4),(0,0))

                for n, txt in enumerate(self.showInfoText[0]):
                    infoSurface.blit(self.ft.render(txt, True, (200, 200, 200)), (infoSurface.get_rect()[2] * 0.05,
                                                                                  infoSurface.get_rect()[3] * 0.05 +
                                                                                  self.sz[1] * n))
                infoSurface.set_alpha(self.alphaInfo)
                screen.blit(infoSurface, (size[0] // 2 // 1.5, upper_margin // 2 // 4))
            except IndexError:
                pass
            except AttributeError:
                pass
        if self.sleepInfo and len(self.showInfoText[0]) <= int(
                time.time() - self.timeStart) and not self.notis_collide():
            self.sleepInfo = False
            self.alphaVect = False
            self.timeStart = 0
        elif size[0] // 2 // 1.5 < pygame.mouse.get_pos()[0] < size[0] // 2 // 1.5 + size[
            0] // 2 // 1.5 and upper_margin // 2 // 2 < pygame.mouse.get_pos()[
            1] < upper_margin // 2 // 2 + upper_margin // 2 and mouse_left_press and self.sleepInfo:
            mouse_left_press = False
            self.sleepInfo = False
            self.alphaVect = True
            self.timeStart = 0
            self.alphaInfo = 0
            del self.showInfoText[0]

    def notis_collide(self):
        if (size[0] // 2 // 1.5) <= pygame.mouse.get_pos()[0] <= (size[0] // 2 // 1.5) + infoSurface.get_width() and (
                upper_margin // 2 // 4) <= pygame.mouse.get_pos()[1] <= (
                upper_margin // 2 // 4) + infoSurface.get_height():
            return True
        else:
            return False


Grid = grid('eng')


def re_settings_button():
    global settings_pad
    pad = settings_wheel
    SettingsButtons.empty()
    Switches.empty()
    Lists.empty()
    Slides.empty()
    if 0 < pad < 1.9:
        SoundOnOffButton = Buttons.label(
            (size[0] // 2 - size[0] // 1.92 // 2, size[1] * 0.5 * pad, size[0] // 1.92, size[1] // 36),
            GameLanguage['Settings Sound'],
            (0, 255, 255), (0, 0, 0))
        SwitchSoundOnOff = Buttons.switch(
            (SoundOnOffButton.rect.x + SoundOnOffButton.rect.w - (
                    SoundOnOffButton.rect.h * 2 - SoundOnOffButton.rect.h * 0.1) - 1,
             SoundOnOffButton.rect.y + 1,
             SoundOnOffButton.rect.h * 2 - SoundOnOffButton.rect.h * 0.1,
             SoundOnOffButton.rect.h - 2), (0, 255, 0), (255, 255, 255), (64, 64, 64),
            'Sound', GameSettings['Sound'])
        Switches.add(SwitchSoundOnOff)
        SettingsButtons.add(SoundOnOffButton)
    pad += 0.1
    if GameSettings['Sound']:
        if 0 < pad < 1.9:
            NotificationOnOffButton = Buttons.label((size[0] // 2 - size[0] // 1.92 // 2 + size[0] // 1.92 // 2 * 0.1,
                                                     size[1] * 0.5 * pad, size[0] // 1.92, size[1] // 36),
                                                    GameLanguage['Settings Notification Sound'], (0, 255, 255),
                                                    (0, 0, 0))
            SwitchNotificationOnOff = Buttons.switch(
                (NotificationOnOffButton.rect.x + NotificationOnOffButton.rect.w - (
                        NotificationOnOffButton.rect.h * 2 - NotificationOnOffButton.rect.h * 0.1) - 1,
                 NotificationOnOffButton.rect.y + 1,
                 NotificationOnOffButton.rect.h * 2 - NotificationOnOffButton.rect.h * 0.1,
                 NotificationOnOffButton.rect.h - 2), (0, 255, 0), (255, 255, 255),
                (64, 64, 64), 'NotificationSound', GameSettings['NotificationSound'])
            SettingsButtons.add(NotificationOnOffButton)
            Switches.add(SwitchNotificationOnOff)
        pad += 0.1
        if GameSettings['NotificationSound']:
            if 0 < pad < 1.9:
                NotificationSlideButton = Buttons.label(
                    (size[0] // 2 - size[0] // 1.92 // 2 + size[0] // 1.92 // 2 * 0.2,
                     size[1] * 0.5 * pad, size[0] // 1.92, size[1] // 36),
                    GameLanguage['Settings Sound Slide'], (0, 255, 255),
                    (0, 0, 0))
                SlideNotification = Buttons.Slide((
                    NotificationSlideButton.rect.x + NotificationSlideButton.rect.w - NotificationSlideButton.rect.h * 10 - 1,
                    NotificationSlideButton.rect.y + 1,
                    (NotificationSlideButton.rect.h * 10),
                    NotificationSlideButton.rect.h - 2),
                    (255, 255, 255), (24, 24, 24), GameSettings['NotificationSoundVol'],
                    'NotificationSoundVol')
                Slides.add(SlideNotification)
                SettingsButtons.add(NotificationSlideButton)
            pad += 0.1
        if 0 < pad < 1.9:
            GameSoundOnOffButton = Buttons.label((size[0] // 2 - size[0] // 1.92 // 2 + size[0] // 1.92 // 2 * 0.1,
                                                  size[1] * 0.5 * pad, size[0] // 1.92, size[1] // 36),
                                                 GameLanguage['Settings Game Sound'],
                                                 (0, 255, 255), (0, 0, 0))
            SwitchGameSoundOnOff = Buttons.switch(
                (GameSoundOnOffButton.rect.x + GameSoundOnOffButton.rect.w - (
                        GameSoundOnOffButton.rect.h * 2 - GameSoundOnOffButton.rect.h * 0.1) - 1,
                 GameSoundOnOffButton.rect.y + 1,
                 GameSoundOnOffButton.rect.h * 2 - GameSoundOnOffButton.rect.h * 0.1,
                 GameSoundOnOffButton.rect.h - 2), (0, 255, 0), (255, 255, 255),
                (64, 64, 64), 'GameSound', GameSettings['GameSound'])
            SettingsButtons.add(GameSoundOnOffButton)
            Switches.add(SwitchGameSoundOnOff)
        pad += 0.1
        if GameSettings['GameSound']:
            if 0 < pad < 1.9:
                GameSoundSlideButton = Buttons.label((size[0] // 2 - size[0] // 1.92 // 2 + size[0] // 1.92 // 2 * 0.2,
                                                      size[1] * 0.5 * pad, size[0] // 1.92, size[1] // 36),
                                                     GameLanguage['Settings Sound Slide'], (0, 255, 255),
                                                     (0, 0, 0))
                SlideGameSound = Buttons.Slide((
                    GameSoundSlideButton.rect.x + GameSoundSlideButton.rect.w - GameSoundSlideButton.rect.h * 10 - 1,
                    GameSoundSlideButton.rect.y + 1,
                    (GameSoundSlideButton.rect.h * 10),
                    GameSoundSlideButton.rect.h - 2),
                    (255, 255, 255), (24, 24, 24), GameSettings['GameSoundVol'],
                    'GameSoundVol')
                SettingsButtons.add(GameSoundSlideButton)
                Slides.add(SlideGameSound)
            pad += 0.1
    if 0 < pad < 1.9:
        LanguageSettings = Buttons.label(
            (size[0] // 2 - size[0] // 1.92 // 2, size[1] * 0.5 * pad, size[0] // 1.92, size[1] // 36),
            GameLanguage['Settings Language'],
            (0, 255, 255), (0, 0, 0))
        LanguageSettingsList = Buttons.List(
            (LanguageSettings.rect.x + LanguageSettings.rect.w - (
                    LanguageSettings.rect.h * 4 - LanguageSettings.rect.h * 0.1) - 1,
             LanguageSettings.rect.y + 1,
             LanguageSettings.rect.h * 4 - LanguageSettings.rect.h * 0.1,
             LanguageSettings.rect.h - 2),
            GameSettings['GameLanguage'], ['eng', 'rus'], (255, 255, 255), (255, 0, 255), (0, 0, 0), 'GameLanguage')
        SettingsButtons.add(LanguageSettings)
        Lists.add(LanguageSettingsList)
    pad += 0.1

    settings_pad = pad


re_settings_button()


def update_game(ver):
    global run
    mb = 0
    file = requests.get(f'https://github.com/AlexKim0710/OceanShipsWar/releases/download/alpha/OceanShipsWar.{ver}.exe',
                        stream=True)
    with open(f'OceanShipsWar {ver}.exe', 'wb') as f:
        for chunk in file.iter_content(1024 * 1024):
            f.write(chunk)
            mb += 1
    subprocess.Popen(f'OceanShipsWar {ver}.exe')
    run = False


FromGitVersion = requests.get(
                'https://raw.githubusercontent.com/AlexKim0710/OceanShipsWar/main/version').text[:-1]
if version < float(FromGitVersion):
    ERRORS.append(f'Загружается новая версия: {FromGitVersion}')
    threading.Thread(target=update_game, args=[FromGitVersion]).start()

while run:
    key_esc = False
    if pygame.display.get_window_size()[0] != size[0] or pygame.display.get_window_size()[1] != size[1]:
        size = [pygame.display.get_window_size()[0] if pygame.display.get_window_size()[0] >= 120 else 120,
                pygame.display.get_window_size()[1] if pygame.display.get_window_size()[1] >= 120 else 120]
        # if size[0] == get_monitors()[0].width and size[1] == get_monitors()[0].height:
        #     screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        #     room_screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # else:
        #     screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        #     room_screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        bsize = size[0] // 27.428571428571427
        ships_wh = int(bsize // 7)
        left_margin, upper_margin = (size[0] // 2 - bsize * 5), (size[1] // 2 - bsize * 5)
        font = pygame.font.SysFont('notosans', int(bsize / 1.5))
        infoSurface = pygame.Surface((size[0] // 2 // 1.5, upper_margin // 2), pygame.SRCALPHA)
        re_theme()
        re_settings_button()
        for x in range(10):
            for y in range(10):
                blocks_pos.append([[left_margin + x * bsize, upper_margin + y * bsize],
                                   [left_margin + ((x + 1) * bsize), upper_margin + ((y + 1) * bsize)]])
                blocks_corns.append([left_margin + x * bsize, upper_margin + y * bsize])
    for event in pygame.event.get():
        if create_game:
            for s in CreateGameButtons.sprites():
                u = s.update(event)
                if u:
                    u = u.split(':', 1)
                    if u[0] == 'create':
                        try:
                            GameSettings['my socket'] = [u[1], 998]
                            me = 'main'
                            not_me = 'client'
                            Enemy_socket = None
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                            sock.bind((GameSettings['my socket'][0], GameSettings['my socket'][1]))
                            sock.setblocking(False)
                            sock.listen(1)
                            re_theme()
                        except Exception as err:
                            ERRORS.append(f'Введите общедоступный IP адрес или хостинг!. {err}')
                            GameSettings['my socket'] = ['', 0]
                            re_theme()
        elif join_game:
            for s in JoinGameButtons.sprites():
                u = s.update(event)
                if u:
                    u = u.split(':', 1)
                    if u[0] == 'join':
                        GameSettings['my socket'] = [u[1], 998]
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_left_press = True
            if event.button == 4 and settings_wheel <= settings_upper_margin and settings_wheel - 0.1 >= settings_wheel - settings_pad + 1.8:
                settings_wheel = round(settings_wheel - 0.1, 1)
                re_settings_button()
            if event.button == 5 and settings_wheel + 0.1 <= settings_upper_margin:
                settings_wheel = round(settings_wheel + 0.1, 1)
                re_settings_button()
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_left_press = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                key_esc = True
    if room:
        room_screen.fill(BACKGROUND)
        sprites.update()
        RoomQuit.update()
        if ButtonTheme.isCollide() and mouse_left_press:
            theme = not theme
            re_theme()
            mouse_left_press = False
        elif ButtonSettings.isCollide() and mouse_left_press:
            # mouse_left_press = False
            # settings = True
            # room = False
            # re_settings_button()
            ERRORS.append('Настройки пока выключены. Простите.')
            mouse_left_press = False
        elif RoomQuit.isCollide() and mouse_left_press:
            run = False
        elif ButtonAdm.isCollide() and mouse_left_press:
            room = False
            create_game = True
        elif ButtonClient.isCollide() and mouse_left_press:
            room = False
            join_game = True
        elif Update.isCollide() and mouse_left_press:
            FromGitVersion = requests.get(
                'https://raw.githubusercontent.com/AlexKim0710/OceanShipsWar/main/version').text[:-1]
            if version < float(FromGitVersion):
                ERRORS.append(f'Загружается новая версия: {FromGitVersion}')
                threading.Thread(target=update_game, args=[FromGitVersion]).start()
            else:
                ERRORS.append('Актиальная версия')
        sprites.draw(screen)
    elif settings:
        room_screen.fill(BACKGROUND)
        SettingsButtons.update()
        SettingsMainLabel.update()
        EscButton.update()
        if EscButton.isCollide() and mouse_left_press or key_esc:
            settings = False
            room = True
        for s in Switches.sprites():
            if s.update(mouse_left_press):
                GameSettings[s.update(mouse_left_press)] = not GameSettings[s.update(mouse_left_press)]
                mouse_left_press = False
                re_settings_button()
        for l in Lists.sprites():
            u = l.update(mouse_left_press)
            if u:
                if ':' in str(u):
                    if 'GameLanguage' in u:
                        re_lang(str(u).split(':')[1])
                        Grid.edit(str(u).split(':')[1])
                        re_theme()
                    GameSettings[str(u).split(':')[0]] = str(u).split(':')[1]
                    re_settings_button()
                mouse_left_press = False
            elif not Slides.sprites():
                mouse_left_press = False
        count_sl = 0
        for s in Slides.sprites():
            u = s.update(mouse_left_press)
            if u:
                GameSettings[u[0]] = u[1]
            else:
                count_sl += 1
            if count_sl == len(Slides.sprites()):
                mouse_left_press = False
        SettingsButtons.draw(screen)
        Switches.draw(screen)
        Lists.draw(screen)
        Slides.draw(screen)
        pygame.draw.rect(screen, BACKGROUND, (0, 0, size[0], size[1] * 0.05))
        pygame.draw.line(screen, LINES, (0, size[1] * 0.05), (size[0], size[1] * 0.05), int(bsize // 2 // 10))
        pygame.draw.rect(screen, BACKGROUND, (0, size[1] * .95, size[0], size[1] * 0.95))
        pygame.draw.line(screen, LINES, (0, size[1] * .95), (size[0], size[1] * 0.95), int(bsize // 2 // 10))
        SystemButtons.draw(screen)
    elif create_game:
        screen.fill(BACKGROUND)
        EscButton.update()
        CreateGameMainLabel.update()
        if EscButton.isCollide() and mouse_left_press or key_esc:
            GameSettings['my socket'] = ['', 0]
            sock = None
            re_theme()
            create_game = False
            room = True
        if GameSettings['my socket'][0]:
            try:
                Enemy_socket, addr = sock.accept()
                GameSettings['enemy socket'] = [addr[0], addr[1]]
                create_game = False
                game = True
                is_adm = True
            except BlockingIOError:
                pass
            CreateGameWaitUser.update()
        pygame.draw.rect(screen, BACKGROUND, (0, 0, size[0], size[1] * 0.05))
        pygame.draw.line(screen, LINES, (0, size[1] * 0.05), (size[0], size[1] * 0.05), int(bsize // 2 // 10))
        pygame.draw.rect(screen, BACKGROUND, (0, size[1] * .95, size[0], size[1] * 0.95))
        pygame.draw.line(screen, LINES, (0, size[1] * .95), (size[0], size[1] * 0.95), int(bsize // 2 // 10))
        SystemButtons.draw(screen)
        CreateGameButtons.draw(screen)
    elif join_game:
        screen.fill(BACKGROUND)
        EscButton.update()
        JoinGameMainLabel.update()
        if EscButton.isCollide() and mouse_left_press or key_esc:
            GameSettings['my socket'] = ['', 0]
            sock = None
            join_game = False
            room = True
            re_theme()

        if GameSettings['my socket'][0]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.settimeout(1)
                sock.connect(
                    (GameSettings['my socket'][0],
                     998 if not GameSettings['my socket'][1] else GameSettings['my socket'][1]))
                is_adm = False
                game = True
                join_game = False
                me = 'client'
                not_me = 'main'
            except Exception as err:
                ERRORS.append(f'Введите общедоступный IP адрес или хостинг!. {err}')
                GameSettings['my socket'] = ['', 0]
                re_theme()

        pygame.draw.rect(screen, BACKGROUND, (0, 0, size[0], size[1] * 0.05))
        pygame.draw.line(screen, LINES, (0, size[1] * 0.05), (size[0], size[1] * 0.05), int(bsize // 2 // 10))
        pygame.draw.rect(screen, BACKGROUND, (0, size[1] * .95, size[0], size[1] * 0.95))
        pygame.draw.line(screen, LINES, (0, size[1] * .95), (size[0], size[1] * 0.95), int(bsize // 2 // 10))
        SystemButtons.draw(screen)
        JoinGameButtons.draw(screen)
    elif game:
        if pygame.display.get_window_size() != size:
            size = pygame.display.get_window_size()
            bsize = int(sum(size) // 42.857142857142854)
            ships_wh = int(bsize // 7)
            left_margin, upper_margin = (size[0] // 2 - bsize * 5), (size[1] // 2 - bsize * 5)
            font = pygame.font.SysFont('notosans', int(bsize / 1.5))
            infoSurface = pygame.Surface((size[0] // 2 // 1.5, upper_margin // 2), pygame.SRCALPHA)
            for x in range(10):
                for y in range(10):
                    blocks_pos.append([[left_margin + x * bsize, upper_margin + y * bsize],
                                       [left_margin + ((x + 1) * bsize), upper_margin + ((y + 1) * bsize)]])
                    blocks_corns.append([left_margin + x * bsize, upper_margin + y * bsize])

        run_game = False
        if is_adm:
            try:
                Enemy_socket, addr = sock.accept()
                print(f'connected: {addr}')
            except BlockingIOError:
                pass

            if Enemy_socket:
                try:
                    input_data = eval(Enemy_socket.recv(1024 * 2).decode())
                    Enemy_socket.send(str(send_data).encode())
                    run_game = True
                except BlockingIOError:
                    pass
                except OSError:
                    pass
                except ConnectionResetError:
                    ERRORS.append('Противник отключился.')
                    game = False
                    room = True
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                except ConnectionAbortedError:
                    ERRORS.append('Противник отключился.')
                    game = False
                    room = True
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                except json.decoder.JSONDecodeError:
                    print('Network connecting is over')
                    run = False
        else:
            try:
                sock.send(str(send_data).encode())
                input_data = eval(sock.recv(1024 * 2).decode())
                run_game = True
            except ConnectionResetError:
                ERRORS.append('Противник отключился.')
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                game = False
                room = True
        if run_game:
            screen.fill(BACKGROUND)
            for n, block in enumerate(blocks_pos):
                mouse_pos = pygame.mouse.get_pos()
                if block[0][0] <= mouse_pos[0] <= block[1][0] and block[0][1] <= mouse_pos[1] <= block[1][1]:
                    mouse_on_block = [n // 10, n % 10]
                    mouse_on_block_pos = block[0]
                    break
                else:
                    mouse_on_block = False
            if BUILD:
                for i, env in enumerate(ships_env):
                    if env[0] < pygame.mouse.get_pos()[0] < env[2] and env[1] < pygame.mouse.get_pos()[1] < env[3]:
                        Draw_select = True
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)
                        legitBuild = False
                        mouse_left_press = False
                        block_block_num = mouse_on_block
                        for type_ship in range(1, max(ships.keys()) + 1):
                            for sh in ships[type_ship].values():
                                if sh[0] <= pygame.mouse.get_pos()[0] <= sh[0] + sh[2] and sh[1] <= \
                                        pygame.mouse.get_pos()[1] <= sh[1] + sh[3]:
                                    Draw_select = False
                        break
                    else:
                        if not (mouse_on_block == block_block_num):
                            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                            Draw_select = True
                            block_block_num = False
                            legitBuild = True
                        else:
                            break
                if legitBuild and mouse_on_block and Draw_select:
                    pygame.draw.rect(screen, GREEN, (mouse_on_block_pos[0], mouse_on_block_pos[1], bsize, bsize), 5)
                elif mouse_on_block and Draw_select:
                    pygame.draw.rect(screen, RED, (mouse_on_block_pos[0], mouse_on_block_pos[1], bsize, bsize), 5)
                if not solo_ship and not duo_ship and not trio_ship and not quadro_ship:
                    BUILD = False
                    if send_data['move'] == 'build':
                        send_data['move'] = 'fin build'
                if mouse_left_press and mouse_on_block and legitBuild:
                    if solo_ship or duo_ship or trio_ship or quadro_ship:
                        great_build = False
                        if not build_ship:
                            block_start_build = mouse_on_block
                            pos_start_build = mouse_on_block_pos
                            index_of_len_ship = 2
                            build_ship = True
                            doSelect = True
                        else:
                            if block_start_build == mouse_on_block:
                                create_ship = [mouse_on_block_pos[0], mouse_on_block_pos[1], bsize, bsize]

                            else:
                                if doSelect:
                                    if block_start_build[0] < mouse_on_block[0]:
                                        doSelect = False
                                        left_to_right = True
                                        right_to_left, up_to_down, down_to_up = False, False, False

                                    elif block_start_build[0] > mouse_on_block[0]:
                                        doSelect = False
                                        right_to_left = True
                                        left_to_right, up_to_down, down_to_up = False, False, False

                                    elif block_start_build[1] < mouse_on_block[1]:
                                        doSelect = False
                                        up_to_down = True
                                        left_to_right, right_to_left, down_to_up = False, False, False

                                    elif block_start_build[1] > mouse_on_block[1]:
                                        doSelect = False
                                        down_to_up = True
                                        left_to_right, right_to_left, up_to_down = False, False, False

                                else:
                                    if left_to_right:
                                        if mouse_on_block[0] - block_start_build[0] >= 0:
                                            create_ship = [pos_start_build[0], pos_start_build[1],
                                                           (mouse_on_block[0] - block_start_build[0] + 1) * bsize,
                                                           bsize]
                                            index_of_len_ship = 2
                                        else:
                                            doSelect = True

                                    elif right_to_left:
                                        if block_start_build[0] - mouse_on_block[0] >= 0:
                                            create_ship = [mouse_on_block_pos[0], pos_start_build[1],
                                                           (block_start_build[0] - mouse_on_block[0] + 1) * bsize,
                                                           bsize]
                                            index_of_len_ship = 2
                                        else:
                                            doSelect = True

                                    elif up_to_down:
                                        if mouse_on_block[1] - block_start_build[1] >= 0:
                                            create_ship = [pos_start_build[0], pos_start_build[1], bsize,
                                                           (mouse_on_block[1] - block_start_build[1] + 1) * bsize]
                                            index_of_len_ship = 3
                                        else:
                                            doSelect = True

                                    elif down_to_up:
                                        if block_start_build[1] - mouse_on_block[1] >= 0:
                                            create_ship = [pos_start_build[0], mouse_on_block_pos[1], bsize,
                                                           (block_start_build[1] - mouse_on_block[1] + 1) * bsize]
                                            index_of_len_ship = 3
                                        else:
                                            doSelect = True

                                    pygame.draw.rect(screen, LINES, create_ship, ships_wh)
                                    for i, env in enumerate(ships_env):
                                        if env != quadro_ship_env:
                                            if (env[0] < create_ship[0] < env[2] and env[1] < create_ship[1] < env[
                                                3]) or (
                                                    env[0] < create_ship[2] + create_ship[0] < env[2] and env[1] <
                                                    create_ship[
                                                        3] + create_ship[1] < env[3]):
                                                ERRORS.append('Так нельзя!')
                                                legitBuild = False
                                                mouse_left_press = False
                                                build_ship = False

                else:
                    if build_ship and create_ship:
                        mouse_left_press = False
                        if create_ship[index_of_len_ship] / bsize > 4:
                            create_ship[index_of_len_ship] = 4 * bsize
                            build_ship = False
                            doSelect = True
                            ERRORS.append('Максимальная длина корабля 4 клетки!.')
                        if create_ship[index_of_len_ship] / bsize == 4:
                            if quadro_ship:
                                quadro_ship -= 1
                                My_ships_blocks[4][quadro] = []
                                bl = []
                                send_data['ships'][4][quadro] = {}
                                for l in range(4):
                                    if index_of_len_ship == 3:
                                        My_ships_blocks[4][quadro].append([create_ship[0], create_ship[1] + bsize * l,
                                                                           create_ship[0] + bsize,
                                                                           create_ship[1] + bsize + bsize * l])
                                    elif index_of_len_ship == 2:
                                        My_ships_blocks[4][quadro].append([create_ship[0] + bsize * l, create_ship[1],
                                                                           create_ship[0] + bsize + bsize * l,
                                                                           create_ship[1] + bsize])
                                    bl.append([
                                        get_cords_block([My_ships_blocks[4][0][l][0], My_ships_blocks[4][0][l][1]])[0],
                                        get_cords_block([My_ships_blocks[4][0][l][0], My_ships_blocks[4][0][l][1]])[1]
                                    ])

                                great_build = True
                                ships[4][quadro] = create_ship
                                send_data['ships'][4][quadro]['ship'] = [
                                    [get_cords_block(
                                        [My_ships_blocks[4][quadro][0][0], My_ships_blocks[4][quadro][0][1]])[
                                         0],
                                     get_cords_block(
                                         [My_ships_blocks[4][quadro][0][0], My_ships_blocks[4][quadro][0][1]])[
                                         1]],
                                    [get_cords_block(
                                        [My_ships_blocks[4][quadro][3][0], My_ships_blocks[4][quadro][3][1]])[
                                         0],
                                     get_cords_block(
                                         [My_ships_blocks[4][quadro][3][0], My_ships_blocks[4][quadro][3][1]])[
                                         1]]]
                                send_data['ships'][4][quadro]['blocks'] = bl
                                quadro += 1
                            else:
                                ERRORS.append('4-х палубные корабли закончились!.')
                                create_ship = None
                                build_ship = False
                                doSelect = True
                        elif create_ship[index_of_len_ship] / bsize == 3:
                            if trio_ship:
                                trio_ship -= 1
                                bl = []
                                send_data['ships'][3][trio] = {}
                                My_ships_blocks[3][trio] = []
                                for l in range(3):
                                    if index_of_len_ship == 3:
                                        My_ships_blocks[3][trio].append([create_ship[0], create_ship[1] + bsize * l,
                                                                         create_ship[0] + bsize,
                                                                         create_ship[1] + bsize + bsize * l])
                                    elif index_of_len_ship == 2:
                                        My_ships_blocks[3][trio].append([create_ship[0] + bsize * l, create_ship[1],
                                                                         create_ship[0] + bsize + bsize * l,
                                                                         create_ship[1] + bsize])
                                    bl.append([
                                        get_cords_block(
                                            [My_ships_blocks[3][trio][l][0], My_ships_blocks[3][trio][l][1]])[
                                            0],
                                        get_cords_block(
                                            [My_ships_blocks[3][trio][l][0], My_ships_blocks[3][trio][l][1]])[1]
                                    ])
                                send_data['ships'][3][trio]['ship'] = [
                                    [get_cords_block([My_ships_blocks[3][trio][0][0], My_ships_blocks[3][trio][0][1]])[
                                         0],
                                     get_cords_block([My_ships_blocks[3][trio][0][0], My_ships_blocks[3][trio][0][1]])[
                                         1]],
                                    [get_cords_block([My_ships_blocks[3][trio][2][0], My_ships_blocks[3][trio][2][1]])[
                                         0],
                                     get_cords_block([My_ships_blocks[3][trio][2][0], My_ships_blocks[3][trio][2][1]])[
                                         1]]]
                                send_data['ships'][3][trio]['blocks'] = bl
                                ships[3][trio] = create_ship
                                trio += 1
                                great_build = True
                            else:
                                ERRORS.append('3-х палубные корабли закончились!.')
                                create_ship = None
                                build_ship = False
                                doSelect = True
                        elif create_ship[index_of_len_ship] / bsize == 2:
                            if duo_ship:
                                duo_ship -= 1
                                My_ships_blocks[2][duo] = []
                                bl = []
                                send_data['ships'][2][duo] = {}
                                for l in range(2):
                                    if index_of_len_ship == 3:
                                        My_ships_blocks[2][duo].append([create_ship[0], create_ship[1] + bsize * l,
                                                                        create_ship[0] + bsize,
                                                                        create_ship[1] + bsize + bsize * l])
                                    elif index_of_len_ship == 2:

                                        My_ships_blocks[2][duo].append([create_ship[0] + bsize * l, create_ship[1],
                                                                        create_ship[0] + bsize + bsize * l,
                                                                        create_ship[1] + bsize])
                                    bl.append([
                                        get_cords_block([My_ships_blocks[2][duo][l][0], My_ships_blocks[2][duo][l][1]])[
                                            0],
                                        get_cords_block([My_ships_blocks[2][duo][l][0], My_ships_blocks[2][duo][l][1]])[
                                            1]
                                    ])
                                send_data['ships'][2][duo]['ship'] = [
                                    [get_cords_block([My_ships_blocks[2][duo][0][0], My_ships_blocks[2][duo][0][1]])[0],
                                     get_cords_block([My_ships_blocks[2][duo][0][0], My_ships_blocks[2][duo][0][1]])[
                                         1]],
                                    [get_cords_block([My_ships_blocks[2][duo][1][0], My_ships_blocks[2][duo][1][1]])[0],
                                     get_cords_block([My_ships_blocks[2][duo][1][0], My_ships_blocks[2][duo][1][1]])[
                                         1]]]
                                send_data['ships'][2][duo]['blocks'] = bl
                                ships[2][duo] = create_ship
                                duo += 1
                                great_build = True
                            else:

                                ERRORS.append('2-х палубные корабли закончились!.')
                                create_ship = None
                                build_ship = False
                                doSelect = True
                        elif create_ship[index_of_len_ship] / bsize == 1:
                            if solo_ship:
                                solo_ship -= 1
                                My_ships_blocks[1][solo] = []
                                bl = []
                                send_data['ships'][1][solo] = {}
                                for l in range(1):
                                    if index_of_len_ship == 3:
                                        My_ships_blocks[1][solo].append([create_ship[0], create_ship[1] + bsize * l,
                                                                         create_ship[0] + bsize,
                                                                         create_ship[1] + bsize + bsize * l])
                                    elif index_of_len_ship == 2:
                                        My_ships_blocks[1][solo].append([create_ship[0] + bsize * l, create_ship[1],
                                                                         create_ship[0] + bsize + bsize * l,
                                                                         create_ship[1] + bsize])
                                    bl.append([
                                        get_cords_block(
                                            [My_ships_blocks[1][solo][l][0], My_ships_blocks[1][solo][l][1]])[
                                            0],
                                        get_cords_block(
                                            [My_ships_blocks[1][solo][l][0], My_ships_blocks[1][solo][l][1]])[1]
                                    ])
                                send_data['ships'][1][solo]['ship'] = [
                                    [get_cords_block([My_ships_blocks[1][solo][0][0], My_ships_blocks[1][solo][0][1]])[
                                         0],
                                     get_cords_block([My_ships_blocks[1][solo][0][0], My_ships_blocks[1][solo][0][1]])[
                                         1]],
                                    [get_cords_block([My_ships_blocks[1][solo][0][0], My_ships_blocks[1][solo][0][1]])[
                                         0],
                                     get_cords_block([My_ships_blocks[1][solo][0][0], My_ships_blocks[1][solo][0][1]])[
                                         1]]]
                                send_data['ships'][1][solo]['blocks'] = bl
                                ships[1][solo] = create_ship
                                solo += 1
                                great_build = True
                            else:
                                ERRORS.append('1-о палубные корабли закончились!.')
                                create_ship = None
                                build_ship = False
                                doSelect = True
                        elif ships[ship][index_of_len_ship] / bsize == 0:
                            create_ship = None
                            build_ship = False
                            doSelect = True

                    if great_build:
                        great_build = False
                        build_ship = False
                        doSelect = True
                        ships_env.append(
                            [create_ship[0] - bsize, create_ship[1] - bsize, create_ship[0] + create_ship[2] + bsize,
                             create_ship[1] + create_ship[3] + bsize])
                        ship += 1
                        create_ship = None
                        left_to_right, right_to_left, up_to_down, down_to_up = False, False, False, False
                for type_s in range(1, max(ships.keys()) + 1):
                    for rc in ships[type_s].values():
                        pygame.draw.rect(screen, LINES, rc, ships_wh)

            Grid.draw()
            draw_ship_count(solo_ship, duo_ship, trio_ship, quadro_ship)

            if not BUILD:
                if win:
                    win = False
                    room = True
                    game = False
                for n, ev in enumerate(send_data['event']):
                    if 'update' in ev:
                        send_data['ships'] = eval(ev.split('|')[1])
                        send_data['selects'] = eval(ev.split('|')[2])
                        send_data['die'] = eval(ev.split('|')[3])
                        del send_data['event'][n]
                    elif 'lose' in ev:
                        ERRORS.append('LOSE!.')
                        game = False
                        room = True
                if is_adm:
                    if send_data['move'] == not_me and input_data['pass']:
                        send_data['move'] = me
                    elif send_data['move'] == me and send_data['pass']:
                        send_data['move'] = not_me
                    if send_data['move'] == not_me and send_data['pass']:
                        send_data['pass'] = False
                    move = send_data['move']
                else:
                    if input_data['move'] == not_me and send_data['pass']:
                        send_data['pass'] = False
                    move = input_data['move']
                if move == me:
                    txt = font.render('Ваш удар!.', True, (0, 255, 0))
                    screen.blit(txt, (size[0] // 2 - txt.get_rect()[2] // 2, size[1] - txt.get_rect()[3] - bsize // 2))
                    if mouse_on_block and mouse_left_press:
                        if mouse_on_block_pos not in My_selected_blocks_pos and mouse_on_block not in Enemy_die_block:
                            mouse_left_press = False
                            finality_point = False
                            killed_enemy = False
                            final_killed_enemy = False
                            for type_ship in input_data['ships']:
                                for num_of_ship in input_data['ships'][type_ship]:
                                    for num_of_block, bbl in enumerate(
                                            input_data['ships'][type_ship][num_of_ship]['blocks']):
                                        bl = get_pos_block([bbl[0], bbl[1]])
                                        bl = [bl[0], bl[1], bl[0] + bsize, bl[1] + bsize]
                                        if (bl[0] <= mouse_pos[0] <= bl[2]) and (bl[1] <= mouse_pos[1] <= bl[3]):
                                            Enemy_die_block_rect.append([bl[0], bl[1], bsize, bsize])
                                            send_data['die']['blocks'].append(bbl)
                                            del input_data['ships'][type_ship][num_of_ship]['blocks'][num_of_block]
                                            killed_enemy = True
                                            final_killed_enemy = False
                                            if not len(input_data['ships'][type_ship][num_of_ship]['blocks']):
                                                final_killed_enemy = True
                                                killed_enemy = True
                                                Enemy_die.append(
                                                    get_rect_ship(input_data['ships'][type_ship][num_of_ship]['ship']))
                                                input_data['die']['ships'].append(
                                                    input_data['ships'][type_ship][num_of_ship]['ship'])
                                                input_data['ships'][type_ship][num_of_ship]['ship'] = []
                                            send_data['event'].append(
                                                f'update|{str(input_data["ships"])}|{str(input_data["selects"])}|{str(input_data["die"])}')
                                            break

                            if killed_enemy:
                                Enemy_die_block.append(mouse_on_block)
                                if final_killed_enemy:
                                    killed_sound.play()
                                else:
                                    wounded_sound.play()
                                send_data['pass'] = False
                            else:
                                missed_sound.play()
                                send_data['pass'] = True
                                My_selected_blocks_pos.append(mouse_on_block_pos)
                                My_selected_blocks.append(mouse_on_block)
                    for rc in Enemy_die_block_rect:
                        if rc:
                            pygame.draw.line(screen, RED, (rc[0], rc[1]), (rc[0] + bsize, rc[1] + bsize), 5)
                            pygame.draw.line(screen, RED, (rc[0] + bsize, rc[1]), (rc[0], rc[1] + bsize), 5)
                    for rc in Enemy_die:
                        if rc:
                            pygame.draw.rect(screen, RED, rc, 5)
                    for rc in My_selected_blocks_pos:
                        pygame.draw.circle(screen, RED, (rc[0] + bsize // 2, rc[1] + bsize // 2), bsize / 100 * 10)
                    if mouse_on_block not in My_selected_blocks and mouse_on_block not in Enemy_die_block:
                        if mouse_on_block:
                            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                            pygame.draw.rect(screen, BLUE, (
                                get_pos_block(mouse_on_block)[0], get_pos_block(mouse_on_block)[1], bsize, bsize), 5)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)
                        pygame.draw.rect(screen, RED,
                                         (get_pos_block(mouse_on_block)[0], get_pos_block(mouse_on_block)[1], bsize,
                                          bsize),
                                         5)
                    tp = 0
                    for type_ship in input_data['ships']:
                        for num_of_ship in input_data['ships'][type_ship]:
                            if input_data['ships'][type_ship][num_of_ship]['ship'] == []:
                                tp += 1
                                print(tp)
                            else:
                                tp = 0
                    if tp == sum([solo, duo, trio, quadro]):
                        ERRORS.append('WIN!')
                        win = True
                        sock.close()

                elif move == not_me:
                    txt = font.render('Ждем...', True, (255, 255, 0))
                    screen.blit(txt, (size[0] // 2 - txt.get_rect()[2] // 2, size[1] - txt.get_rect()[3] - bsize // 2))
                    for type_s in range(1, max(send_data['ships'].keys()) + 1):
                        for sp in send_data['ships'][type_s].values():
                            if sp['ship']:
                                pygame.draw.rect(screen, LINES, get_rect_ship(sp['ship']), ships_wh)

                elif input_data['move'] == 'build':
                    for type_s in range(1, max(send_data['ships'].keys()) + 1):
                        for sp in send_data['ships'][type_s].values():
                            pygame.draw.rect(screen, LINES, get_rect_ship(sp['ship']), ships_wh)
                elif send_data['move'] == 'fin build' or input_data['move'] == 'fin build':
                    if is_adm:
                        send_data['move'] = random.choice([me, not_me])
                    else:
                        send_data['move'] = None
    Grid.show_info_update()
    for n, er in enumerate(ERRORS):
        del ERRORS[n]
        Grid.show_info(er)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
if sock:
    sock.close()

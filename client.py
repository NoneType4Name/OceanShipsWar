import json
import math
import os
import sys
import random
import socket
import subprocess
import time
import pygame
from ast import literal_eval
import requests
import threading
from screeninfo import get_monitors
from netifaces import interfaces, ifaddresses, AF_INET
from asets.Gui import *

clock = pygame.time.Clock()

run = True
sock = None
# GlobalTimeOut = requests.get('https://google.com').elapsed.total_seconds()
mouse_left_press = False
NotificationLeftPress = False
key_esc = False
pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.font.init()
size = [get_monitors()[0].width, get_monitors()[0].height]
global_size = size
attitude = list(map(lambda x: x//math.gcd(*size), size))
screen = pygame.display.set_mode(size, pygame.HWSURFACE)
ico = pygame.image.load('asets/ico.png')
pygame.display.set_icon(ico)
pygame.display.set_caption('Ocean Ship War')
KILLED_SHIP = (60, 60, 60)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
main_dir = os.getcwd()
theme = 0
version = '0.0.3b'
try:
    os.chdir(sys._MEIPASS)
except AttributeError:
    pass

bsize = size[0] // 27.428571428571427
ships_wh = int(bsize // 7)
left_margin, upper_margin = (size[0] // 2 - bsize * 5), (size[1] // 2 - bsize * 5)
font = pygame.font.Font('asets/notosans.ttf', int(bsize / 1.5))
infoSurface = pygame.Surface((size[0] // 2 // 1.5, upper_margin // 2), pygame.SRCALPHA)
blocks = {}
build_ship = False
build_y = False
ship = 0
doSelect = True
create_ship = None
ships = {1: {}, 2: {}, 3: {}, 4: {}}
ships_env = []
quadro_ship = 1
trio_ship = 2
duo_ship = 3
solo_ship = 4
great_build = False
ERRORS = []
LegitBuild = True
block_block_num = False
quadro_ship_rect = None
quadro_ship_env = None
DrawCursor = True
BUILD = True
killed_enemy = False
is_adm = None
room = True
create_game = False
join_game = False
settings = False
game = False
end_game = False
Sounds = {}
MaxStartLoad = 0
StartLoaded = 0
FineLoadGame = True
ConditionOfLoad = False
SettingsActiveElement = None

Labels = pygame.sprite.Group()
SettingsElements = pygame.sprite.Group()
settings_pos = 0.1
upper_margin_settings = 0.1
pad = 0
down_margin_settings = 1
sprites = pygame.sprite.Group()
SystemButtons = pygame.sprite.Group()
CreateGameButtons = pygame.sprite.Group()
JoinGameButtons = pygame.sprite.Group()
Notifications = pygame.sprite.Group()
LoadGameGroup = pygame.sprite.Group()
letters = []
solo, duo, trio, quadro = [0]*4
send_data = {'ships': {1: {}, 2: {}, 3: {}, 4: {}},
             'count': 0,
             'selects': [],
             'killed': {'blocks': [], 'ships': []},
             'die': {'blocks': [], 'ships': []},
             'move': 'build',
             'end game': False,
             'pass': False,
             'event': []}
input_data = send_data
Settings = {
    'Graphic': {
        'WindowSize': size,
        'Language': 'rus'
    },
    'Sound':{
        'Notification': 1,
        'Game': 1
    }
}
GameLanguage = {}
active_element = list(Settings.keys())[0]
GameSettings = {
    'my socket': ['', 0],
    'enemy socket': ['', 0]}
if os.path.exists('settings.json'):
    try:
        with open('settings.json') as f:
            Settings = json.loads(f.read())
    except json.decoder.JSONDecodeError as err:
        ERRORS.append(f'Ошибка инициализации json конфига\tСтрока:{err.lineno}\tСтолбец:{err.colno}\tСимвол:{err.pos}\tОшибка:{err.msg}')

GameLanguage = {'start game': 'Создать игру',
                'join game': 'Присоеденится к игре',
                'settings': 'Настройки',
                'theme light': 'Яркая',
                'theme dark': 'Тёмная',
                'Sound': 'Звук',
                'Sound Game': 'Звуки игры',
                'Sound Notification': 'Звуки уведомлений',
                'Graphic': 'Графика',
                'Graphic Language': 'Язык',
                'Graphic WindowSize': 'Размер окна',
                'Exit': 'Выход',
                'version': f'Версия {version}'}


def re_lang():
    global GameLanguage
    if Settings['Graphic']['Language'] == 'rus':
        GameLanguage = {'start game': 'Создать игру',
                        'join game': 'Присоеденится к игре',
                        'settings': 'Настройки',
                        'theme light': 'Яркая',
                        'theme dark': 'Тёмная',
                        'Sound': 'Звук',
                        'Sound Game': 'Звуки игры',
                        'Sound Notification': 'Звуки уведомлений',
                        'Graphic': 'Графика',
                        'Graphic Language': 'Язык',
                        'Graphic WindowSize': 'Размер окна',
                        'Exit': 'Выход',
                        'version': f'Версия {version}'}
    elif Settings['Graphic']['Language'] == 'eng':
        GameLanguage = {'start game': 'Create game',
                        'join game': 'Join to game',
                        'settings': 'Settings',
                        'theme light': 'Light',
                        'theme dark': 'Dark',
                        'Sound': 'Sound',
                        'Sound Game': 'Game Sound',
                        'Sound Notification': 'Notifications Sound',
                        'Graphic': 'Graphic',
                        'Graphic Language': 'Language',
                        'Graphic WindowSize': 'Window size',
                        'Exit': 'Exit',
                        'version': f'Version {version}'}


re_lang()


def GetRect(cords: tuple) -> pygame.Rect:
    if cords:
        return pygame.Rect(blocks[cords[0]][cords[1]])
    else:
        return False


def GetShip(cords: tuple) -> pygame.Rect:
    if cords:
        cords0 = GetRect(cords[0])
        cords1 = GetRect(cords[1])
        if cords0[1] == cords1[1]:
            return pygame.Rect(*cords0.topleft, cords1.x - cords0.x + bsize, bsize)
        else:
            return pygame.Rect(*cords0.topleft, bsize, cords1.y - cords0.y + bsize)

    else:
        return False


def GetShipEnv(cords: tuple) -> pygame.Rect:
    if cords:
        return pygame.Rect(cords[0] - bsize, cords[1] - bsize, cords[2] + bsize * 2, cords[3] + bsize * 2)
    else:
        return cords


def GetShipBlocks(cords: tuple) -> list:
    if cords:
        cord = []
        if cords[0][0] == cords[1][0]:
            for pos in range(cords[0][1], cords[1][1] + 1):
                cord.append((cords[0][0], pos))
        else:
            for pos in range(cords[0][0], cords[1][0] + 1):
                cord.append((pos, cords[0][1]))
        return cord


def re_theme():
    global ButtonAdm, ButtonClient, ButtonSettings, ButtonTheme, EscButton, SettingsMainLabel, RoomQuit, \
        CreateGameMainLabel, TextInputCr, TextInputJn, CreateGameWaitUser, JoinGameMainLabel, JoinGameWaitUser, BACKGROUND, LINES, KILLED_SHIP, Update, \
        StartLoadProgress, StartLoadLabel, StartLoadLabel2
    if theme:
        KILLED_SHIP = (200, 200, 200)
        LINES = pygame.Color(24, 24, 24)
        BACKGROUND = (227, 227, 227)
        ButtonsCl1 = (177, 220, 237)
        ButtonsCl2 = (255, 255, 255)
        ButtonsTxtColor = (64, 64, 64)
        ButtonsAtcCol1 = (255, 255, 255)
        ButtonsAtcCol2 = (127, 127, 127)
        ButtonsClActT = (0, 0, 0)
        TextInputArCl = (0, 255, 255)
        TextInputTxCl = (0, 0, 0)
    else:
        KILLED_SHIP = (60, 60, 60)
        LINES = pygame.Color(255, 255, 255)
        BACKGROUND = (24, 24, 24)
        ButtonsCl1 = (255, 255, 255)
        ButtonsCl2 = (0, 0, 0)
        ButtonsTxtColor = (255, 255, 255)
        ButtonsAtcCol1 = (255, 255, 255)
        ButtonsAtcCol2 = (127, 127, 127)
        ButtonsClActT = (0, 0, 0)
        TextInputArCl = (0, 0, 100)
        TextInputTxCl = (255, 255, 255)
    StartLoadProgress = ProgressBar(
        (size[0]//2-size[0]*0.2/2,size[1]*0.7,size[0]*0.2,size[1]*0.05), LINES, (0, 255, 0), 0)
    StartLoadLabel = Label((size[0]//2-size[0]*0.2/2,size[1]*0.6,size[0]*0.2,size[1]*0.05),'0 %',(0,0,0,0),(0,255,0), center=True)
    StartLoadLabel2 = Label((size[0]//2-size[0]*0.2/2,size[1]*0.65,size[0]*0.2,size[1]*0.05),'',(0,0,0,0),(0,255,0), center=True)
    Update = Button((-1, size[1] - bsize // 2, bsize * 2, bsize // 2), str(GameLanguage['version']), ButtonsCl1,
                    ButtonsCl2, ButtonsTxtColor,
                    ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    TextInputCr = TextInput(
        (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.2,
         size[1] * 0.1), BACKGROUND, TextInputArCl, TextInputTxCl, 'create',  [i['addr'] for i in ifaddresses(interfaces()[0]).setdefault(AF_INET, [{'addr':socket.gethostbyname(socket.getfqdn())}])][0],
        GameSettings['my socket'][0])
    TextInputJn = TextInput(
        (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.2,
         size[1] * 0.1), BACKGROUND, TextInputArCl, TextInputTxCl, 'join', '192.168.1.1',
        GameSettings['my socket'][0])
    CreateGameWaitUser = Label(
        (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.95 - size[1] * 0.1 // 2, size[0] * 0.2,
         size[1] * 0.1), f'Ждем соперника... Ваш адрес: {GameSettings["my socket"][0]}:{GameSettings["my socket"][1]}', BACKGROUND, (0, 255, 255), center=True)
    JoinGameWaitUser = Label(
        (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.95 - size[1] * 0.1 // 2, size[0] * 0.2,
         size[1] * 0.1), f'Ждем соперника... Адрес будущего соперника: {GameSettings["enemy socket"][0]}:{GameSettings["enemy socket"][1]}', BACKGROUND,
        (255, 0, 255), center=True)
    SettingsMainLabel = Label((size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                              GameLanguage['settings'], BACKGROUND, LINES, center=True)
    CreateGameMainLabel = Label((size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                                GameLanguage['start game'], BACKGROUND, LINES, center=True)
    JoinGameMainLabel = Label((size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                              GameLanguage['join game'], BACKGROUND, LINES, center=True)
    RoomQuit = Button((size[0] - bsize + 1, -1, bsize, bsize),
                      GameLanguage['Exit'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
                      ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    EscButton = Button((-1, -1, (bsize + bsize * 0.5) // 2, bsize // 2), 'ESC', ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
                       ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    ButtonAdm = Button(
        (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.3 - size[1] * 0.1, size[0] * 0.16,
         size[1] * 0.1),
        GameLanguage['start game'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
        ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    ButtonClient = Button(
        (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.16,
         size[1] * 0.1),
        GameLanguage['join game'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
        ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    ButtonSettings = Button(
        (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.7 - size[1] * 0.1, size[0] * 0.16,
         size[1] * 0.1),
        GameLanguage['settings'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
        ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    ButtonTheme = Button((size[0] - bsize - bsize // 2, size[1] - bsize - bsize // 2, bsize, bsize),
                         GameLanguage['theme light'] if theme else GameLanguage['theme dark'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
                         ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    sprites.empty()
    SystemButtons.empty()
    CreateGameButtons.empty()
    JoinGameButtons.empty()
    LoadGameGroup.empty()
    SystemButtons.add(EscButton, SettingsMainLabel, CreateGameMainLabel, CreateGameWaitUser, JoinGameMainLabel,
                      JoinGameWaitUser)
    CreateGameButtons.add(TextInputCr)
    JoinGameButtons.add(TextInputJn)
    sprites.add(ButtonAdm, ButtonClient, ButtonSettings, ButtonTheme, RoomQuit, Update)
    LoadGameGroup.add(StartLoadProgress,StartLoadLabel, StartLoadLabel2)


re_theme()
# easygui.fileopenbox(filetypes=["*.json"], multiple=True)
SOLO = solo_ship
DUO = duo_ship
TRIO = trio_ship
QUADRO = quadro_ship


def draw_ship_count(ships_count, max_ships=[SOLO,DUO,TRIO,QUADRO]):
    mid = [size[0] // 2 + size[0] // 2 // 2, size[1] // 2 - size[1] // 2 // 1.5]
    for type_ship in range(len(ships_count)):
        counter_block_num = 0
        for num_block in range(((max_ships[type_ship] * (type_ship + 1)) + max_ships[type_ship])):
            if counter_block_num < type_ship+1:
                if ships_count[type_ship]:
                    color = LINES
                else:
                    color = KILLED_SHIP
                counter_block_num += 1
            else:
                color = BACKGROUND
                counter_block_num = 0
                ships_count[type_ship] -= 1 if ships_count[type_ship] else 0
            pygame.draw.rect(screen, color, (mid[0] + num_block * (bsize // 2), mid[1] + bsize * (type_ship+1), bsize // 2, bsize // 2), ships_wh//3)


def draw():
    global letters
    if Settings['Graphic']['Language'] == 'eng':
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    elif Settings['Graphic']['Language'] == 'rus':
        letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И']
    for it in range(11):
        # Hor grid1
        pygame.draw.line(screen, LINES, (left_margin, upper_margin + it * bsize),
                         (left_margin + 10 * bsize, upper_margin + it * bsize), 1)
        # Vert grid1
        pygame.draw.line(screen, LINES, (left_margin + it * bsize, upper_margin),
                         (left_margin + it * bsize, upper_margin + 10 * bsize), 1)
        if it < 10:
            num = font.render(str(it + 1), True, LINES)
            letter = font.render(letters[it], True, LINES)
            num_ver_width = num.get_width()
            num_ver_height = num.get_height()
            letters_hor_width = letter.get_width()

            # Ver num grid1
            screen.blit(num, (left_margin - (bsize // 2 + num_ver_width // 2),
                              upper_margin + it * bsize + (bsize // 2 - num_ver_height // 2)))
            # Hor letters grid1
            screen.blit(letter, (left_margin + it * bsize + (bsize //
                                                             2 - letters_hor_width // 2),
                                 upper_margin - font.size(letters[it])[1] * 1.2))


draw()

for num_let in range(len(letters)):
    blocks[num_let] = []
    for num in range(len(letters)):
        blocks[num_let].append(pygame.Rect(left_margin + num_let * bsize, upper_margin + num * bsize, bsize, bsize))


def command(name):
    global active_element
    active_element = name
    re_settings_button()


def re_settings_button():
    global pad, active_element
    if theme:
        set_of_settings = {
            'up margin': 0.15,
            'down margin': 1.9,
            'label': ((214, 213, 212), (23, 21, 19),[(0,0,0), (200, 200, 200)]),
            'buttons': ((214, 213, 212), (214, 213, 212), (23, 21, 19), (0, 0, 0), (164, 163, 162), (23, 21, 19)),
            'buttons active': ((0, 0, 0), (164, 163, 162), (23, 21, 19), (0, 0, 0), (164, 163, 162), (23, 21, 19)),
            'switches': ((0, 255, 0), (0, 0, 0), (191, 191, 191)),
            'slides': ((117, 75, 7), (202, 169, 115)),
            'lists': ((23, 21, 19), (226, 226, 224), (214, 213, 210))
        }
    else:
        set_of_settings = {
            'up margin': 0.15,
            'down margin': 1.9,
            'label': ((41, 42, 43),(232, 234, 236), [(255,255,255), (91, 92, 93)]),
            'buttons': ((41, 42, 43),(41, 42, 43),(232, 234, 236), (255,255,255), (91, 92, 93), (232, 234, 236)),
            'buttons active': ((255,255,255), (91, 92, 93), (232, 234, 236), (255,255,255), (91, 92, 93), (232, 234, 236)),
            'switches': ((0, 255, 0), (255, 255, 255), (64, 64, 64)),
            'slides':((138, 180, 248), (53, 86, 140)),
            'lists':((232, 234, 236), (29, 29, 31), (41, 42, 45))
        }
    set_for_lists = {
        'Language': ['rus', 'eng'],
        'WindowSize': pygame.display.list_modes()
    }
    pad = round(settings_pos, 3)
    buttons_pad = set_of_settings['up margin']
    Labels.empty()
    SettingsElements.empty()
    temp_g = pygame.sprite.Group()
    if not active_element:
        active_element = list(Settings.keys())[0]
    BaseRect = pygame.Rect(size[0] // 2 - size[0] // 1.92 // 2, size[1] * pad, size[0] // 1.92, size[1] // 36)
    for type_settings in Settings:
        SettingsElements.add(Button((size[0]*0.05, size[1] * buttons_pad, BaseRect.h * 5, BaseRect.h),
                             GameLanguage[type_settings],
                             *set_of_settings['buttons active' if type_settings == active_element else 'buttons'], 1))
        if type_settings == active_element:
            for element in Settings[type_settings]:
                BaseRect = pygame.Rect(size[0] // 2 - size[0] // 1.92 // 2, size[1] * pad, size[0] // 1.92, size[1] // 36)
                MainElement = Label(BaseRect, GameLanguage[f'{type_settings} {element}'], *set_of_settings['label'], False)
                if type(Settings[type_settings][element]) is bool:
                    Element = Switch((BaseRect.x + BaseRect.w - (BaseRect.h * 2 - BaseRect.h * 0.1) - 1,
                                        BaseRect.y + 1,
                                        BaseRect.h * 2 - BaseRect.h * 0.1,
                                        BaseRect.h - 2),
                                        *set_of_settings['switches'],
                                        name=f'{type_settings} {element}', power=Settings[type_settings][element])
                    SettingsElements.add(Element)
                elif (type(Settings[type_settings][element])) in [str, list, tuple]:
                    Element = List((BaseRect.x + BaseRect.w - (BaseRect.h * 4 - BaseRect.h * 0.1) - 1,
                                    BaseRect.y + 1,
                                    BaseRect.h * 4 - BaseRect.h * 0.1,
                                    BaseRect.h - 2),
                                    Settings[type_settings][element],
                                    set_for_lists[element],
                                    *set_of_settings['lists'],
                                    f'{type_settings} {element}')
                    temp_g.add(Element)
                elif (type(Settings[type_settings][element])) in [float, int]:
                    Element = Slide(
                        (BaseRect.x + BaseRect.w - (BaseRect.h - 2) * 11.5 - 1,
                        BaseRect.y + 1,
                         (BaseRect.h - 2) * 10,
                         BaseRect.h - 2),
                        *set_of_settings['slides'], base_data=Settings[type_settings][element],
                        name=f'{type_settings} {element}')
                    SettingsElements.add(Element)
                else:
                    print(type_settings,element,type(Settings[type_settings][element]))
                    raise SystemError
                Labels.add(MainElement)
                pad += BaseRect.h/size[1] * 1.1
        buttons_pad += (BaseRect.h/size[1] * 1.1)

    for el in reversed(temp_g.sprites()):
        SettingsElements.add(el)
    return


re_settings_button()


def update_game(ver):
    global run
    mb = 0
    file = requests.get(f'https://github.com/NoneType4Name/OceanShipsWar/releases/latest/download/OceanShipsWar.exe',
                        stream=True)
    with open(fr'{main_dir}\OceanShipsWar {ver}.exe', 'wb') as f:
        for chunk in file.iter_content(1024 * 1024):
            f.write(chunk)
            mb += 1
    subprocess.Popen(fr'{main_dir}\OceanShipsWar {ver}.exe')
    run = False


def StartGame():
    global FineLoadGame, Sounds, StartLoaded, MaxStartLoad, ConditionOfLoad, FromGitVersion
    if pygame.mixer.get_init():
        Sounds = {}
        MaxStartLoad = 0
        StartLoaded = 0
        FineLoadGame = False
        ConditionOfLoad = ''
        list_of_load = {
            "info_sound": {"type": 'ogg'},
            "killed_sound": {"type": 'ogg'},
            "missed_sound": {"type": 'ogg'},
            "wounded_sound": {"type": 'ogg'}}
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAITARROW)
        while run:
            StartLoadLabel.text = 'Подключение...'
            try:
                FromGitVersion = \
                requests.get('https://github.com/NoneType4Name/OceanShipsWar/releases/latest').url.split('/')[-1]
                StartLoadLabel.text = ''
                break
            except requests.exceptions.ConnectionError:
                pass
        for var in list_of_load:
            ConditionOfLoad = f'Search: ./asets/{var}'
            while run:
                if os.path.exists(f'{main_dir}/asets/{var}.{list_of_load[var]["type"]}'):
                    MaxStartLoad += 1
                    break

        for var in list_of_load:
            ConditionOfLoad = f'Load: ./asets/{var}'
            StartLoaded += 1
            Sounds[var] = pygame.mixer.Sound(f'{main_dir}/asets/{var}.{list_of_load[var]["type"]}')
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        FineLoadGame = True
    else:
        Settings['Sound']['Notification'] = 0
        Settings['Sound']['Game'] = 0
        ERRORS.append('Ошибка инициализации звука.')
        return
    if FineLoadGame:
        if version != FromGitVersion:
            from_git_version_int = int(FromGitVersion.replace('.', '').replace('b', ''))
            version_int = int(version.replace('.', '').replace('b', ''))
            if from_git_version_int < version_int:
                ERRORS.append(f'\tПриветствуем участника pre-тестирования!.\t')
            else:
                ERRORS.append(f'Загружается новая версия: {FromGitVersion}')
                threading.Thread(target=update_game, args=[FromGitVersion]).start()
        elif 'b' in FromGitVersion:
            ERRORS.append(f'\tПриветствуем участника бетатестирования!.\t')
    return


threading.Thread(target=StartGame).start()

while run:
    key_esc = False
    mouse_pos = pygame.mouse.get_pos()
    if size != Settings['Graphic']['WindowSize']:
        size = Settings['Graphic']['WindowSize']
        pygame.display.quit()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.display.init()
        screen = pygame.display.set_mode(size, pygame.HWSURFACE)
        pygame.display.set_caption('Ocean Ship Wars')
        pygame.display.set_icon(ico)
        bsize = size[0] // 27.428571428571427
        ships_wh = int(bsize // 7)
        left_margin, upper_margin = (size[0] // 2 - bsize * 5), (size[1] // 2 - bsize * 5)
        font = pygame.font.Font('asets/notosans.ttf', int(bsize / 1.5))
        infoSurface = pygame.Surface((size[0] // 2 // 1.5, upper_margin // 2), pygame.SRCALPHA)
        re_theme()
        re_settings_button()
    for event in pygame.event.get():
        if create_game:
            for s in CreateGameButtons.sprites():
                update: dict = s.update(event)
                if update:
                    u = list(update.keys())[0]
                    if u == 'create':
                        try:
                            if ':' in update[u]:
                                data = update[u].split(':', 1)
                                GameSettings['my socket'] = [data[0], int(data[1])]
                            else:
                                GameSettings['my socket'] = [update[u], 9998]
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
                            ERRORS.append(f'Введите общедоступный IP адрес или хостинг!.\t{err}')
                            GameSettings['my socket'] = ['', 0]
                            re_theme()
        elif join_game:
            for s in JoinGameButtons.sprites():
                update: dict = s.update(event)
                if update:
                    u = list(update.keys())[0]
                    if u == 'join':
                        if ':' in update[u]:
                            data = update[u].split(':', 1)
                            GameSettings['my socket'] = [data[0], int(data[1])]
                        else:
                            GameSettings['my socket'] = [update[u], 9998]
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            step = 0.05
            if event.button == 1:
                mouse_left_press = True
                NotificationLeftPress = True
            elif event.button == 5:
                if settings_pos - step >= upper_margin_settings:
                    for s in Labels.sprites():
                        s.RectEdit(0, -int(size[1]*step))
                    for s in SettingsElements.sprites():
                        s.RectEdit(0, -int(size[1]*step))
                    settings_pos = round(settings_pos - step, 3)
            elif event.button == 4:
                if settings_pos + step + pad <= down_margin_settings:
                    for s in Labels.sprites():
                        s.RectEdit(0, int(size[1]*step))
                    for s in SettingsElements.sprites():
                        s.RectEdit(0, int(size[1]*step))
                    settings_pos = round(settings_pos + step, 3)
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_left_press = False
                NotificationLeftPress = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                key_esc = True
    if not FineLoadGame:
        screen.fill(BACKGROUND)
        StartLoadLabel2.text = ConditionOfLoad
        if MaxStartLoad:
            StartLoadProgress.value = StartLoaded/MaxStartLoad
            StartLoadLabel2.text = ConditionOfLoad
            StartLoadLabel.text = f'{int(StartLoaded/MaxStartLoad*100)} %'
        else:
            StartLoadProgress.value = 0
            StartLoadLabel.text = 'Подключение...'
        LoadGameGroup.update()
        LoadGameGroup.draw(screen)

    elif room:
        screen.fill(BACKGROUND)
        sprites.update()
        RoomQuit.update()
        if ButtonTheme.isCollide() and mouse_left_press:
            theme = not theme
            re_theme()
            mouse_left_press = False
        elif ButtonSettings.isCollide() and mouse_left_press:
            mouse_left_press = False
            settings = True
            room = False
            re_settings_button()
            ERRORS.append('Настройки пока работают не исправно!.\tПростите.')
        elif RoomQuit.isCollide() and mouse_left_press:
            run = False
        elif ButtonAdm.isCollide() and mouse_left_press:
            mouse_left_press = False
            room = False
            create_game = True
            TextInputCr.active = True
        elif ButtonClient.isCollide() and mouse_left_press:
            mouse_left_press = False
            room = False
            join_game = True
            TextInputJn.active = True
        elif Update.isCollide() and mouse_left_press:
            FromGitVersion = requests.get('https://github.com/NoneType4Name/OceanShipsWar/releases/latest').url.split('/')[-1]
            if version != FromGitVersion:
                FromGitVersionInt = int(FromGitVersion.replace('.', '').replace('b', ''))
                versionInt = int(version.replace('.', '').replace('b', ''))
                if FromGitVersionInt < versionInt:
                    ERRORS.append('pre-release.')
                else:
                    ERRORS.append(f'Загружается новая версия: {FromGitVersion}')
                    threading.Thread(target=update_game, args=[FromGitVersion]).start()
            else:
                ERRORS.append('Актуальная версия.')
        sprites.draw(screen)
    elif settings:
        screen.fill(BACKGROUND)
        SettingsMainLabel.update()
        EscButton.update()
        if SettingsActiveElement:
            Labels.update(GameLanguage[SettingsActiveElement.name])
        else:
            Labels.update()
        Labels.draw(screen)
        if EscButton.isCollide() and NotificationLeftPress or key_esc:
            SettingsActiveElement = None
            settings = False
            room = True
        for sprite in SettingsElements.sprites():
            if not SettingsActiveElement:
                SpriteUpdate: dict = sprite.update(mouse_left_press)
                if SpriteUpdate:
                    if type(SpriteUpdate) is bool:
                        SettingsActiveElement = sprite
                    elif type(SpriteUpdate) is int:
                        SettingsActiveElement = sprite
                        mouse_left_press = False
                    elif type(SpriteUpdate) is dict:
                        temp = tuple(SpriteUpdate.keys())[0]
                        if temp:
                            temp2 = temp.split(' ')
                            Settings[temp2[0]][temp2[1]] = SpriteUpdate[temp]
                        mouse_left_press = False
                        re_lang()
                        re_theme()
                        re_settings_button()
            else:
                if sprite != SettingsActiveElement:
                    sprite.update(False)
                else:
                    SpriteUpdate: dict = sprite.update(mouse_left_press)
                    if SpriteUpdate:
                        if type(SpriteUpdate) != bool:
                            temp = tuple(SpriteUpdate.keys())[0]
                            temp2 = temp.split(' ')
                            Settings[temp2[0]][temp2[1]] = SpriteUpdate[temp]
                            SettingsActiveElement = None
                            mouse_left_press = False
                            re_lang()
                            re_theme()
                            re_settings_button()
                        else:
                            SettingsActiveElement = None
                            mouse_left_press = False

        SettingsElements.draw(screen)
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
                sock.settimeout(5)
                sock.connect(
                    (GameSettings['my socket'][0], 9998 if not GameSettings['my socket'][1] else GameSettings['my socket'][1]))
                is_adm = False
                game = True
                join_game = False
                me = 'client'
                not_me = 'main'
            except Exception as err:
                ERRORS.append(f'Введите общедоступный IP адрес или хостинг!. \t{err}')
                GameSettings['my socket'] = ['', 0]
                re_theme()

        pygame.draw.rect(screen, BACKGROUND, (0, 0, size[0], size[1] * 0.05))
        pygame.draw.line(screen, LINES, (0, size[1] * 0.05), (size[0], size[1] * 0.05), int(bsize // 2 // 10))
        pygame.draw.rect(screen, BACKGROUND, (0, size[1] * .95, size[0], size[1] * 0.95))
        pygame.draw.line(screen, LINES, (0, size[1] * .95), (size[0], size[1] * 0.95), int(bsize // 2 // 10))
        SystemButtons.draw(screen)
        JoinGameButtons.draw(screen)
    elif game:
        run_game = False
        if is_adm:
            if Enemy_socket:
                try:
                    input_data = literal_eval(Enemy_socket.recv(2048).decode())
                    Enemy_socket.send(str(send_data).encode())
                    run_game = True
                except (BlockingIOError,OSError):
                    pass
                except (ConnectionAbortedError, SyntaxError, ConnectionResetError, socket.timeout):
                    ERRORS.append('Противник отключился.')
                    game = False
                    room = True
                    sock.close()
                    sock = None
                    GameSettings['my socket'] = ['', 0]
                    GameSettings['enemy socket'] = ['', 0]
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        else:
            try:
                sock.send(str(send_data).encode())
                input_data = literal_eval(sock.recv(2048).decode())
                run_game = True
            except (ConnectionResetError, socket.timeout):
                ERRORS.append('Противник отключился.')
                game = False
                room = True
                sock.close()
                sock = None
                GameSettings['my socket'] = ['', 0]
                GameSettings['enemy socket'] = ['', 0]
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        if end_game:
            run_game = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            screen.fill(BACKGROUND)
            EscButton.update()
            l = Label((size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.3 // 2, size[0] * 0.2, size[1] * 0.3), 'Вы проиграли!.' if send_data['end game'] == me else 'Вы выйграли!.', BACKGROUND,(0, 255, 255))
            l.update()
            screen.blit(l.image, l.rect)
            screen.blit(EscButton.image, EscButton.rect)
            if EscButton.isCollide() and mouse_left_press or key_esc:
                game = False
                end_game = False
                room = True
                end_game_alpha = 0
                sock.close()
                sock = None
                GameSettings['my socket'] = ['', 0]
                GameSettings['enemy socket'] = ['', 0]

        if run_game:
            screen.fill(BACKGROUND)
            draw()
            RunCycle = True
            mouse_on_block = False
            for letter in blocks:
                if RunCycle:
                    for num, block in enumerate(blocks[letter]):
                        if block.collidepoint(mouse_pos):
                            mouse_on_block = (letter, num)
                            RunCycle = False
                            break
                else:
                    break
            if BUILD:
                LegitBuild = True
                RunCycle = True
                DrawCursor = True
                for type_s in ships:
                    if RunCycle:
                        for rc in ships[type_s].values():
                            rc = rc['ship']
                            rect = GetShip(rc)
                            if GetShipEnv(rect).collidepoint(mouse_pos):
                                LegitBuild = False
                                if GetShip(rc).collidepoint(mouse_pos):
                                    DrawCursor = False
                                RunCycle = False
                                break
                    else:
                        break

                if not solo_ship and not duo_ship and not trio_ship and not quadro_ship:
                    BUILD = False
                    send_data['ships'] = ships
                    send_data['count'] = ship
                    if send_data['move'] == 'build':
                        send_data['move'] = 'fin build'
                if mouse_left_press and mouse_on_block and LegitBuild:
                    if solo_ship or duo_ship or trio_ship or quadro_ship:
                        DrawCursor = False
                        great_build = False
                        if not build_ship:
                            start_build = mouse_on_block
                            index_of_len_ship = 2
                            build_ship = True
                            doSelect = True
                        else:
                            if start_build == mouse_on_block:
                                create_ship = (start_build, mouse_on_block)
                            else:
                                if doSelect:
                                    if GetRect(start_build).x < GetRect(mouse_on_block).x:
                                        doSelect = False
                                        left_to_right = True
                                        right_to_left, up_to_down, down_to_up = False, False, False

                                    elif GetRect(start_build).x > GetRect(mouse_on_block).x:
                                        doSelect = False
                                        right_to_left = True
                                        left_to_right, up_to_down, down_to_up = False, False, False

                                    elif GetRect(start_build).y < GetRect(mouse_on_block).y:
                                        doSelect = False
                                        up_to_down = True
                                        left_to_right, right_to_left, down_to_up = False, False, False

                                    elif GetRect(start_build).y > GetRect(mouse_on_block).y:
                                        doSelect = False
                                        down_to_up = True
                                        left_to_right, right_to_left, up_to_down = False, False, False

                                else:
                                    if left_to_right:
                                        if GetRect(mouse_on_block).x - GetRect(start_build).x > 0:
                                            create_ship = (start_build, (mouse_on_block[0], start_build[1]))
                                            index_of_len_ship = 2
                                        else:
                                            doSelect = True

                                    elif right_to_left:
                                        if GetRect(start_build).x - GetRect(mouse_on_block).x > 0:
                                            create_ship = ((mouse_on_block[0], start_build[1]), start_build)
                                            index_of_len_ship = 2
                                        else:
                                            doSelect = True

                                    elif up_to_down:
                                        if GetRect(mouse_on_block).y - GetRect(start_build).y > 0:
                                            create_ship = (start_build, (start_build[0], mouse_on_block[1]))
                                            index_of_len_ship = 3
                                        else:
                                            doSelect = True

                                    elif down_to_up:
                                        if GetRect(start_build).y - GetRect(mouse_on_block).y > 0:
                                            create_ship = ((start_build[0], mouse_on_block[1]), start_build)
                                            index_of_len_ship = 3
                                        else:
                                            doSelect = True
                            if create_ship:
                                pygame.draw.rect(screen, LINES, GetShip(create_ship), ships_wh)

                else:
                    if build_ship and create_ship:
                        mouse_left_press = False
                        RunCycle = True
                        for type_s in ships:
                            if RunCycle:
                                for rc in ships[type_s].values():
                                    rect = GetShip(rc['ship'])
                                    if GetShipEnv(GetShip(create_ship)).colliderect(rect):
                                        create_ship = None
                                        build_ship = False
                                        ERRORS.append('Не по правилам!.')
                                        RunCycle = False
                                        break
                            else:
                                break
                        else:
                            if GetShip(create_ship)[index_of_len_ship] / bsize > 4:
                                ERRORS.append('Максимальная длина корабля 4 клетки!.')
                                create_ship = None
                                build_ship = False
                                doSelect = True
                                DrawCursor = True
                            elif GetShip(create_ship)[index_of_len_ship] / bsize == 4:
                                if quadro_ship:
                                    quadro_ship -= 1
                                    ships[4][quadro] = {'ship': create_ship, 'blocks': GetShipBlocks(create_ship)}
                                    quadro += 1
                                    great_build = True
                                else:
                                    ERRORS.append('4-х палубные корабли закончились!.')
                                    create_ship = None
                                    build_ship = False
                                    doSelect = True
                                    DrawCursor = True
                            elif GetShip(create_ship)[index_of_len_ship] / bsize == 3:
                                if trio_ship:
                                    trio_ship -= 1
                                    ships[3][trio] = {'ship': create_ship, 'blocks': GetShipBlocks(create_ship)}
                                    trio += 1
                                    great_build = True
                                else:
                                    ERRORS.append('3-х палубные корабли закончились!.')
                                    create_ship = None
                                    build_ship = False
                                    doSelect = True
                                    DrawCursor = True
                            elif GetShip(create_ship)[index_of_len_ship] / bsize == 2:
                                if duo_ship:
                                    duo_ship -= 1
                                    ships[2][duo] = {'ship': create_ship, 'blocks': GetShipBlocks(create_ship)}
                                    duo += 1
                                    great_build = True
                                else:
                                    ERRORS.append('2-х палубные корабли закончились!.')
                                    create_ship = None
                                    build_ship = False
                                    doSelect = True
                                    DrawCursor = True
                            elif GetShip(create_ship)[index_of_len_ship] / bsize == 1:
                                if solo_ship:
                                    solo_ship -= 1
                                    ships[1][solo] = {'ship': create_ship, 'blocks': GetShipBlocks(create_ship)}
                                    solo += 1
                                    great_build = True
                                else:
                                    ERRORS.append('1-о палубные корабли закончились!.')
                                    create_ship = None
                                    build_ship = False
                                    doSelect = True
                                    DrawCursor = True
                        if great_build:
                            great_build = False
                            build_ship = False
                            doSelect = True
                            DrawCursor = True
                            ship += 1
                            create_ship = None
                            left_to_right, right_to_left, up_to_down, down_to_up = False, False, False, False
                for type_s in ships:
                    for rc in ships[type_s].values():
                        pygame.draw.rect(screen, LINES, GetShip(rc['ship']), ships_wh)
                if LegitBuild:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)
                if LegitBuild and mouse_on_block and DrawCursor:
                    pygame.draw.rect(screen, GREEN, GetRect(mouse_on_block), ships_wh)
                elif not LegitBuild and mouse_on_block and DrawCursor:
                    pygame.draw.rect(screen, RED, GetRect(mouse_on_block), ships_wh)

                draw_ship_count([solo_ship, duo_ship, trio_ship, quadro_ship])

            if not BUILD:
                send_data['event'] = []
                for n, event in enumerate(input_data['event']):
                    try:
                        if event['type'] == 'sound':
                            if Settings['Sound']['Game']:
                                Sounds[event['event']].set_volume(Settings['Sound']['Game'])
                                Sounds[event['event']].play()
                    except Exception:
                        pass
                try:
                    for type_ship in send_data['ships']:
                        for num_of_ship in send_data['ships'][type_ship]:
                            for num_of_block, block in enumerate(send_data['ships'][type_ship][num_of_ship]['blocks']):
                                if block in input_data['killed']['blocks']:
                                    del send_data['ships'][type_ship][num_of_ship]['blocks'][num_of_block]
                                    send_data['die']['blocks'].append(block)
                                    if not send_data['ships'][type_ship][num_of_ship]['blocks']:
                                        send_data['die']['ships'].append(send_data['ships'][type_ship][num_of_ship]['ship'])
                                        del send_data['ships'][type_ship][num_of_ship]
                                    break
                except RuntimeError:
                    pass

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
                    if len(input_data['die']['ships']) == input_data['count']:
                        send_data['end game'] = not_me
                        ERRORS.append('Выйгрыш!.')
                        end_game = True
                    elif len(send_data['die']['ships']) == send_data['count']:
                        send_data['end game'] = me
                        ERRORS.append('Проигрыш!.')
                        end_game = True
                    txt = font.render('Ваш удар!.', True, (0, 255, 0))
                    screen.blit(txt, (size[0] // 2 - txt.get_rect()[2] // 2, size[1] - txt.get_rect()[3] - bsize // 2))
                    if mouse_on_block and mouse_left_press:
                        if mouse_on_block not in send_data['selects'] and mouse_on_block not in send_data['killed'][
                            'blocks']:
                            mouse_left_press = False
                            killed_enemy = False
                            final_killed_enemy = False
                            RunCycle = True
                            for type_ship in input_data['ships']:
                                if RunCycle:
                                    for num_of_ship in input_data['ships'][type_ship]:
                                        if RunCycle:
                                            for num_of_block, block in enumerate(
                                                    input_data['ships'][type_ship][num_of_ship]['blocks']):
                                                RectBlock = GetRect(block)
                                                if RectBlock.collidepoint(mouse_pos):
                                                    send_data['killed']['blocks'].append(block)
                                                    del input_data['ships'][type_ship][num_of_ship]['blocks'][
                                                        num_of_block]
                                                    killed_enemy = True
                                                    final_killed_enemy = False
                                                    if not len(input_data['ships'][type_ship][num_of_ship]['blocks']):
                                                        final_killed_enemy = True
                                                        killed_enemy = True
                                                        send_data['killed']['ships'].append(
                                                            input_data['ships'][type_ship][num_of_ship]['ship'])
                                                    RunCycle = False
                                                    break
                                        else:
                                            break
                                else:
                                    break
                            if killed_enemy:
                                if final_killed_enemy:
                                    if Settings['Sound']['Game']:
                                        Sounds['killed_sound'].set_volume(Settings['Sound']['Game'])
                                        Sounds['killed_sound'].play()
                                        send_data['event'].append(
                                            {'type': 'sound', 'event': 'killed_sound'})
                                else:
                                    if Settings['Sound']['Game']:
                                        Sounds['wounded_sound'].set_volume(Settings['Sound']['Game'])
                                        Sounds['wounded_sound'].play()
                                        send_data['event'].append(
                                            {'type': 'sound', 'event': 'wounded_sound'})
                                send_data['pass'] = False
                            else:
                                if Settings['Sound']['Game']:
                                    Sounds['missed_sound'].set_volume(Settings['Sound']['Game'])
                                    Sounds['missed_sound'].play()
                                    send_data['event'].append({'type': 'sound', 'event': 'missed_sound'})
                                send_data['pass'] = True
                                send_data['selects'].append(mouse_on_block)
                    for rc in input_data['die']['blocks']:
                        pygame.draw.line(screen, RED, GetRect(rc).topleft, GetRect(rc).bottomright)
                        pygame.draw.line(screen, RED, GetRect(rc).topright, GetRect(rc).bottomleft)

                    for rc in input_data['die']['ships']:
                        pygame.draw.rect(screen, RED, GetShip(rc), ships_wh)

                    for rc in send_data['selects']:
                        pygame.draw.circle(screen, RED, GetRect(rc).center, bsize / 100 * 10)
                    if mouse_on_block not in send_data['selects'] and mouse_on_block not in send_data['killed']['blocks']:
                        if mouse_on_block:
                            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                            pygame.draw.rect(screen, BLUE, GetRect(mouse_on_block), ships_wh)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)
                        pygame.draw.rect(screen, RED, GetRect(mouse_on_block), ships_wh)

                elif move == not_me:
                    if len(input_data['die']['ships']) == input_data['count']:
                        send_data['end game'] = not_me
                        ERRORS.append('Выйгрыш!.')
                        end_game = True
                    elif len(send_data['die']['ships']) == send_data['count']:
                        send_data['end game'] = me
                        ERRORS.append('Проигрыш!.')
                        end_game = True
                    txt = font.render('Ждем...', True, (255, 255, 0))
                    screen.blit(txt, (size[0] // 2 - txt.get_rect()[2] // 2, size[1] - txt.get_rect()[3] - bsize // 2))
                    for type_s in range(1, max(send_data['ships'].keys()) + 1):
                        for sp in send_data['ships'][type_s].values():
                            pygame.draw.rect(screen, LINES, GetShip(sp['ship']), ships_wh)
                    for block in send_data['die']['blocks']:
                        block = GetRect(block)
                        pygame.draw.line(screen, tuple(map(lambda c: c - 100 if c > 100 else 100, LINES)),
                                         block.topright, block.midbottom)
                        pygame.draw.line(screen, tuple(map(lambda c: c - 100 if c > 100 else 100, LINES)), block.midtop,
                                         block.bottomleft)
                    for rc in send_data['die']['ships']:
                        pygame.draw.rect(screen, tuple(map(lambda c: c - 100 if c > 100 else 100, LINES)),
                                         GetShip(rc), ships_wh)
                    for rc in input_data['selects']:
                        pygame.draw.circle(screen, RED, GetRect(rc).center, bsize / 100 * 10)
                    out_to_func_draw_ship_count = []
                    for type_ship in input_data['ships']:
                        out_to_func_draw_ship_count.append(len(send_data['ships'][type_ship]))
                    draw_ship_count(out_to_func_draw_ship_count)

                elif input_data['move'] == 'build':
                    for type_s in range(1, max(send_data['ships'].keys()) + 1):
                        for sp in send_data['ships'][type_s].values():
                            pygame.draw.rect(screen, LINES, GetShip(sp['ship']), ships_wh)
                elif send_data['move'] == 'fin build' or input_data['move'] == 'fin build':
                    if is_adm:
                        send_data['move'] = random.choice([me, not_me])
                    else:
                        send_data['move'] = None
    for n, er in enumerate(ERRORS):
        if Settings['Sound']['Notification']:
            Sounds['info_sound'].set_volume(Settings['Sound']['Notification'])
            Sounds['info_sound'].play()
        Notifications.add(Notification(
            (size[0] // 2 - size[0] * 0.4 // 2, size[1] * 0.07, size[0] * 0.4, size[1] * 0.1),
            er, (86, 86, 86), (0, 0, 0), (255, 255, 255)))
        del ERRORS[n]
    for n, s in enumerate(reversed(Notifications.sprites())):
        if not n:
            if s.update(NotificationLeftPress):
                NotificationLeftPress = False
        else:
            if s.update(False):
                NotificationLeftPress = False
    Notifications.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
if sock:
    sock.close()

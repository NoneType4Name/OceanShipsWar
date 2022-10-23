import sys
import os
import copy
import json
import time
import random
import socket
import psutil
import pygame
import requests
import win32gui
import threading
import Reg as reg
import subprocess
from log import log
import win32process
import win32com.client
from ctypes import windll
from ast import literal_eval
from screeninfo import get_monitors
from urllib.parse import urlparse, parse_qs
from netifaces import interfaces, ifaddresses, AF_INET
from Gui import *
pygame.init()
pygame.font.init()
try:
    pygame.mixer.init()
    INIT_SOUND = True
except pygame.error:
    INIT_SOUND = False


class DATA(dict):
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))
        super().__init__(data)

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return DATA(value) if isinstance(value, dict) else value


def get_hwnd_by_pid(pid):
    hwnd = []
    win32gui.EnumWindows(lambda hw, null: hwnd.append(
        hw if ((win32process.GetWindowThreadProcessId(hw)[1] == pid) and (win32gui.IsWindowVisible(hw))) else 0), None)
    return max(hwnd)


def SetForegroundWindow():
    win32com.client.Dispatch("WScript.Shell").SendKeys("%")
    windll.user32.SetForegroundWindow(pygame.display.get_wm_info()['window'])


GAME_PROCESS = psutil.Process(os.getpid())
try:
    CONSOLE_PROCESS = psutil.Process(GAME_PROCESS.ppid())
except Exception:
    CONSOLE_PROCESS = GAME_PROCESS


try:
    os.chdir(sys._MEIPASS)
    main_dir = os.path.dirname(sys.executable)
    isEXE = True
except AttributeError:
    os.chdir(os.path.split(__file__)[0])
    main_dir = os.path.dirname(__file__)
    isEXE = False

link = None
parser = reg.createParser()
GameProperties = reg.getFileProperties(sys.executable)
VERSION = GameProperties.StringFileInfo.ProductVersion
BETA = 1
PRE_RELEASE = 2
RELEASE = 0
CONSOLE_HWND = get_hwnd_by_pid(CONSOLE_PROCESS.pid)


def GetVersionFromString(string_version=VERSION):
    data = int(string_version.replace('.',''))
    version = data//10
    graphic_version = '.'.join(list(str(version)))
    type_version = data % 10
    return DATA({'version':version, 'string_version':graphic_version, 'type': type_version})


LANG_RUS = 'rus'
LANG_ENG = 'end'
LANG_DEFAULT = LANG_RUS
DEFAULT_DICTIONARY = {'start game': 'Создать игру',
                      'join game': 'Присоеденится к игре',
                      'settings': 'Настройки',
                      'theme light': 'Яркая',
                      'theme dark': 'Тёмная',
                      'Sound': 'Звук',
                      'Sound Game': 'Звуки игры',
                      'Sound Notification': 'Звуки уведомлений',
                      'Graphic': 'Графика',
                      'Graphic Language': 'Язык',
                      'Language List': ['русский', 'english'],
                      'Graphic WindowSize': 'Размер окна',
                      'Exit': 'Выход',
                      'version': f'Версия $VERSION%',
                      'Game random build': 'Случайная расстановка',
                      'Game clear map': 'Очистить карту',
                      'Graphic Font': 'Шрифт',
                      'Graphic Theme': 'Тема',
                      'Theme List': ['тёмная', 'яркая'],
                      'Other': 'Другое',
                      'Other Console': 'Консоль отладки',
                      'Other Links': 'Глубокие ссылки',
                      'Letters': 'АБВГДЕЁЖЗИ',
                      }


RUN = True
GAME_NAME = 'OceanShipsWar'
DISPLAY_SIZE = (get_monitors()[0].width, get_monitors()[0].height)
CONSOLE_TITLE = "OceanShipsWar - Debug Console"


GAME_SCENE_INIT = -1
GAME_SCENE_LOAD = 0
GAME_SCENE_MAIN = 1
GAME_SCENE_CREATE = 2
GAME_SCENE_JOIN = 3
GAME_SCENE_SETTINGS = 4

GAME_EVENT_NOTIFICATION = 0
GAME_EVENT_MERGE_SETTINGS = 1
GAME_EVENT_GAME_DEFEAT = 2
GAME_EVENT_GAME_WIN = 3
GAME_EVENT_GAME_START = 4
GAME_EVENT_GAME_END = 5
GAME_EVENT_GAME_CREATE = 6
GAME_EVENT_GAME_JOIN = 7
GAME_EVENT_EDIT_LANGUAGE = 8
GAME_EVENT_EDIT_THEME = 9

GAME_EVENT_NOTIFICATION_TYPE_DEFAULT = 0



DATAS_FOLDER_NAME = 'assets'
ICON_PATH = f'{DATAS_FOLDER_NAME}/ico.png'
FONT_PATH = f'{DATAS_FOLDER_NAME}/default.ttf'


API_HOST = 'localhost'
API_PORT = 9997
API_METHOD_JOIN = 'join'

namespace_args = parser.parse_args()
run_with_links = namespace_args.links if namespace_args.links is not None else True if reg.get_value(reg.HKEY_CLASSES_ROOT, r'osw\shell\open\command', None) else False
size = (int(namespace_args.size.split('x')[0]), int(namespace_args.size.split('x')[1])) if namespace_args.size else DISPLAY_SIZE
theme = float(namespace_args.theme) if namespace_args.theme is not None else 0
lang = namespace_args.lang if namespace_args.lang else LANG_RUS
debug = namespace_args.debug if namespace_args.debug else False
Settings = {
    'Graphic': {
        'WindowSize': size,
        'Language': lang,
        'Font': f'{FONT_PATH}',
        'Theme': 0

    },
    'Sound': {
        'Notification': 1,
        'Game': 1
    },
    'Other': {
        'Links': True if reg.get_value(reg.HKEY_CLASSES_ROOT, r'osw\shell\open\command',
                                       None).data == main_dir and run_with_links else False,
        'Console': debug
    }
}
SoundsList = {
    "info_sound": {"type": 'ogg', 'path': 0},
    "killed_sound": {"type": 'ogg', 'path': 0},
    "missed_sound": {"type": 'ogg', 'path': 0},
    "wounded_sound": {"type": 'ogg', 'path': 0},
}
bsize = int(size[0] // 27.428571428571427)
ships_wh = bsize // 7
left_margin, upper_margin = (size[0] // 2 - bsize * 5), (size[1] // 2 - bsize * 5)

font = pygame.font.Font(FONT_PATH, int(bsize / 1.5))

infoSurface = pygame.Surface((size[0] // 2 // 1.5, upper_margin // 2), pygame.SRCALPHA)


KILLED_SHIP = (60, 60, 60)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)


def _replace_str_var(dictionary):
    for key in dictionary:
        value = dictionary[key]
        if type(value) is str and '$' in value:
            split_by_md = value.split('$')
            for md in split_by_md:
                if '%' in md:
                    md = md.split('%')[0]
                    try:
                        value = value.replace(f'${md}%', eval(md))
                    except NameError:
                        print(f'UNKNOWN VARIABLE:{md}')
        dictionary[key] = value
    return dictionary


class Language(DATA):
    def __init__(self, language, dictionary):
        exemplar_dict = DEFAULT_DICTIONARY
        for key in dictionary:
            exemplar_dict[key] = dictionary[key]
        super().__init__(_replace_str_var(exemplar_dict))
        self.type = language


class Blocks(DATA):
    def __init__(self, language_object: Language):
        letters = language_object.Letters
        blocks = {}
        for num_let in range(len(letters)):
            blocks[str(num_let)] = []
            for num in range(len(letters)):
                blocks[str(num_let)].append(pygame.Rect(left_margin + num_let * bsize, upper_margin + num * bsize, bsize, bsize))
        self.blocks = blocks
        super().__init__(self.blocks)


class Game:
    def __init__(self, screen, language_name, language_dict):
        self.Language = Language(language_name, language_dict)
        self.scene = GAME_SCENE_INIT
        self.screen = screen
        self.notifications = []
        self.MaxLoad = 0
        self.Load = 0
        self.PercentTextLabel = ''
        self.TextLabel = ''
        self.GameEvents = []
        sz_modes = pygame.display.list_modes()
        if size not in sz_modes:
            sz_modes.insert(0, size)
        self.set_for_lists = {
            'Language': dict(zip(['rus', 'eng'], self.Language['Language List'])),
            'WindowSize': dict(zip(sz_modes, [f'{val[0]} x {val[1]}' for val in sz_modes])),
            'Theme': dict(zip([0, 1], self.Language['Theme List']))
        }

    def GameEvent(self, **kwargs):
        self.GameEvents.append(DATA(kwargs))

    def AddNotification(self, notification_text, notification_type):
        self.notifications.append(notification_text)
        self.GameEvent(event=GAME_EVENT_NOTIFICATION, type=notification_type, content=notification_text)

    def SetScene(self, scene):
        self.scene = scene

    def init_files(self, list_of_load, dict_for_loaded_files):
        self.scene = GAME_SCENE_INIT
        self.MaxLoad = 0
        self.Load = 0
        self.PercentTextLabel = ''
        self.TextLabel = ''
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAITARROW)
        while RUN:
            self.TextLabel = 'Подключение...'
            try:
                requests.get('https://api.github.com/repos/NoneType4Name/OceanShipsWar/releases/latest')
                self.TextLabel = ''
                break
            except requests.exceptions.ConnectionError:
                pass
        self.MaxLoad = len(list_of_load)*2
        for var in list_of_load:
            self.TextLabel = f'Search: ./{DATAS_FOLDER_NAME}/{var}'
            while RUN:
                if os.path.exists(f'./{DATAS_FOLDER_NAME}/{var}.{list_of_load[var]["type"]}'):
                    self.MaxLoad += 1
                    break
                elif os.path.exists(f'{main_dir}/{var}.{list_of_load[var]["type"]}'):
                    list_of_load[var]['path'] = 1
                    self.MaxLoad += 1
                    break
        for var in list_of_load:
            self.TextLabel = f'Load: ./{DATAS_FOLDER_NAME}/{var}'
            if list_of_load[var]['path']:
                dict_for_loaded_files[var] = pygame.mixer.Sound(f'{main_dir}/{DATAS_FOLDER_NAME}/{var}.{list_of_load[var]["type"]}')
            else:
                dict_for_loaded_files[var] = pygame.mixer.Sound(f'./{DATAS_FOLDER_NAME}/{var}.{list_of_load[var]["type"]}')
            self.Load += 1
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


blocks = Blocks(Language(LANG_RUS, DEFAULT_DICTIONARY))

import glob
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
from constants import *
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
            try:
                setattr(self, name, self._wrap(value))
            except TypeError:
                break
        super().__init__(data)

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return DATA(value) if isinstance(value, dict) else value


class SIZE(tuple):
    def __init__(self, data):
        self.w = data[0]
        self.h = data[1]


def read_dictionary(exemplar_dict, dictionary):
    for key in dictionary:
        exemplar_dict[key] = dictionary[key]
    return exemplar_dict


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
                        log.debug(f'UNKNOWN VARIABLE:{md}')
        dictionary[key] = value
    return dictionary


class Language(DATA):
    def __init__(self, languages, dictionaries, default_language):
        langs_dict = {}
        for language, dictionary in zip(languages, dictionaries):
            exemplar_dict = DEFAULT_DICTIONARY
            for key in dictionary:
                exemplar_dict[key] = dictionary[key]
            langs_dict[language] = _replace_str_var(exemplar_dict)
        super().__init__(langs_dict)
        self.LanguageList = list(languages)
        self.DefaultLanguage = default_language


def get_hwnd_by_pid(pid):
    hwnd = []
    win32gui.EnumWindows(lambda hw, null: hwnd.append(
        hw if ((win32process.GetWindowThreadProcessId(hw)[1] == pid) and (win32gui.IsWindowVisible(hw))) else 0), None)
    return max(hwnd)


GAME_PROCESS = psutil.Process(os.getpid())
try:
    CONSOLE_PROCESS = psutil.Process(GAME_PROCESS.ppid())
except Exception:
    CONSOLE_PROCESS = GAME_PROCESS


if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)
    MAIN_DIR = os.path.dirname(sys.executable)
    isEXE = True
else:
    os.chdir(os.path.split(__file__)[0])
    MAIN_DIR = os.path.dirname(__file__)
    isEXE = False


CONSOLE_HWND = get_hwnd_by_pid(CONSOLE_PROCESS.pid)


def GetVersionFromString(string_version):
    data = int(string_version.replace('.',''))
    version = data//10
    graphic_version = '.'.join(list(str(version)))
    type_version = data % 10
    return DATA({'version':version, 'string_version':graphic_version, 'type': type_version})


class Blocks(DATA):
    def __init__(self, language_object: Language, left_margin, upper_margin, block_size):
        letters = language_object.Letters
        blocks = {}
        for num_let in range(len(letters)):
            blocks[str(num_let)] = []
            for num in range(len(letters)):
                blocks[str(num_let)].append(pygame.Rect(left_margin + num_let * block_size, upper_margin + num * block_size, block_size, block_size))
        self.blocks = blocks
        super().__init__(self.blocks)


class Game:
    def __init__(self, settings: DATA, language: Language, colors: DATA):
        self.size = None
        self.screen = None
        self.block_size = None
        self.Language = language
        self.Settings = settings
        self.Colors = colors
        self.SCENE = GAME_SCENE_INIT
        self.Notifications = []
        self.GameEvents = []
        self.Properties = reg.getFileProperties(sys.executable)
        self.VERSION = GameProperties.StringFileInfo.ProductVersion

    def init(self, caption, icon_path, size, flag):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode(size, flag)
        self.size = size
        pygame.display.set_icon(pygame.image.load(icon_path))
        pygame.display.set_caption(caption)
        self.block_size = int(size.w // BLOCK_ATTITUDE)

    def GameEvent(self, **kwargs):
        self.GameEvents.append(DATA(kwargs))

    def AddNotification(self, notification_text, notification_type):
        self.Notifications.append(notification_text)
        self.GameEvent(event=GAME_EVENT_NOTIFICATION, type=notification_type, content=notification_text)

    def SetScene(self, scene):
        self.SCENE = scene
        self.GameEvent(events=GAME_EVENT_MERGE_SCENE)

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
                elif os.path.exists(f'{MAIN_DIR}/{var}.{list_of_load[var]["type"]}'):
                    list_of_load[var]['path'] = 1
                    self.MaxLoad += 1
                    break
        for var in list_of_load:
            self.TextLabel = f'Load: ./{DATAS_FOLDER_NAME}/{var}'
            if list_of_load[var]['path']:
                dict_for_loaded_files[var] = pygame.mixer.Sound(f'{MAIN_DIR}/{DATAS_FOLDER_NAME}/{var}.{list_of_load[var]["type"]}')
            else:
                dict_for_loaded_files[var] = pygame.mixer.Sound(f'./{DATAS_FOLDER_NAME}/{var}.{list_of_load[var]["type"]}')
            self.Load += 1
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


# blocks = Blocks(Language(LANG_RUS, DEFAULT_DICTIONARY))

# DARK_KIT_FOR_LABEL = ((41, 42, 43), (232, 234, 236), [(255, 255, 255), (91, 92, 93)])
# DARK_KIT_FOR_BUTTON = (41, 42, 43), (41, 42, 43), (232, 234, 236), (255, 255, 255), (91, 92, 93), (232, 234, 236)
# DARK_KIT_FOR_RED_BUTTON = ((255, 0, 0, 20), (255, 0, 0, 20), (232, 234, 236), (255, 255, 255), (255, 0, 0), (232, 234, 236))
# DARK_KIT_FOR_SELECTED_BUTTON = ((255, 255, 255), (91, 92, 93), (232, 234, 236), (255, 255, 255), (91, 92, 93), (232, 234, 236))
# DARK_KIT_FOR_SWITCH = ((0, 255, 0), (255, 255, 255), (64, 64, 64))
# DARK_KIT_FOR_SLIDE = ((138, 180, 248), (53, 86, 140))
# DARK_KIT_FOR_LIST =  ((232, 234, 236), (29, 29, 31), (41, 42, 45))
# DARK_KIT_FOR_PATH = ((138, 180, 248), (53, 86, 140),(232, 234, 236))
#
# LIGHT_KIT_FOR_LABEL = ((214, 213, 212), (23, 21, 19), [(0, 0, 0), (200, 200, 200)])
# LIGHT_KIT_FOR_BUTTON = ((214, 213, 212), (214, 213, 212), (23, 21, 19), (0, 0, 0), (164, 163, 162), (23, 21, 19))
# LIGHT_KIT_FOR_RED_BUTTON = ((255, 0, 0, 20), (255, 0, 0, 20), (232, 234, 236), (255, 255, 255), (255, 0, 0), (232, 234, 236))
# LIGHT_KIT_FOR_SELECTED_BUTTON = ((255, 255, 255), (91, 92, 93), (232, 234, 236), (255, 255, 255), (91, 92, 93), (232, 234, 236))
# LIGHT_KIT_FOR_SWITCH = ((0, 255, 0), (255, 255, 255), (64, 64, 64))
# LIGHT_KIT_FOR_SLIDE = ((138, 180, 248), (53, 86, 140))
# LIGHT_KIT_FOR_LIST =  ((232, 234, 236), (29, 29, 31), (41, 42, 45))
# LIGHT_KIT_FOR_PATH = ((138, 180, 248), (53, 86, 140),(232, 234, 236))


# Settings = {
#     'Graphic': {
#         'WindowSize': {'value': size, 'type': List, 'values': dict(zip(LANGUAGES, Language.LanguageList))},
#         'Language': {'value': lang, 'type': List, 'values': dict(zip(sz_modes, [f'{val[0]} x {val[1]}' for val in sz_modes]))},
#         'Font': {'value': f'{FONT_PATH}', 'type': Path, 'title': 'Select Font (ttf)...', 'multiple': 0,
#                  'types': ['*.ttf']},
#         'Theme': {'value': theme, 'type': List, 'values': dict(zip(THEMES, Language.ThemeList))}
#
#     },
#     'Sound': {
#         'Notification': {'value': 1, 'type': Slide},
#         'Game': {'value': 1, 'type': Slide}
#     },
#     'Other': {
#         'Links': {'value': True if reg.get_value(reg.HKEY_CLASSES_ROOT, r'osw\shell\open\command',
#                                                  None).data == MAIN_DIR and run_with_links else False,
#                   'type': Switch},
#         'Console': {'value': debug, 'type': Switch}}
# }

# Game = Game(Settings)

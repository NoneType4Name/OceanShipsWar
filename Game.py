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
from svglib.svglib import svg2rlg
from screeninfo import get_monitors
from urllib.parse import urlparse, parse_qs
from reportlab.graphics import renderPM
from netifaces import interfaces, ifaddresses, AF_INET
from Gui import *


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
        self.RUN = False
        pygame.init()
        pygame.font.init()
        self.size = None
        self.flag = None
        self.depth = None
        self.display = None
        self.vsync = None
        self.caption = None
        self.screen = None
        self.block_size = None

        self.Language = language
        self.Settings = settings
        self.Colors = colors
        self.Sounds = {}
        self.SOUND = False
        self.SCENE = GAME_SCENE_INIT

        self.Notifications = []
        self.GameEvents = []
        self.Properties = reg.getFileProperties(sys.executable)
        self.VERSION = self.Properties.StringFileInfo.ProductVersion
        if hasattr(sys, '_MEIPASS'):
            os.chdir(sys._MEIPASS)
            self.MAIN_DIR = os.path.dirname(sys.executable)
            self.EXE = True
        else:
            os.chdir(os.path.split(__file__)[0])
            self.MAIN_DIR = os.path.dirname(__file__)
            self.EXE = False

    def init(self, caption: str, icon_path: str, size: SIZE, flag: int, depth=0, display=0, vsync=0):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.size = size
        self.flag = flag
        self.depth = depth
        self.display = display
        self.vsync = vsync
        self.caption = caption
        self.screen = pygame.display.set_mode(self.size, self.flag, self.depth)
        pygame.display.set_icon(pygame.image.load(icon_path))
        pygame.display.set_caption(caption)
        self.block_size = int(size.w // BLOCK_ATTITUDE)
        self.RUN = True
        self.MixerInit()

    def MixerInit(self):
        if not self.SOUND:
            try:
                pygame.mixer.init()
                self.SOUND = True
            except pygame.error:
                self.SOUND = False
        if self.SOUND:



    def GameEvent(self, **kwargs):
        event = DATA(kwargs)
        self.GameEvents.append(event)

    def AddNotification(self, notification_text, notification_type):
        self.Notifications.append(notification_text)
        self.GameEvent(event=GAME_EVENT_NOTIFICATION, type=notification_type, content=notification_text)

    def SetScene(self, scene):
        self.SCENE = scene
        self.GameEvent(events=GAME_EVENT_MERGE_SCENE, scene=scene)

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

class LoadScene:
    def __init__(self, parent: Game, func_to_thread, *args):
        self.ProgressBar = ProgressBar(None,
                                       (parent.size.w * 0.4, parent.size.h * 0.7, parent.size.w * 0.2, parent.size.h * 0.05),
                                       *parent.Colors.ProgressBar, value=0)
        threading.Thread(func_to_thread, args=[self, parent, args])
        self.image = pygame.Surface(parent.size, parent.flag)

    def update(self):
        return


def InitSound(self:LoadScene, parent: Game):
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAITARROW)
    while parent.RUN:


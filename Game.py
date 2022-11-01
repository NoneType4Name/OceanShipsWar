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

    def __getattr__(self, item):
        print(item)
        return self.get(str(item))

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


def _replace_str_var(dictionary, self=None):
    str_dict = str(dictionary)
    if '$' in str_dict:
        split_by_md = str_dict.split('$')
        for md in split_by_md:
            if '%' in md:
                md = md.split('%')[0]
                try:
                    if self is not None:
                        str_dict = str_dict.replace(f'${md}%', getattr(self, md))
                    else:
                        str_dict = str_dict.replace(f'${md}%', eval(md))
                except NameError:
                    log.debug(f'UNKNOWN VARIABLE: {self}.{md}')
    return literal_eval(str_dict)


class Language(DATA):
    def __init__(self, languages, dictionaries, default_language, replace_str_to_var=True):
        langs_dict = {}
        for language, dictionary in zip(languages, dictionaries):
            exemplar_dict = DEFAULT_DICTIONARY
            for key in dictionary:
                exemplar_dict[key] = dictionary[key]
            if replace_str_to_var:
                langs_dict[language] = _replace_str_var(exemplar_dict)
            else:
                langs_dict[language] = exemplar_dict
        super().__init__(langs_dict)
        self.LanguageList = list(languages)
        self.DefaultLanguage = default_language
        self.DefaultDict = DATA(langs_dict[default_language])


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
    def __init__(self, settings: DATA, language: Language, colors: DATA, main_dir: str, exe: bool):
        self.RUN = False
        pygame.font.init()
        self.size = None
        self.flag = None
        self.depth = None
        self.display = None
        self.vsync = None
        self.caption = None
        self.screen = None
        self.clock = pygame.time.Clock()
        self.block_size = None

        self.Settings = settings
        self.Colors = colors
        self.Sounds = {}
        self.SOUND = False
        self.SCENE = None

        self.Notifications = []
        self.GameEvents = []
        self.Properties = reg.getFileProperties(sys.executable)
        self.VERSION = self.Properties.StringFileInfo.ProductVersion
        self.MAIN_DIR = main_dir
        self.EXE = exe
        self.Language = DATA(_replace_str_var(language.__dict__, self))
        self.Scene = DATA(
            {
                INIT:InitScene,
                MAIN:MainScene,
                LOAD:LoadScene,
                CREATE:None,
                JOIN:None,
                SETTINGS:None
            })
        self.ConvertScene = None

    def init(self, caption: str, icon_path: str, size: SIZE, flag=0, depth=0, display=0, vsync=0):
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
        self.SCENE = self.Scene[MAIN](self, self.Scene[INIT])
        self.ConvertScene = ConvertScene(self, self.SCENE, self.Scene[scene], kwargs)
        self.RUN = True

    def MixerInit(self, frequency=44100, size=-16, channels=2, buffer=512, devicename='', allowedchanges=5):
        self.SetScene(LOAD,
                      frequency=frequency,
                      size=size,
                      channels=channels,
                      buffer=buffer,
                      devicename=devicename,
                      allowedchanges=allowedchanges
                      )

    def mixer_init_thread(self, scene, kwargs):
        if not self.SOUND:
            try:
                pygame.mixer.init(*kwargs.values())
                self.SOUND = True
            except pygame.error:
                self.SOUND = False
        if self.SOUND:
            Load = 0
            scene.PercentLabel.value = ''
            scene.TextLabel.value = ''
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAITARROW)
            while self.RUN:
                scene.TextLabel.value = 'Подключение...'
                try:
                    requests.get(GITHUB_REPOS_URL+'releases/latest')
                    scene.TextLabel.value = ''
                    break
                except requests.exceptions.ConnectionError:
                    pass
            MaxLoad = len(SoundsDict)*2

            for sound_name in SoundsDict:
                scene.TextLabel.value = f'Search: ./{DATAS_FOLDER_NAME}/{sound_name}'
                while self.RUN:
                    if os.path.exists(f'./{DATAS_FOLDER_NAME}/{sound_name}.{SoundsDict[sound_name]["type"]}'):
                        Load += 1
                        break
                    elif os.path.exists(f'{self.MAIN_DIR}/{sound_name}.{SoundsDict[sound_name]["type"]}'):
                        SoundsDict[sound_name]['path'] = 1
                        Load += 1
                        break
                scene.ProgressBar.value = Load / MaxLoad
                scene.PercentLabel.value = f'{Load / MaxLoad * 100} %'

            for sound_name in SoundsDict:
                scene.TextLabel.value = f'Load: ./{DATAS_FOLDER_NAME}/{sound_name}'
                if SoundsDict[sound_name]['path']:
                    self.Sounds[sound_name] = pygame.mixer.Sound(
                        f'{self.MAIN_DIR}/{DATAS_FOLDER_NAME}/{sound_name}.{SoundsDict[sound_name]["type"]}')
                else:
                    self.Sounds[sound_name] = pygame.mixer.Sound(
                        f'./{DATAS_FOLDER_NAME}/{sound_name}.{SoundsDict[sound_name]["type"]}')
                Load += 1
                scene.ProgressBar.value = Load / MaxLoad
                scene.PercentLabel.value = f'{Load / MaxLoad * 100} %'

            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return True

    # def GameEvent(self, **kwargs):
    #     event = DATA(kwargs)
    #     self.GameEvents.append(event)

    def AddNotification(self, notification_text):
        self.Notifications.append(notification_text)

    def SetScene(self, scene, **kwargs):
        self.Scene[self.SCENE.type] = self.SCENE
        self.SCENE = ConvertScene(self, self.SCENE, self.Scene[scene], kwargs)

    def update(self):
        self.screen.blit(self.SCENE.update(), (0, 0))
        pygame.display.flip()
        self.clock.tick(GAME_FPS)


class ConvertScene:
    def __init__(self, parent: Game, old, new, kwargs):
        self.old = old
        self.parent = parent
        self.new = new(parent, self.old, kwargs)
        self.old_alpha = 255
        self.new_alpha = 0
        self.step = SPEED_MERGE_SCENE
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)

    def NewScene(self, new, kwargs):
        self.old = self.new
        self.new = new(self.parent, self.old, kwargs)
        self.old_alpha = 255
        self.new_alpha = 0
        self.image = pygame.Surface(self.parent.size, pygame.SRCALPHA)

    def update(self):
        if self.old_alpha - self.step > 0 and self.new_alpha + self.step < 255:
            self.new_alpha += self.step
            self.old_alpha -= self.step
        elif self.old_alpha and self.new_alpha != 255:
            self.old_alpha = 0
            self.new_alpha = 255
        if self.old_alpha:
            image_old = self.old.update()
            image_old.set_alpha(self.old_alpha)
            self.image.blit(image_old, (0, 0))
        image_new = self.new.update()
        image_new.set_alpha(self.new_alpha)
        self.image.blit(image_new, (0, 0))
        return self.image


class InitScene:
    def __init__(self, parent: Game):
        self.type = INIT
        self.parent = parent
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)

    def update(self):
        self.image.fill(self.parent.Colors.Background)
        return self.image


class LoadScene:
    def __init__(self, parent: Game, input_scene, func_to_thread=None, **kwargs):
        self.type = LOAD
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)
        self.InputScene = input_scene.type
        self.parent = parent
        self.func = func_to_thread
        self.kwargs = kwargs
        self.Thread = None
        self.ProgressBar = ProgressBar(None,
                                       (parent.size.w * 0.4, parent.size.h * 0.7,
                                        parent.size.w * 0.2, parent.size.h * 0.05),
                                       *parent.Colors.Scene.Load.ProgressBar,
                                       value=0
                                       )
        self.PercentLabel = Label(FONT_PATH,
                                  (parent.size[0] * 0.4, parent.size[1] * 0.6,
                                   parent.size[0] * 0.2, parent.size[1] * 0.05),
                                  '0 %',
                                  *parent.Colors.Scene.Load.Label,
                                  center=True
                                  )
        self.TextLabel = Label(FONT_PATH,
                               (parent.size[0] * 0.4, parent.size[1] * 0.65,
                                parent.size[0] * 0.2, parent.size[1] * 0.05),
                               '',
                               *parent.Colors.Scene.Load.Label,
                               center=True)
        self.Elements = pygame.sprite.Group([self.ProgressBar, self.PercentLabel, self.TextLabel])
        if self.func:
            self.Thread = threading.Thread(target=self.func, args=[self, self.parent, self.kwargs])
        else:
            self.Thread = threading.Thread(target=self.parent.mixer_init_thread(self, self.kwargs))
        self.Thread.start()

    def update(self):
        self.image.fill(self.parent.Colors.Background)
        self.Elements.update()
        self.Elements.draw(self.image)
        if not self.Thread.is_alive():
            self.parent.SetScene(self.InputScene)
        return self.image


class MainScene:
    def __init__(self, parent: Game, input_scene):
        self.type = MAIN
        self.parent = parent
        self.InputScene = input_scene
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)
        self.ButtonUpdate = Button(FONT_PATH,
                                   (-1, parent.size.h - parent.block_size * 0.5,
                                    parent.block_size * 2, parent.block_size * 0.5),
                                   parent.Language.DefaultDict.Version, *parent.Colors.Scene.Main.Button)
        self.ButtonEsc = Button(FONT_PATH,
                                (-1, -1,
                                 parent.block_size * 0.75, parent.block_size * 0.5),
                                'ESC', *parent.Colors.Scene.Main.Button)
        self.ButtonCreateGame = Button(FONT_PATH,
                                       (parent.size.w * 0.42, parent.size.h * 0.2,
                                        parent.size.w * 0.16, parent.size.h * 0.1),
                                       parent.Language.DefaultDict.StartGame, *parent.Colors.Scene.Main.Button)
        self.ButtonJoinGame = Button(FONT_PATH,
                                     (parent.size.w * 0.42, parent.size.h * 0.4,
                                      parent.size.w * 0.16, parent.size.h * 0.1),
                                     parent.Language.DefaultDict.JoinGame, *parent.Colors.Scene.Main.Button)
        self.ButtonSettings = Button(FONT_PATH,
                                     (parent.size.w * 0.42, parent.size.h * 0.6,
                                      parent.size.w * 0.16, parent.size.h * 0.1),
                                     parent.Language.DefaultDict.Settings, *parent.Colors.Scene.Main.Button)
        self.ButtonTheme = Button(FONT_PATH,
                                  (parent.size.w - parent.block_size * 1.5, parent.size.h - parent.block_size * 1.5,
                                   parent.block_size, parent.block_size),
                                  parent.Language.DefaultDict.ThemeLight if parent.Settings.Graphic.Theme is THEME_LIGHT else parent.Language.DefaultDict.ThemeDark, *parent.Colors.Scene.Main.Button)
        self.Elements = pygame.sprite.Group(self.ButtonUpdate, self.ButtonEsc, self.ButtonCreateGame, self.ButtonJoinGame, self.ButtonSettings, self.ButtonTheme)

    def update(self):
        self.image.fill(self.parent.Colors.Background)
        self.Elements.update()
        self.Elements.draw(self.image)
        return self.image

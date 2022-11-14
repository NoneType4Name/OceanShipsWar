import glob
import sys
import os
import copy
import json
import threading
import time
import random
import socket
import psutil
import pygame
import requests
import win32gui
import Reg as reg
import subprocess

from log import log
import win32process
import win32com.client
from constants import *
from ctypes import windll
from scene.Settings import *
from ast import literal_eval
from scene.Menu import MainScene
from scene.Load import LoadScene
from screeninfo import get_monitors
from scene.JoinGame import JoinGame
from scene.Converter import ConvertScene
from scene.CreateGame import CreateGame
from scene.Notification import Notifications
from urllib.parse import urlparse, parse_qs
from netifaces import interfaces, ifaddresses, AF_INET


class DATA(dict):
    def __init__(self, data):
        for name, value in data.items():
            try:
                setattr(self, name, self._wrap(value))
            except TypeError:
                break
        super().__init__(data)

    def __getattr__(self, item):
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
                    log.error(f'UNKNOWN VARIABLE: {self}.{md}')
    return literal_eval(str_dict)


class Language(DATA):
    def __init__(self, dict_of_all_languages: dict, default_language, replace_str_to_var=True):
        langs_dict = {}
        for language in dict_of_all_languages:
            dictionary = dict_of_all_languages[language]
            exemplar_dict = copy.deepcopy(DEFAULT_DICTIONARY)
            for key in dictionary:
                exemplar_dict[key] = dictionary[key]
            if replace_str_to_var:
                langs_dict[language] = _replace_str_var(exemplar_dict)
            else:
                langs_dict[language] = exemplar_dict
        super().__init__(langs_dict)
        self.LanguageList = list(dict_of_all_languages.keys())
        self.DefaultLanguage = default_language
        self.DefaultDict = DATA(langs_dict[default_language])


def get_hwnd_by_pid(pid):
    hwnd = []
    win32gui.EnumWindows(lambda hw, null: hwnd.append(
        hw if ((win32process.GetWindowThreadProcessId(hw)[1] == pid) and (win32gui.IsWindowVisible(hw))) else 0), None)
    return max(hwnd)


def LoadNewVersion(parent, version):
    scene = parent.ConverScene.new
    b = 0
    scene.ProgressBar = 0
    scene.PercentLabel = '0%'
    scene.TextLabel = 'Connecting...'
    while True:
        file = requests.get(
            f'https://github.com/NoneType4Name/OceanShipsWar/releases/latest/download/OceanShipsWar.exe',
            stream=True)
        scene.TextLabel = 'Load content...'
        break
    with open(fr'{parent.MAIN_DIR}\OceanShipsWar {version}.exe', 'wb') as f:
        for chunk in file.iter_content(8):
            f.write(chunk)
            b += 8
            scene.PercentLabel = f'{b / file.headers["Content-Length"]}%'
            scene.PercentLabel = b / file.headers['Content-Length']
    parent.AddNotification('Launch update?.')
    if (windll.user32.MessageBoxW(parent.GAME_HWND,
                                  f"Запустить файл OceanShipsWar {version}.exe?",
                                  f"Запустить", 36)) == 6:
        subprocess.Popen(fr'{parent.MAIN_DIR}\OceanShipsWar {version}.exe')
        parent.RUN = False


class Version:
    def __init__(self, string_version: str):
        self.major, self.minor, self.micro, self.type = map(int, string_version.split('.'))
        st = string_version.split('.')[:-1]
        try:
            str_type = VERSIONS[int(self.type)]
        except KeyError:
            str_type = str(self.type)
        self.string_version = '.'.join(st) + str_type

    def __gt__(self, other):
        if type(other) is not Version:
            other = Version(other)
        return sum([self.major, self.minor, self.micro, self.type]) > sum(
            [other.major, other.minor, other.micro, other.type])

    def __lt__(self, other):
        if type(other) is not Version:
            other = Version(other)
        return sum([self.major, self.minor, self.micro, self.type]) < sum(
            [other.major, other.minor, other.micro, other.type])


class Blocks(DATA):
    def __init__(self, language_object: Language, left_margin, upper_margin, block_size):
        letters = language_object.Letters
        blocks = {}
        for num_let in range(len(letters)):
            blocks[str(num_let)] = []
            for num in range(len(letters)):
                blocks[str(num_let)].append(
                    pygame.Rect(left_margin + num_let * block_size, upper_margin + num * block_size, block_size,
                                block_size))
        self.blocks = blocks
        super().__init__(self.blocks)


class Game:
    def __init__(self, settings: DATA, language: Language, colors: DATA, main_dir: str, exe: bool, debug=False):
        pygame.font.init()
        self.mouse_pos = (0, 0)
        self.mouse_right_press = False
        self.mouse_right_release = False
        self.mouse_left_press = False
        self.mouse_left_release = False
        self.mouse_middle_press = False
        self.mouse_middle_release = False
        self.mouse_wheel_x = 0
        self.mouse_wheel_y = 0
        self.cursor = pygame.SYSTEM_CURSOR_ARROW
        self.events = []

        self.FPS = GAME_FPS

        self.CONSOLE_HWND = None
        self.CONSOLE_PROCESS = None
        self.GAME_HWND = None
        self.GAME_PROCESS = None
        self.RUN = False
        self.size = None
        self.flag = None
        self.depth = None
        self.display = None
        self.vsync = None
        self.caption = None
        self.screen = None
        self.clock = pygame.time.Clock()
        self.block_size = None
        self.debug = debug

        self.Settings = settings
        self.Colors = colors
        self.Sounds = {SOUND_TYPE_NOTIFICATION:{},
                       SOUND_TYPE_GAME:{}
                       }
        self.SOUND = False

        self.Notifications = pygame.sprite.Group()
        self.GameEvents = []
        self.Properties = reg.getFileProperties(sys.executable)
        self.version = Version(str(self.Properties.FileVersion))
        self.VERSION = self.version.string_version
        self.MAIN_DIR = main_dir
        self.EXE = exe
        self.Language = DATA(_replace_str_var(language.__dict__, self))
        self.Scene = DATA(
            {
                INIT: InitScene,
                MAIN: MainScene,
                LOAD: LoadScene,
                CREATE: CreateGame,
                JOIN: JoinGame,
                SETTINGS: Settings
            })
        self.ConvertScene = ConvertScene(self, self.Scene[INIT])
        self.ConvertSceneThread = threading.Thread(target=lambda _:True)

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
        pygame.scrap.init()
        self.block_size = int(size.w // BLOCK_ATTITUDE)
        self.GAME_PROCESS = psutil.Process(os.getpid())
        try:
            self.CONSOLE_PROCESS = psutil.Process(self.GAME_PROCESS.ppid())
        except Exception:
            self.CONSOLE_PROCESS = self.GAME_PROCESS
        self.GAME_HWND = pygame.display.get_wm_info()['window']
        self.CONSOLE_HWND = get_hwnd_by_pid(self.CONSOLE_PROCESS.pid)
        self.ConsoleOC()
        self.RUN = True
        self.ConvertScene.NewScene(self.Scene[INIT], None)

    def MixerInit(self, frequency=44100, size=-16, channels=2, buffer=512, devicename='', allowedchanges=5):
        self.SetScene(LOAD,
                      parent=MAIN,
                      frequency=frequency,
                      size=size,
                      channels=channels,
                      buffer=buffer,
                      devicename=devicename,
                      allowedchanges=allowedchanges
                      )

    def mixer_init_thread(self, scene, kwargs):
        try:
            pygame.mixer.init(*list(kwargs.values()))
        except pygame.error:
            pass

        if pygame.mixer.get_init():
            Load = 0
            scene.PercentLabel.value = ''
            scene.TextLabel.text = ''
            while self.RUN:
                scene.TextLabel.text = 'Подключение...'
                try:
                    requests.get(GITHUB_REPOS_URL + 'releases/latest')
                    scene.TextLabel.text = ''
                    break
                except requests.exceptions.ConnectionError:
                    pass

            MaxLoad = len(list(itertools.chain(*SoundsDict.values()))) * 2
            for sound_type in SoundsDict:
                for sound_name in SoundsDict[sound_type]:
                    scene.TextLabel.text = f'Search: {os.path.join(".", SOUNDS_DIR, sound_type, sound_name+"."+SOUNDS_TYPE)}'
                    while self.RUN:
                        if os.path.exists(f'{os.path.join(".", DATAS_FOLDER_NAME, SOUNDS_DIR, sound_type, sound_name+"."+SOUNDS_TYPE)}'):
                            Load += 1
                            break
                        elif os.path.exists(f'{os.path.join(self.MAIN_DIR, DATAS_FOLDER_NAME, SOUNDS_DIR, sound_type, sound_name+"."+SOUNDS_TYPE)}'):
                            SoundsDict[sound_type][sound_name] = 1
                            Load += 1
                            break
                    scene.ProgressBar.value = Load / MaxLoad
                    scene.PercentLabel.text = f'{round(Load / MaxLoad * 100)}%'

            for sound_type in SoundsDict:
                for sound_name in SoundsDict[sound_type]:
                    scene.TextLabel.text = f'Load: ./{os.path.join(SOUNDS_DIR, sound_type, sound_name+"."+SOUNDS_TYPE)}'
                    if SoundsDict[sound_type][sound_name]:
                        sound = pygame.mixer.Sound(f'{os.path.join(self.MAIN_DIR, DATAS_FOLDER_NAME, SOUNDS_DIR, sound_type, sound_name+"."+SOUNDS_TYPE)}')
                    else:
                        sound = pygame.mixer.Sound(f'{os.path.join(DATAS_FOLDER_NAME, SOUNDS_DIR, sound_type, sound_name+"."+SOUNDS_TYPE)}')
                    self.Sounds[sound_type][sound_name] = sound
                    Load += 1
                    scene.ProgressBar.value = Load / MaxLoad
                    scene.PercentLabel.text = f'{round(Load / MaxLoad * 100)}%'
            self.Sounds = DATA(self.Sounds)
            self.SOUND = True
            return

    def GameEvent(self, **kwargs):
        event = DATA(kwargs)
        self.GameEvents.append(event)

    def AddNotification(self, notification_text):
        self.Notifications.add(Notification(FONT_PATH, (self.size[0] * 0.3, self.size[1] * 0.07,
                                                        self.size[0] * 0.4, self.size[1] * 0.1),
                                            notification_text, (86, 86, 86), (0, 0, 0), (255, 255, 255)))
        self.PlaySound(SOUND_TYPE_NOTIFICATION, 'in')

    def PlaySound(self, sound_type: str, sound_name: str, loops=0, maxtime=0, fade_ms=0):
        if self.SOUND:
            if sound_type == SOUND_TYPE_NOTIFICATION and self.Settings.Sound.Notification:
                self.Sounds[SOUND_TYPE_NOTIFICATION][sound_name].set_volume(self.Settings.Sound.Notification.value)
                self.Sounds[SOUND_TYPE_NOTIFICATION][sound_name].play(loops, maxtime, fade_ms)
            elif sound_type == SOUND_TYPE_GAME and self.Settings.Sound.Game:
                self.Sounds[SOUND_TYPE_GAME][sound_name].set_volume(self.Settings.Sound.Game.value)
                self.Sounds[SOUND_TYPE_GAME][sound_name].play(loops, maxtime, fade_ms)

    def GetUpdate(self):
        possible_version = Version('4.0.0.0')
        # possible_version = Version(json.loads(requests.get('https://api.github.com/repos/NoneType4Name/OceanShipsWar/releases/latest').content)['tag_name'])
        if self.version < possible_version:
            possible_version = json.loads(
                requests.get('https://api.github.com/repos/NoneType4Name/OceanShipsWar/releases/latest').content)[
                'tag_name']
            self.AddNotification('New version is available, load it?')
            if (windll.user32.MessageBoxW(self.GAME_HWND,
                                          f"Доступна версия {possible_version}, продолжить обновление?",
                                          f"Обновление до версии {possible_version}", 36)) == 6:
                self.SetScene(LOAD, func=LoadNewVersion, args=[self, possible_version])
                LoadNewVersion(self, possible_version)
        else:
            self.AddNotification('Actual version.')

    def ConsoleOC(self):
        win32gui.ShowWindow(self.CONSOLE_HWND, 4 if self.debug else 0)
        self.debug = not self.debug

    def SetScene(self, scene, **kwargs):
        self.ConvertScene.NewScene(self.Scene[scene], kwargs)

    def UpdateEvents(self):
        self.mouse_left_release = False
        self.mouse_right_release = False
        self.mouse_middle_release = False

        # self.mouse_left_press = False
        # self.mouse_right_press = False
        # self.mouse_middle_press = False

        self.mouse_wheel_x = 0
        self.mouse_wheel_y = 0

        self.mouse_pos = pygame.mouse.get_pos()
        self.cursor = pygame.SYSTEM_CURSOR_ARROW
        self.events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUN = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    self.mouse_left_press = True
                    self.mouse_left_release = False
                elif event.button == pygame.BUTTON_RIGHT:
                    self.mouse_right_press = True
                    self.mouse_right_release = False
                elif event.button == pygame.BUTTON_MIDDLE:
                    self.mouse_middle_press = True
                    self.mouse_middle_release = False

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    self.mouse_left_press = False
                    self.mouse_left_release = True
                elif event.button == pygame.BUTTON_RIGHT:
                    self.mouse_right_press = False
                    self.mouse_right_release = True
                elif event.button == pygame.BUTTON_MIDDLE:
                    self.mouse_middle_press = False
                    self.mouse_middle_release = True
            elif event.type == pygame.MOUSEWHEEL:
                self.mouse_wheel_x = event.x
                self.mouse_wheel_y = event.y

            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0] or event.touch:
                    self.mouse_wheel_x = event.rel[0]
                    self.mouse_wheel_y = event.rel[1]
            self.events.append(event)

    def update(self):
        self.UpdateEvents()
        if not self.ConvertSceneThread.is_alive():
            self.ConvertSceneThread = threading.Thread(target=self.ConvertScene.update, args=[self.events])
            self.ConvertSceneThread.start()
        self.Notifications.update(self.mouse_left_press)
        # self.screen.blit(self.ConvertScene.update(self.text_input_events), (0, 0))
        self.screen.blit(self.ConvertScene.image, (0, 0))
        pygame.mouse.set_cursor(self.cursor)
        self.Notifications.draw(self.screen)
        pygame.display.flip()
        self.clock.tick(self.FPS)


class InitScene:
    def __init__(self, parent: Game, *kwargs):
        self.type = INIT
        self.parent = parent
        self.image = pygame.Surface((0, 0), pygame.SRCALPHA)

    def update(self, active, events):
        self.image.fill(self.parent.Colors.Background)
        return self.image

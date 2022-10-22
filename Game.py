import Reg as reg
import psutil
import os
import sys
import pygame
import win32gui
import win32process
import win32com.client
from ctypes import windll
from screeninfo import get_monitors
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


def GetVersionFromString(string=VERSION):
    data = int(string.replace('.',''))
    version = data//10
    graphic_version = '.'.join(list(str(version)))
    type_version = data % 10
    return DATA({'version':version, 'string_version':graphic_version, 'type': type_version})


LANG_RUS = 'rus'
LANG_ENG = 'end'
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

GAME_NAME = 'OceanShipsWar'
DISPLAY_SIZE = (get_monitors()[0].width, get_monitors()[0].height)
CONSOLE_TITLE = "OceanShipsWar - Debug Console"

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
        # print(self.blocks)
        super().__init__(self.blocks)


blocks = Blocks(Language(LANG_RUS, DEFAULT_DICTIONARY))

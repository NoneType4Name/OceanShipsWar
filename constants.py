LANG_RUS = 'rus'
LANG_ENG = 'eng'
DEFAULT_LANGUAGE = LANG_RUS

ALPHA = 0
BETA = 1
PRE_RELEASE = 2
RELEASE = 3
VERSIONS = {
    ALPHA:       'a',
    BETA:        'b',
    PRE_RELEASE: 'p',
    RELEASE:     'r'
}

RUS_DICT = {'StartGame': 'Создать игру',
            'JoinGame': 'Присоеденится к игре',
            'Settings': 'Настройки',
            'ThemeLight': 'Яркая',
            'ThemeDark': 'Тёмная',
            'Sound': 'Звук',
            'SoundGame': 'Звуки игры',
            'SoundNotification': 'Звуки уведомлений',
            'Graphic': 'Графика',
            'GraphicLanguage': 'Язык',
            'LanguageList': ['русский', 'english'],
            'GraphicWindowSize': 'Размер окна',
            'Exit': 'Выход',
            'Version': 'Версия $VERSION%',
            'GameRandomBuild': 'Случайная расстановка',
            'GameClearMap': 'Очистить карту',
            'GraphicFont': 'Шрифт',
            'GraphicTheme': 'Тема',
            'ThemeList': ['тёмная', 'яркая'],
            'Other': 'Другое',
            'OtherConsole': 'Консоль отладки',
            'OtherLinks': 'Глубокие ссылки',
            'Letters': 'АБВГДЕЁЖЗИ',
            }

ENG_DICT = {'StartGame': 'Create game',
            'JoinGame': 'Join to game',
            'Settings': 'Settings',
            'ThemeLight': 'Light',
            'ThemeDark': 'Dark',
            'Sound': 'Sound',
            'SoundGame': 'Game Sound',
            'SoundNotification': 'Notifications Sound',
            'Graphic': 'Graphic',
            'GraphicLanguage': 'Language',
            'LanguageList': ['русский', 'english'],
            'GraphicWindowSize': 'Window size',
            'Exit': 'Exit',
            'Version': 'Version $VERSION%',
            'GameRandomBuild': 'Random building',
            'GameClearMap': 'Clear map',
            'GraphicFont': 'Font',
            'GraphicTheme': 'Theme',
            'ThemeList': ['dark', 'light'],
            'Other': 'Other',
            'OtherConsole': 'Debug Console',
            'OtherLinks': 'Deep links',
            'Letters': 'ABCDEFGHIJ'
            }

DEFAULT_LANGUAGES = {LANG_RUS:RUS_DICT, LANG_ENG:ENG_DICT}
DEFAULT_DICTIONARY = DEFAULT_LANGUAGES[DEFAULT_LANGUAGE]

THEME_LIGHT = 1
THEME_DARK = 0
THEMES = [THEME_DARK, THEME_LIGHT]

GAME_NAME = 'OceanShipsWar'
CONSOLE_TITLE = "OceanShipsWar - Debug Console"
GITHUB_REPOS_URL = 'https://api.github.com/repos/NoneType4Name/OceanShipsWar/'

INIT = -1
MAIN = 0
LOAD = 1
CREATE = 2
JOIN = 3
SETTINGS = 4

GAME_EVENT_NOTIFICATION = 0
GAME_EVENT_MERGE_SETTINGS = 1
GAME_EVENT_MERGE_SCENE = 2
GAME_EVENT_GAME_DEFEAT = 3
GAME_EVENT_GAME_WIN = 4
GAME_EVENT_GAME_START = 5
GAME_EVENT_GAME_END = 6
GAME_EVENT_GAME_CREATE = 7
GAME_EVENT_GAME_JOIN = 8
GAME_EVENT_EDIT_LANGUAGE = 9
GAME_EVENT_EDIT_THEME = 10

GAME_EVENT_NOTIFICATION_TYPE_DEFAULT = 0
SOUND_TYPE_NOTIFICATION = 'NOTIFICATION'
SOUND_TYPE_GAME = 'GAME'

SoundsDict = {
    "info": {'type':SOUND_TYPE_NOTIFICATION},
    "kill": {"file_type": 'ogg', 'path': 0, 'type':SOUND_TYPE_GAME},
    "miss": {"file_type": 'ogg', 'path': 0, 'type':SOUND_TYPE_GAME},
    "wound": {"file_type": 'ogg', 'path': 0, 'type':SOUND_TYPE_GAME},
}

DATAS_FOLDER_NAME = 'assets'
GAME_FPS = 60
ICON_PATH = f'{DATAS_FOLDER_NAME}/ico.png'
FONT_PATH = f'{DATAS_FOLDER_NAME}/default.ttf'
LANGUAGE_FILE_MASK = '_language.json'

API_HOST = 'localhost'
API_PORT = 9997
API_METHOD_JOIN = 'join'

BLOCK_ATTITUDE = 27.428571428571427
SHIP_ATTITUDE = 7
COUNT_BLOCKS_X = 10
COUNT_BLOCKS_Y = 10
SPEED_MERGE_SCENE = 50

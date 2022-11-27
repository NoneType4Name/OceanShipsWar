LANG_RUS = 'русский'
LANG_ENG = 'english'
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
            'Settings': 'Настройки',
            'ThemeLight': 'Яркая',
            'ThemeDark': 'Тёмная',
            'LoadVersionPercent': '{percent}%',
            'LoadVersionTextConnect': 'Подключение...',
            'LoadVersionTextLoad': 'Загрузка...',
            'LoadVersionLaunchNotification': 'Запустить обновленную версию?',
            'LoadVersionLaunchYNMessageBoxText': 'Запустить обновленную версию OceanShipsWar {version}.exe?',
            'LoadVersionLaunchYNMessageBoxTitle': 'Запуск',
            'InitTextLabelDefault': '',
            'InitPercentLabelDefault': '',
            'InitTextLabelConnect': 'Подключение...',
            'InitTextLabelSuccessConnect': 'Подключение...',
            'InitTextLabelSearch': 'Поиск файла {file}',
            'InitTextLabelLoad': 'Инициализация файла {file}',
            'InitPercentLabel': '{percent}%',
            'UpdateNotificationFine': 'Доступна новая версия {version}, загрузить её?.',
            'UpdateNotificationNotFine': 'Обновлений нет.',
            'UpdateNotificationYNMessageBoxText': 'Доступна версия {version}, загрузить её?.',
            'UpdateNotificationYNMessageBoxTitle': 'Обновление до версии {version}.',
            'CreateGameWrongIP': 'Неверный адрес.',
            'CreateGameConnect': 'Подключение...',
            'CreateGameYouIP': 'Ваш IP адрес: {ip}:{port}',
            'CreateGameYouLink': 'Нажмите для копирования приглашения.',
            'CreateGameYouIPDefault': 'Секунду...',
            'CreateGameYouLinkDefault': 'Секунду...',
            'CreateGameYouIPCopied': 'IP адрес скопирован в буфер обмена.',
            'CreateGameYouLinkCopied': 'Ссылка приглашение скопирована в буфер обмена.',
            'CreateGameConditionDefault': '',
            'CreateGameInputDefault': 'Введите IP в формате IP:PORT.',
            'CreateGameConnectionError': 'Неверный адрес приглашения',
            'PlayGameQuit': 'Главное меню.',
            'PlayGameRule': 'Это действие запрещено правилами.',
            'PlayGameCount': '{value} клеточные корабли уже установлены.',
            'PlayGameLen': 'Максимальноя длина корбля: 4 клетки.',
            'PlayGameAttackBySelf': 'Сейчас атакуете Вы.',
            'PlayGameAttackByNotSelf': 'Сейчас атакует Ваш противник.',
            'PlayGameLose': 'Вы проиграли :(.',
            'PlayGameWin': 'Вы выиграли :).',
            'PlayGameWait': 'Ждем готовности противника.',
            'PlayGameWaitEnemy': 'Ждем подключения противника.',
            'PlayGameBuild': 'Разместите корабли на поверхности',
            'Esc':'ESC',
            'Sound': 'Звук',
            'SoundGame': 'Звуки игры',
            'SoundNotification': 'Звуки уведомлений',
            'Graphic': 'Графика',
            'GraphicLanguage': 'Язык',
            'LanguageList': ['русский', 'english'],
            'GraphicWindowSize': 'Размер окна',
            'Exit': 'Выход',
            'Version': 'Версия {version}',
            'GameRandomBuild': 'Случайная расстановка',
            'GameClearMap': 'Очистить карту',
            'GraphicFont': 'Шрифт',
            'GraphicTheme': 'Тема',
            'ThemeList': ['тёмная', 'яркая'],
            'Other': 'Другое',
            'OtherConsole': 'Консоль отладки',
            'OtherLinks': 'Глубокие ссылки',
            'Letters': 'АБВГДЕЁЖЗИ',
            'Demo': 'Данный файл является демонстрационным вариантом и возможно лишен некоторых возможностей.',
            'Sudo': 'Запустите игру с правами администратора.'
            }

ENG_DICT = {'StartGame': 'Create game',
            'Settings': 'Settings',
            'ThemeLight': 'Light',
            'ThemeDark': 'Dark',
            'LoadVersionPercent': '{percent}%',
            'LoadVersionTextConnect': 'Connecting...',
            'LoadVersionTextLoad': 'Loading...',
            'LoadVersionLaunchNotification': 'Load new version?',
            'LoadVersionLaunchYNMessageBoxText': 'Launch new OceanShipsWar {version}.exe?',
            'LoadVersionLaunchYNMessageBoxTitle': 'Launch',
            'InitTextLabelDefault': '',
            'InitPercentLabelDefault': '',
            'InitTextLabelConnect': 'Connecting...',
            'InitTextLabelSuccessConnect': 'Connecting...',
            'InitTextLabelSearch': 'Find {file}',
            'InitTextLabelLoad': 'Init {file}',
            'InitPercentLabel': '{percent}%',
            'UpdateNotificationFine': 'New version {version} is available, load it?.',
            'UpdateNotificationNotFine': 'New version is not available.',
            'UpdateNotificationYNMessageBoxText': 'Version {version} is available, load it?.',
            'UpdateNotificationYNMessageBoxTitle': 'Upgrade to version {version}.',
            'CreateGameWrongIP': 'Incorrect IP address.',
            'CreateGameConnect': 'Connecting...',
            'CreateGameYouIP': 'You IP address: {ip}:{port}',
            'CreateGameYouLink': 'Click to copy invitation link.',
            'CreateGameYouIPDefault': 'Moment...',
            'CreateGameYouLinkDefault': 'Moment...',
            'CreateGameYouIPCopied': 'You IP address was copied to clipboard.',
            'CreateGameYouLinkCopied': 'Invitation link copied to clipboard.',
            'CreateGameConditionDefault': '',
            'CreateGameInputDefault': 'You IP with format: IP:PORT.',
            'CreateGameConnectionError': 'Invalid invitation address',
            'PlayGameQuit': 'Main menu.',
            'PlayGameRule': 'This action is prohibited by the rules.',
            'PlayGameCount': '{value} cell ships have already been installed.',
            'PlayGameLen': 'Maximum ship length: 4 cells.',
            'PlayGameAttackBySelf': 'Now you are attacking.',
            'PlayGameAttackByNotSelf': 'Now your opponent is attacking.',
            'PlayGameLose': 'You lost :(.',
            'PlayGameWin': 'You won :).',
            'PlayGameWait': 'Waiting for the enemy to be ready.',
            'PlayGameWaitEnemy': 'Waiting for the connection of opponent.',
            'PlayGameBuild': 'Place ships on surface.',
            'Esc': 'ESC',
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
            'Letters': 'ABCDEFGHIJ',
            'Demo': 'This file is a demo and may lack some features.',
            'Sudo': 'Run the game with super user.'
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
SETTINGS = 4
PLAY = 5

# GAME_EVENT_NOTIFICATION = 0
GAME_EVENT_ATTACK = 0
GAME_EVENT_LEAVE_GAME = 1
GAME_EVENT_END = 2

# GAME_EVENT_MERGE_SETTINGS = 1
# GAME_EVENT_MERGE_SCENE = 2
# GAME_EVENT_GAME_DEFEAT = 3
# GAME_EVENT_GAME_WIN = 4
# GAME_EVENT_GAME_START = 5
# GAME_EVENT_GAME_END = 6
# GAME_EVENT_GAME_CREATE = 7
# GAME_EVENT_GAME_JOIN = 8
# GAME_EVENT_EDIT_LANGUAGE = 9
# GAME_EVENT_EDIT_THEME = 10

GAME_EVENT_NOTIFICATION_TYPE_DEFAULT = 0
SOUNDS_DIR = 'Sounds'
SOUND_TYPE_NOTIFICATION = 'Notification'
SOUND_TYPE_GAME = 'Game'
SOUNDS_TYPE = 'ogg'


SoundsDict = {
    SOUND_TYPE_NOTIFICATION:{'in': 0, 'out': 0},
    SOUND_TYPE_GAME:{'active': 0, 'select': 0, 'denied': 0, 'kill': 0, 'miss': 0, 'wound': 0}
}

DATAS_FOLDER_NAME = 'assets'
GAME_FPS = 60
ICON_PATH = f'{DATAS_FOLDER_NAME}/ico.png'
FONT_PATH = f'{DATAS_FOLDER_NAME}/default.ttf'
LANGUAGE_FILE_MASK = '_language.json'

API_HOST = 'localhost'
API_PORT = 9996
API_METHOD_CONNECT = 'connect'

GAME_HOST = '0.0.0.0'
GAME_PORT = 9997
GAME_PING_DELAY = 10
GAME_EXTRA_PING_DELAY = 1
GAME_DATA_LEN = 2**16

BLOCK_ATTITUDE = 27.428571428571427
SHIP_ATTITUDE = 7
COUNT_BLOCKS_X = 10
COUNT_BLOCKS_Y = 10
SPEED_MERGE_SCENE = 100
DEFAULT_BORDER = 2
BORDER_ATTITUDE = 0.1
BORDER_ACTIVE_ATTITUDE = 0.2
SETTINGS_UPPER_MARGIN = 0.15

GAME_CONDITION_WAIT = 0
GAME_CONDITION_BUILD = 1
GAME_CONDITION_WAIT_AFTER_BUILD = 2
GAME_CONDITION_WAIT_AFTER_ATTACK = 3
GAME_CONDITION_ATTACK = 4
GAME_CONDITION_LOSE = 5
GAME_CONDITION_WIN = 6

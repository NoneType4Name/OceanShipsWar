try:
    version = '0.0.6b'
    import copy
    import json
    import math
    import os
    import sys
    import random
    import socket
    import subprocess
    import psutil
    import select
    import time
    import pygame
    from ast import literal_eval
    import requests
    import threading
    from ctypes import windll
    from screeninfo import get_monitors
    from netifaces import interfaces, ifaddresses, AF_INET
    from Gui import *
    import Reg as reg
    import win32process
    import win32gui, win32com.client
    import logging
    try:
        os.chdir(sys._MEIPASS)
        main_dir = os.path.dirname(sys.executable)
    except AttributeError:
        os.chdir(os.path.split(__file__)[0])
        main_dir = os.path.dirname(__file__)
    logging.basicConfig(filename='logs.txt', filemode='w',
                        format='%(levelname)s\t[%(asctime)s] [%(module)s in %(funcName)s] line %(lineno)d|\t%(message)s',
                        level=logging.NOTSET)
    logging.info('import libs')
    shell_win = win32com.client.Dispatch("WScript.Shell")
    link = None
    run_with_links = True
    size = (get_monitors()[0].width, get_monitors()[0].height)
    caption = 'OceanShipsWar'
    icon_path = 'asets/ico.png'
    default_font = 'asets/notosans.ttf'
    lang = 'rus'
    theme = 0

    def base_parse_args(args):
        for arg in args:
            split_arg = arg.split('=')
            if split_arg[0] == 'link':
                global run_with_links
                run_with_links = bool(int(split_arg[1]))
            elif split_arg[0] == 'size':
                global size
                sz = split_arg[1].split('x')
                size = (int(sz[0]), int(sz[1]))
            elif split_arg[0] == 'theme':
                global theme
                theme = float(split_arg[1])
            else:
                logging.warning(f'unknown arg:{arg} in {args}')


    base_parse_args(sys.argv[1:])
    if run_with_links:
        link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        link.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        try:
            link.bind(('localhost', 6666))
            link.setblocking(False)
            link.listen(10)
        except OSError:
            if len(sys.argv) > 1:
                link.connect(('localhost', 6666))
                link.send(sys.argv[1].encode())
                link.close()
            sys.exit(0)


    def work_with_links(arg: str):
        if ':' in arg:
            arg = arg.split(':')[1]
        unpack_args = arg.split('&')
        for request in unpack_args:
            global game
            request = request.split('?')
            if request[0] == 'join' and not game:
                if 'code' in request[1]:
                    adr = request[1].split('=')[1]
                    if ':' in adr:
                        adr = adr.split(':', 1)
                        GameSettings['my socket'] = [adr[0], int(adr[1])]
                    else:
                        GameSettings['my socket'] = [adr, 9998]
                    try:
                        global sock, is_adm, settings, room, create_game, join_game, me, not_me
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                        sock.settimeout(3)
                        sock.connect((GameSettings['my socket'][0], GameSettings['my socket'][1]))
                        is_adm = False
                        game = True
                        settings, room, create_game, join_game = [False]*4
                        me = 'client'
                        not_me = 'main'
                        shell_win.SendKeys("%")
                        win32gui.SetForegroundWindow(pygame.display.get_wm_info()['window'])
                    except Exception as err:
                        global ERRORS
                        shell_win.SendKeys("%")
                        win32gui.SetForegroundWindow(pygame.display.get_wm_info()['window'])
                        ERRORS.append(f'Не верный адрес приглашения.\t{err.args}')
                        GameSettings['my socket'] = ['', 0]
                        re_theme()
            else:
                logging.warning(f'unknown request:{request} in {unpack_args}')


    pygame.init()
    logging.debug('SDL success init')
    try:
        pygame.mixer.init()
        logging.debug('mixer success init')
    except pygame.error:
        logging.debug('mixer not init')
    # if getattr(sys, 'frozen', False):
    #     main_dir = os.path.dirname(sys.executable)
    # elif __file__:
    #     main_dir = os.path.dirname(__file__)

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.font.init()
    logging.debug('font success init')
    screen = pygame.Surface(size, pygame.SRCALPHA)
    dsp = pygame.display.set_mode(size, pygame.HWSURFACE)
    pygame.display.set_icon(pygame.image.load(icon_path))
    pygame.display.set_caption(caption)
    KILLED_SHIP = (60, 60, 60)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    bsize = size[0] // 27.428571428571427
    ships_wh = int(bsize // 7)
    left_margin, upper_margin = (size[0] // 2 - bsize * 5), (size[1] // 2 - bsize * 5)
    font = pygame.font.Font(default_font, int(bsize / 1.5))
    infoSurface = pygame.Surface((size[0] // 2 // 1.5, upper_margin // 2), pygame.SRCALPHA)
    blocks = {}
    build_ship = False
    build_y = False
    ship = 0
    doSelect = True
    create_ship = None
    ships = {1: {}, 2: {}, 3: {}, 4: {}}
    ships_env = []
    clock = pygame.time.Clock()
    run = True
    sock = None
    mouse_left_press = False
    NotificationLeftPress = False
    key_esc = False
    QUADRO = quadro_ship = 1
    TRIO = trio_ship = 2
    DUO = duo_ship = 3
    SOLO = solo_ship = 4
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
    room = False
    create_game = False
    join_game = False
    settings = False
    game = False
    end_game = False
    Sounds = {}
    MaxStartLoad = 0
    StartLoaded = 0
    FineLoadGame = False
    ConditionOfLoad = False
    SettingsActiveElement = None
    RandomBuildButton = True
    INIT_SOUND = pygame.mixer.get_init()
    Labels = pygame.sprite.Group()
    SettingsElements = pygame.sprite.Group()
    settings_pos = 0.1
    upper_margin_settings = 0.1
    pad = 0
    down_margin_settings = 1
    sprites = pygame.sprite.Group()
    SystemButtons = pygame.sprite.Group()
    CreateGameButtons = pygame.sprite.Group()
    GameButtons = pygame.sprite.Group()
    JoinGameButtons = pygame.sprite.Group()
    Notifications = pygame.sprite.Group()
    LoadGameGroup = pygame.sprite.Group()
    letters = []
    solo, duo, trio, quadro = [0] * 4
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
                    'Language List': ['русский', 'english'],
                    'Graphic WindowSize': 'Размер окна',
                    'Exit': 'Выход',
                    'version': f'Версия {version}',
                    'Game random build': 'Случайная расстановка',
                    'Game clear map': 'Очистить карту',
                    'Graphic Font': 'Шрифт',
                    'Graphic Theme': 'Тема',
                    'Theme List': ['тёмная', 'яркая'],
                    'Other': 'Другое',
                    'Other Links': 'Глубокие ссылки'}


    def re_lang():
        global GameLanguage, lang
        if lang == 'rus':
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
                            'Language List': ['русский', 'english'],
                            'Graphic WindowSize': 'Размер окна',
                            'Exit': 'Выход',
                            'version': f'Версия {version}',
                            'Game random build': 'Случайная расстановка',
                            'Game clear map': 'Очистить карту',
                            'Graphic Font': 'Шрифт',
                            'Graphic Theme': 'Тема',
                            'Theme List': ['тёмная', 'яркая'],
                            'Other': 'Другое',
                            'Other Links': 'Глубокие ссылки'
                            }
        elif lang == 'eng':
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
                            'Language List': ['русский', 'english'],
                            'Graphic WindowSize': 'Window size',
                            'Exit': 'Exit',
                            'version': f'Version {version}',
                            'Game random build': 'Random building',
                            'Game clear map': 'Clear map',
                            'Graphic Font': 'Font',
                            'Graphic Theme': 'Theme',
                            'Theme List': ['dark', 'light'],
                            'Other': 'Other',
                            'Other Links': 'Deep links'}


    re_lang()
    Settings = {
        'Graphic': {
            'WindowSize': size,
            'Language': lang,
            'Font': './asets/notosans.ttf',
            'Theme': 0

        },
        'Sound': {
            'Notification': 1,
            'Game': 1
        },
        'Other': {
            'Links': True if reg.get_value(reg.reg.HKEY_CLASSES_ROOT, r'osw\shell\open\command', None).data and run_with_links else False
        }
    }
    sz_modes = pygame.display.list_modes()
    if size not in sz_modes:
        sz_modes.insert(0, size)
    set_for_lists = {
        'Language': dict(zip(['rus', 'eng'], GameLanguage['Language List'])),
        'WindowSize': dict(zip(sz_modes, [f'{val[0]} x {val[1]}' for val in sz_modes])),
        'Theme': dict(zip([0, 1], GameLanguage['Theme List']))
    }

    set_of_settings_type = {
        'Graphic': {
            'WindowSize': List,
            'Language': List,
            'Font': Path,
            'Theme': List
        },
        'Sound': {
            'Notification': Slide,
            'Game': Slide
        },
        'Other': {
            'Links': Switch
        }
    }
    set_for_paths = {
        'Font':{'name':'Select Font (ttf)...', 'multiple': 0, 'types':['*.ttf'], 'values':['.ttf']}
    }
    GameSettings = {
        'my socket': ['', 0],
        'enemy socket': ['', 0]}


    def load_settings():
        global Settings, ERRORS
        if os.path.exists('./settings.json'):
            try:
                with open('./settings.json') as f:
                    t_s = json.loads(f.read())
                for k in t_s:
                    for v in t_s[k]:
                        Settings[k][v] = t_s[k][v]
            except json.decoder.JSONDecodeError as err:
                ERRORS.append(
                    f'Ошибка инициализации json конфига\tСтрока:{err.lineno}\tСтолбец:{err.colno}\tСимвол:{err.pos}\tОшибка:{err.msg}')


    re_lang()
    load_settings()
    active_element = list(Settings.keys())[0]


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
            logging.critical(f'{cords}')
            return False


    def GetShipEnv(cords: tuple) -> pygame.Rect:
        if cords:
            return pygame.Rect(cords[0] - bsize, cords[1] - bsize, cords[2] + bsize * 2, cords[3] + bsize * 2)
        else:
            logging.critical(f'{cords}')
            return False


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
        else:
            logging.critical(f'{cords}')
            return False


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
    My_ip = None


    def get_ip():
        global My_ip
        My_ip = [i['addr'] for i in ifaddresses(interfaces()[0]).setdefault(AF_INET, [{'addr': socket.gethostbyname(socket.getfqdn())}])][0]
        return


    get_ip()


    def draw_ship_count(ships_count, max_ships=[SOLO, DUO, TRIO, QUADRO]):
        mid = [size[0] // 2 + size[0] // 2 // 2, size[1] // 2 - size[1] // 2 // 1.5]
        for type_ship in range(len(ships_count)):
            counter_block_num = 0
            for num_block in range(((max_ships[type_ship] * (type_ship + 1)) + max_ships[type_ship])):
                if counter_block_num < type_ship + 1:
                    if ships_count[type_ship]:
                        color = LINES
                    else:
                        color = KILLED_SHIP
                    counter_block_num += 1
                else:
                    color = BACKGROUND
                    counter_block_num = 0
                    ships_count[type_ship] -= 1 if ships_count[type_ship] else 0
                pygame.draw.rect(screen, color, (
                mid[0] + num_block * (bsize // 2), mid[1] + bsize * (type_ship + 1), bsize // 2, bsize // 2), ships_wh // 3)


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

    if Settings['Graphic']['Theme']:
        set_of_settings = {
            'up margin': 0.15,
            'down margin': 1.9,
            'label': ((214, 213, 212), (23, 21, 19), [(0, 0, 0), (200, 200, 200)]),
            'buttons': ((214, 213, 212), (214, 213, 212), (23, 21, 19), (0, 0, 0), (164, 163, 162), (23, 21, 19)),
            'button red': ((255, 100, 100, 20), (255, 100, 100, 20), (23, 21, 19), (0, 0, 0), (255, 0, 0), (23, 21, 19)),
            'buttons active': ((0, 0, 0), (164, 163, 162), (23, 21, 19), (0, 0, 0), (164, 163, 162), (23, 21, 19)),
            'switches': ((0, 255, 0), (0, 0, 0), (191, 191, 191)),
            'slides': ((117, 75, 7), (202, 169, 115)),
            'lists': ((23, 21, 19), (226, 226, 224), (214, 213, 210)),
            'path': ((117, 75, 7), (202, 169, 115), (23, 21, 19)),
        }
    elif not Settings['Graphic']['Theme']:
        set_of_settings = {
            'up margin': 0.15,
            'down margin': 1.9,
            'label': ((41, 42, 43), (232, 234, 236), [(255, 255, 255), (91, 92, 93)]),
            'buttons': ((41, 42, 43), (41, 42, 43), (232, 234, 236), (255, 255, 255), (91, 92, 93), (232, 234, 236)),
            'button red': ((255, 0, 0, 20), (255, 0, 0, 20), (232, 234, 236), (255, 255, 255), (255, 0, 0), (232, 234, 236)),
            'buttons active': (
            (255, 255, 255), (91, 92, 93), (232, 234, 236), (255, 255, 255), (91, 92, 93), (232, 234, 236)),
            'switches': ((0, 255, 0), (255, 255, 255), (64, 64, 64)),
            'slides': ((138, 180, 248), (53, 86, 140)),
            'lists': ((232, 234, 236), (29, 29, 31), (41, 42, 45)),
            'path': ((138, 180, 248), (53, 86, 140),(232, 234, 236))
        }
    StartLoadProgress = ProgressBar(Settings['Graphic']['Font'],
        (size[0] // 2 - size[0] * 0.2 / 2, size[1] * 0.7, size[0] * 0.2, size[1] * 0.05), LINES, (0, 255, 0), 0)
    StartLoadLabel = Label(Settings['Graphic']['Font'], (size[0] // 2 - size[0] * 0.2 / 2, size[1] * 0.6, size[0] * 0.2, size[1] * 0.05), '0 %',
                           (0, 0, 0, 0), (0, 255, 0), center=True)
    StartLoadLabel2 = Label(Settings['Graphic']['Font'], (size[0] // 2 - size[0] * 0.2 / 2, size[1] * 0.65, size[0] * 0.2, size[1] * 0.05), '',
                            (0, 0, 0, 0), (0, 255, 0), center=True)
    Update = Button(Settings['Graphic']['Font'], (-1, size[1] - bsize // 2, bsize * 2, bsize // 2), str(GameLanguage['version']), ButtonsCl1, ButtonsCl2,
                    ButtonsTxtColor, ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    TextInputCr = TextInput(Settings['Graphic']['Font'],
        (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.2, size[1] * 0.1), BACKGROUND,
        TextInputArCl, TextInputTxCl, 'create', My_ip,
        GameSettings['my socket'][0])
    TextInputJn = TextInput(Settings['Graphic']['Font'],
        (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.2,
         size[1] * 0.1), BACKGROUND, TextInputArCl, TextInputTxCl, 'join', '192.168.1.1',
        GameSettings['my socket'][0])
    CreateGameWaitUser = Label(Settings['Graphic']['Font'],
        (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.95 - size[1] * 0.1 // 2, size[0] * 0.2,
         size[1] * 0.1), f'Ждем соперника... Ваш адрес: {GameSettings["my socket"][0]}:{GameSettings["my socket"][1]}',
        BACKGROUND, (0, 255, 255), center=True)
    JoinGameWaitUser = Label(Settings['Graphic']['Font'],
        (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.95 - size[1] * 0.1 // 2, size[0] * 0.2,
         size[1] * 0.1),
        f'Ждем соперника... Адрес будущего соперника: {GameSettings["enemy socket"][0]}:{GameSettings["enemy socket"][1]}',
        BACKGROUND,
        (255, 0, 255), center=True)
    SettingsMainLabel = Label(Settings['Graphic']['Font'], (size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                              GameLanguage['settings'], BACKGROUND, LINES, center=True)
    CreateGameMainLabel = Label(Settings['Graphic']['Font'], (size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                                GameLanguage['start game'], BACKGROUND, LINES, center=True)
    JoinGameMainLabel = Label(Settings['Graphic']['Font'], (size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                              GameLanguage['join game'], BACKGROUND, LINES, center=True)
    RoomQuit = Button(Settings['Graphic']['Font'], (size[0] - bsize + 1, -1, bsize, bsize),
                      GameLanguage['Exit'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
                      ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    EscButton = Button(Settings['Graphic']['Font'], (-1, -1, (bsize + bsize * 0.5) // 2, bsize // 2), 'ESC', ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
                       ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    ButtonAdm = Button(Settings['Graphic']['Font'],
        (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.3 - size[1] * 0.1, size[0] * 0.16,
         size[1] * 0.1),
        GameLanguage['start game'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
        ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    ButtonClient = Button(Settings['Graphic']['Font'],
        (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.16,
         size[1] * 0.1),
        GameLanguage['join game'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
        ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    if RandomBuildButton:
        RandomChoiceButton = Button(Settings['Graphic']['Font'], (size[0] * 0.2, size[1] * 0.7, size[0] * 0.1, size[1] * 0.05), GameLanguage['Game random build'],
                                    *set_of_settings['buttons'])
    ClearMapButton = Button(Settings['Graphic']['Font'], (size[0] * 0.1, size[1] * 0.7 - size[1] * 0.05, size[0] * 0.1, size[1] * 0.05), GameLanguage['Game clear map'],
                            *set_of_settings['button red'])
    ButtonSettings = Button(Settings['Graphic']['Font'],
        (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.7 - size[1] * 0.1, size[0] * 0.16,
         size[1] * 0.1),
        GameLanguage['settings'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
        ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
    ButtonTheme = Button(Settings['Graphic']['Font'], (size[0] - bsize - bsize // 2, size[1] - bsize - bsize // 2, bsize, bsize),
                         GameLanguage['theme light'] if theme else GameLanguage['theme dark'], ButtonsCl1, ButtonsCl2,
                         ButtonsTxtColor,
                         ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)


    def re_theme():
        threading.Thread(target=get_ip)
        global ButtonAdm, ButtonClient, ButtonSettings, ButtonTheme, EscButton, SettingsMainLabel, RoomQuit, \
            CreateGameMainLabel, TextInputCr, TextInputJn, CreateGameWaitUser, JoinGameMainLabel, JoinGameWaitUser, BACKGROUND, LINES, KILLED_SHIP, Update, \
            StartLoadProgress, StartLoadLabel, StartLoadLabel2, ButtonsCl1, ButtonsCl2, ButtonsTxtColor, ButtonsAtcCol1, ButtonsAtcCol2, ButtonsAtcCol2, ButtonsClActT, TextInputArCl, TextInputTxCl, \
            RandomChoiceButton, ClearMapButton, set_of_settings
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
            set_of_settings = {
                    'up margin': 0.15,
                    'down margin': 1.9,
                    'label': ((214, 213, 212), (23, 21, 19), [(0, 0, 0), (200, 200, 200)]),
                    'buttons': ((214, 213, 212), (214, 213, 212), (23, 21, 19), (0, 0, 0), (164, 163, 162), (23, 21, 19)),
                    'button red': (
                    (255, 100, 100, 20), (255, 100, 100, 20), (23, 21, 19), (0, 0, 0), (255, 0, 0), (23, 21, 19)),
                    'buttons active': ((0, 0, 0), (164, 163, 162), (23, 21, 19), (0, 0, 0), (164, 163, 162), (23, 21, 19)),
                    'switches': ((0, 255, 0), (0, 0, 0), (191, 191, 191)),
                    'slides': ((117, 75, 7), (202, 169, 115)),
                    'lists': ((23, 21, 19), (226, 226, 224), (214, 213, 210)),
                    'path': ((117, 75, 7), (202, 169, 115),(23, 21, 19)),
                }
        elif not theme:
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
            set_of_settings = {
                'up margin': 0.15,
                'down margin': 1.9,
                'label': ((41, 42, 43), (232, 234, 236), [(255, 255, 255), (91, 92, 93)]),
                'buttons': (
                    (41, 42, 43), (41, 42, 43), (232, 234, 236), (255, 255, 255), (91, 92, 93), (232, 234, 236)),
                'button red': (
                    (255, 0, 0, 20), (255, 0, 0, 20), (232, 234, 236), (255, 255, 255), (255, 0, 0), (232, 234, 236)),
                'buttons active': (
                    (255, 255, 255), (91, 92, 93), (232, 234, 236), (255, 255, 255), (91, 92, 93), (232, 234, 236)),
                'switches': ((0, 255, 0), (255, 255, 255), (64, 64, 64)),
                'slides': ((138, 180, 248), (53, 86, 140)),
                'lists': ((232, 234, 236), (29, 29, 31), (41, 42, 45)),
                'path': ((138, 180, 248), (53, 86, 140), (232, 234, 236))}
        StartLoadProgress = ProgressBar(Settings['Graphic']['Font'],
                                        (size[0] // 2 - size[0] * 0.2 / 2, size[1] * 0.7, size[0] * 0.2, size[1] * 0.05),
                                        LINES, (0, 255, 0), 0)
        StartLoadLabel = Label(Settings['Graphic']['Font'],
                               (size[0] // 2 - size[0] * 0.2 / 2, size[1] * 0.6, size[0] * 0.2, size[1] * 0.05), '0 %',
                               (0, 0, 0, 0), (0, 255, 0), center=True)
        StartLoadLabel2 = Label(Settings['Graphic']['Font'],
                                (size[0] // 2 - size[0] * 0.2 / 2, size[1] * 0.65, size[0] * 0.2, size[1] * 0.05), '',
                                (0, 0, 0, 0), (0, 255, 0), center=True)
        Update = Button(Settings['Graphic']['Font'], (-1, size[1] - bsize // 2, bsize * 2, bsize // 2),
                        str(GameLanguage['version']), ButtonsCl1, ButtonsCl2,
                        ButtonsTxtColor, ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
        TextInputCr = TextInput(Settings['Graphic']['Font'],
                                (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.2,
                                 size[1] * 0.1), BACKGROUND,
                                TextInputArCl, TextInputTxCl, 'create', My_ip,
                                GameSettings['my socket'][0])
        TextInputJn = TextInput(Settings['Graphic']['Font'],
                                (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.2,
                                 size[1] * 0.1), BACKGROUND, TextInputArCl, TextInputTxCl, 'join', '192.168.1.1',
                                GameSettings['my socket'][0])
        CreateGameWaitUser = Label(Settings['Graphic']['Font'],
                                   (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.95 - size[1] * 0.1 // 2, size[0] * 0.2,
                                    size[1] * 0.1),
                                   f'Ждем соперника... Ваш адрес: {GameSettings["my socket"][0]}:{GameSettings["my socket"][1]}',
                                   BACKGROUND, (0, 255, 255), center=True)
        JoinGameWaitUser = Label(Settings['Graphic']['Font'],
                                 (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.95 - size[1] * 0.1 // 2, size[0] * 0.2,
                                  size[1] * 0.1),
                                 f'Ждем соперника... Адрес будущего соперника: {GameSettings["enemy socket"][0]}:{GameSettings["enemy socket"][1]}',
                                 BACKGROUND,
                                 (255, 0, 255), center=True)
        SettingsMainLabel = Label(Settings['Graphic']['Font'],
                                  (size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                                  GameLanguage['settings'], BACKGROUND, LINES, center=True)
        CreateGameMainLabel = Label(Settings['Graphic']['Font'],
                                    (size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                                    GameLanguage['start game'], BACKGROUND, LINES, center=True)
        JoinGameMainLabel = Label(Settings['Graphic']['Font'],
                                  (size[0] * 0.05, size[1] * 0.023, size[0] * 0.14, size[1] * 0.05),
                                  GameLanguage['join game'], BACKGROUND, LINES, center=True)
        RoomQuit = Button(Settings['Graphic']['Font'], (size[0] - bsize + 1, -1, bsize, bsize),
                          GameLanguage['Exit'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
                          ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
        EscButton = Button(Settings['Graphic']['Font'], (-1, -1, (bsize + bsize * 0.5) // 2, bsize // 2), 'ESC', ButtonsCl1,
                           ButtonsCl2, ButtonsTxtColor,
                           ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
        ButtonAdm = Button(Settings['Graphic']['Font'],
                           (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.3 - size[1] * 0.1, size[0] * 0.16,
                            size[1] * 0.1),
                           GameLanguage['start game'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
                           ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
        ButtonClient = Button(Settings['Graphic']['Font'],
                              (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.5 - size[1] * 0.1, size[0] * 0.16,
                               size[1] * 0.1),
                              GameLanguage['join game'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
                              ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
        if RandomBuildButton:
            RandomChoiceButton = Button(Settings['Graphic']['Font'],
                                        (size[0] * 0.2, size[1] * 0.7, size[0] * 0.1, size[1] * 0.05),
                                        GameLanguage['Game random build'],
                                        *set_of_settings['buttons'])
        ClearMapButton = Button(Settings['Graphic']['Font'],
                                (size[0] * 0.1, size[1] * 0.7 - size[1] * 0.05, size[0] * 0.1, size[1] * 0.05),
                                GameLanguage['Game clear map'],
                                *set_of_settings['button red'])
        ButtonSettings = Button(Settings['Graphic']['Font'],
                                (size[0] / 2 - (size[0] * 0.16) / 2, size[1] * 0.7 - size[1] * 0.1, size[0] * 0.16,
                                 size[1] * 0.1),
                                GameLanguage['settings'], ButtonsCl1, ButtonsCl2, ButtonsTxtColor,
                                ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
        ButtonTheme = Button(Settings['Graphic']['Font'],
                             (size[0] - bsize - bsize // 2, size[1] - bsize - bsize // 2, bsize, bsize),
                             GameLanguage['theme light'] if theme else GameLanguage['theme dark'], ButtonsCl1, ButtonsCl2,
                             ButtonsTxtColor,
                             ButtonsAtcCol1, ButtonsAtcCol2, ButtonsClActT)
        sprites.empty()
        SystemButtons.empty()
        CreateGameButtons.empty()
        JoinGameButtons.empty()
        LoadGameGroup.empty()
        GameButtons.empty()
        SystemButtons.add(EscButton, SettingsMainLabel, CreateGameMainLabel, CreateGameWaitUser, JoinGameMainLabel,
                          JoinGameWaitUser)
        CreateGameButtons.add(TextInputCr)
        JoinGameButtons.add(TextInputJn)
        sprites.add(ButtonAdm, ButtonClient, ButtonSettings, ButtonTheme, RoomQuit, Update)
        LoadGameGroup.add(StartLoadProgress, StartLoadLabel, StartLoadLabel2)
        GameButtons.add(RandomChoiceButton, ClearMapButton)


    re_theme()


    def update_game(ver):
        global run, ERRORS
        if (windll.user32.MessageBoxW(pygame.display.get_wm_info()['window'], f"Доступна версия {ver}, продолжить обновление?",
                                      f"Обновление до версии {ver}", 36)) == 6:
            ERRORS.append(f'Загружается новая версия: {FromGitVersion}')
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
        if INIT_SOUND:
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
                    if os.path.exists(f'./asets/{var}.{list_of_load[var]["type"]}'):
                        MaxStartLoad += 1
                        break

            for var in list_of_load:
                ConditionOfLoad = f'Load: ./asets/{var}'
                StartLoaded += 1
                Sounds[var] = pygame.mixer.Sound(f'./asets/{var}.{list_of_load[var]["type"]}')
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
                    threading.Thread(target=update_game, args=[FromGitVersion]).start()
            elif 'b' in FromGitVersion:
                ERRORS.append(f'\tПриветствуем участника бетатестирования!.\t')
        return


    threading.Thread(target=StartGame).start()


    def RandomPlacing():
        global mouse_left_press, solo_ship, duo_ship, trio_ship, quadro_ship, solo, duo, trio, quadro, ship, ships
        while True:
            solo, duo, trio, quadro = [0]*4
            solo_ship, duo_ship, trio_ship, quadro_ship = SOLO, DUO, TRIO, QUADRO
            ships = {1: {}, 2: {}, 3: {}, 4: {}}
            cord_not_used = {}
            for k in range(0, 10):
                cord_not_used[k] = dict(zip([str(v) for v in range(0, 10)], [y for y in range(0, 10)]))
            errors = 0
            for type_ship, ships_count in enumerate(reversed([solo_ship, duo_ship, trio_ship, quadro_ship])):
                type_ship = 3 - type_ship
                if errors < 50:
                    for _ in range(ships_count):
                        while errors < 50:
                            errors += 1
                            cord_x = random.choice(list(cord_not_used.keys()))
                            y_vals = []
                            for var in cord_not_used[cord_x].values():
                                if var != 'used':
                                    y_vals.append(var)
                            cord_y = random.choice(y_vals)
                            cords = [cord_x, cord_y]
                            vector = random.randint(0, 1)
                            build = False
                            if not vector:
                                if cords[0] + type_ship < len(cord_not_used):
                                    build = True
                            else:
                                if cords[1] + type_ship < len(cord_not_used):
                                    build = True
                            if build:
                                if vector:
                                    build_ship_this = (cords, (cords[0], cords[1]+type_ship))
                                else:
                                    build_ship_this = (cords, (cords[0] + type_ship, cords[1]))
                                run_c = True
                                for type_s in ships:
                                    if run_c:
                                        for rc in ships[type_s].values():
                                            rect = GetShip(rc['ship'])
                                            if GetShipEnv(GetShip(build_ship_this)).colliderect(rect):
                                                run_c = False
                                                break
                                if run_c:
                                    pygame.draw.rect(screen, (0, 200, 255), GetShip(build_ship_this), ships_wh)
                                    time.sleep(0.1)
                                    if type_ship == 0:
                                        solo_ship -= 1
                                        ships[1][solo] = {'ship': build_ship_this, 'blocks': GetShipBlocks(build_ship_this)}
                                        solo += 1
                                    elif type_ship == 1:
                                        duo_ship -= 1
                                        ships[2][duo] = {'ship': build_ship_this, 'blocks': GetShipBlocks(build_ship_this)}
                                        duo += 1
                                    elif type_ship == 2:
                                        trio_ship -= 1
                                        ships[3][trio] = {'ship': build_ship_this, 'blocks': GetShipBlocks(build_ship_this)}
                                        trio += 1
                                    elif type_ship == 3:
                                        quadro_ship -= 1
                                        ships[4][quadro] = {'ship': build_ship_this, 'blocks': GetShipBlocks(build_ship_this)}
                                        quadro += 1
                                    environ = [
                                        (
                                        [build_ship_this[0][0] - 1 if build_ship_this[0][0] else build_ship_this[0][0],
                                         build_ship_this[0][1] - 1 if build_ship_this[0][1] else build_ship_this[0][1]],
                                        [build_ship_this[1][0] + 1 if build_ship_this[1][0] + 1 < len(cord_not_used) else build_ship_this[1][0],
                                         build_ship_this[1][1] - 1 if build_ship_this[1][1] else build_ship_this[1][1]]
                                        ),
                                        (
                                        [build_ship_this[0][0] - 1 if build_ship_this[0][0] else build_ship_this[0][0],
                                         build_ship_this[0][1]],
                                        [build_ship_this[1][0] + 1 if build_ship_this[1][0] + 1 < len(cord_not_used) else build_ship_this[1][0],
                                         build_ship_this[1][1]]
                                        ),
                                        (
                                        [build_ship_this[0][0] - 1 if build_ship_this[0][0] else build_ship_this[0][0],
                                         build_ship_this[0][1] + 1 if build_ship_this[0][1] + 1 < len(cord_not_used) else build_ship_this[0][1]],
                                        [build_ship_this[1][0] + 1 if build_ship_this[1][0] + 1 < len(cord_not_used) else build_ship_this[1][0],
                                         build_ship_this[1][1] + 1 if build_ship_this[1][1] + 1 < len(cord_not_used) else build_ship_this[1][1]]
                                        )]
                                    for block in [*GetShipBlocks(environ[0]),
                                                  *GetShipBlocks(environ[1]),
                                                  *GetShipBlocks(environ[2])]:
                                        if vector:
                                            cord_not_used[cord_x][str(block[1])] = 'used'
                                        else:
                                            cord_not_used[block[0]][cord_y] = 'used'
                                    ship += 1
                                    break
                else:
                    break
            if not solo_ship + duo_ship + trio_ship + quadro_ship:
                break
        return


    SettingsClass = Settings_class(Settings, set_of_settings, set_of_settings_type, set_for_lists, set_for_paths, GameLanguage, size, screen)

    while run:
        if run_with_links and link:
            try:
                threading.Thread(target=work_with_links, args=[link.accept()[0].recv(1024*2).decode()]).start()
            except BlockingIOError:
                pass
        key_esc = False
        mouse_pos = pygame.mouse.get_pos()
        SettingsClass_settings = SettingsClass.settings
        if SettingsClass.settings != Settings:
            if SettingsClass.settings['Graphic']['WindowSize'] != Settings['Graphic']['WindowSize']:
                size = SettingsClass.settings['Graphic']['WindowSize']
                pygame.display.quit()
                os.environ['SDL_VIDEO_CENTERED'] = '1'
                pygame.display.init()
                screen = pygame.Surface(size, pygame.SRCALPHA)
                dsp = pygame.display.set_mode(size, pygame.HWSURFACE)
                pygame.display.set_caption('OceanShipsWar')
                pygame.display.set_icon(pygame.image.load(icon_path))
                bsize = size[0] // 27.428571428571427
                ships_wh = int(bsize // 7)
                left_margin, upper_margin = (size[0] // 2 - bsize * 5), (size[1] // 2 - bsize * 5)
                font = pygame.font.Font(default_font, int(bsize / 1.5))
                infoSurface = pygame.Surface((size[0] // 2 // 1.5, upper_margin // 2), pygame.SRCALPHA)
                for num_let in range(len(letters)):
                    blocks[num_let] = []
                    for num in range(len(letters)):
                        blocks[num_let].append(
                            pygame.Rect(left_margin + num_let * bsize, upper_margin + num * bsize, bsize, bsize))
                re_theme()
                SettingsClass = Settings_class(SettingsClass.settings, set_of_settings, set_of_settings_type, set_for_lists,
                                               set_for_paths, GameLanguage, size, screen)
            if SettingsClass.settings['Graphic']['Font'] != Settings['Graphic']['Font']:
                default_font = SettingsClass.settings['Graphic']['Font']
                font = pygame.font.Font(default_font, int(bsize / 1.5))
                re_theme()
                SettingsClass = Settings_class(SettingsClass.settings, set_of_settings, set_of_settings_type, set_for_lists, set_for_paths,
                                               GameLanguage, size, screen)
            if SettingsClass.settings['Graphic']['Language'] != Settings['Graphic']['Language']:
                lang = SettingsClass.settings['Graphic']['Language']
                re_lang()
                re_theme()
                SettingsClass = Settings_class(SettingsClass.settings, set_of_settings, set_of_settings_type, set_for_lists, set_for_paths,
                                               GameLanguage, size, screen)
            if SettingsClass.settings['Other']['Links'] != Settings['Other']['Links']:
                if windll.shell32.IsUserAnAdmin():
                    if SettingsClass.settings['Other']['Links']:
                        run_with_links = True
                        reg.init_deep_links(f'{main_dir}\\OceanShipsWar.exe')
                    else:
                        run_with_links = False
                        reg.del_deep_link()
                else:
                    ERRORS.append('Запустите игру с правами администратора.')
                    SettingsClass.settings['Other']['Links'] = False
            if SettingsClass.settings['Graphic']['Theme'] != Settings['Graphic']['Theme']:
                theme = SettingsClass.settings['Graphic']['Theme']
                re_theme()
                SettingsClass = Settings_class(SettingsClass.settings, set_of_settings, set_of_settings_type, set_for_lists,
                                               set_for_paths,
                                               GameLanguage, size, screen)
            Settings = copy.deepcopy(SettingsClass.settings)
        EVENTS = []
        for event in pygame.event.get():
            EVENTS.append(event)
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                step = 0.05
                if event.button == 1:
                    mouse_left_press = True
                    NotificationLeftPress = True
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
                StartLoadProgress.value = StartLoaded / MaxStartLoad
                StartLoadLabel2.text = ConditionOfLoad
                StartLoadLabel.text = f'{int(StartLoaded / MaxStartLoad * 100)} %'
            else:
                StartLoadProgress.value = 0
                StartLoadLabel.text = 'Подключение...'
            LoadGameGroup.update()
            LoadGameGroup.draw(screen)
        elif FineLoadGame and not room and ConditionOfLoad:
            room = True
            ConditionOfLoad = ''
            if len(sys.argv) > 1 and run_with_links:
                threading.Thread(target=work_with_links, args=[sys.argv[1]]).start()
        elif room:
            screen.fill(BACKGROUND)
            RandomChoiceButton.update()
            sprites.update()
            RoomQuit.update()
            if ButtonTheme.isCollide() and mouse_left_press:
                theme = 1 - theme
                Settings['Graphic']['Theme'] = theme
                re_theme()
                SettingsClass = Settings_class(Settings, set_of_settings, set_of_settings_type, set_for_lists,
                                               set_for_paths, GameLanguage, size, screen)
                mouse_left_press = False
            elif ButtonSettings.isCollide() and mouse_left_press:
                mouse_left_press = False
                settings = True
                room = False
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
                mouse_left_press = False
                FromGitVersion = requests.get('https://github.com/NoneType4Name/OceanShipsWar/releases/latest').url.split('/')[-1]
                if version != FromGitVersion:
                    FromGitVersionInt = int(FromGitVersion.replace('.', '').replace('b', ''))
                    versionInt = int(version.replace('.', '').replace('b', ''))
                    if FromGitVersionInt < versionInt:
                        ERRORS.append('pre-release.')
                    else:
                        threading.Thread(target=update_game, args=[FromGitVersion]).start()
                else:
                    ERRORS.append('Актуальная версия.')
            sprites.draw(screen)
        elif settings:
            screen.fill(BACKGROUND)
            SettingsMainLabel.update()
            EscButton.update()
            if EscButton.isCollide() and NotificationLeftPress or key_esc:
                SettingsActiveElement = None
                settings = False
                room = True

            SettingsClass.update(mouse_left_press, EVENTS)
            if SettingsClass.mouse != mouse_left_press:
                mouse_left_press = SettingsClass.mouse
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
                    shell_win.SendKeys("%")
                    win32gui.SetForegroundWindow(pygame.display.get_wm_info()['window'])
                except BlockingIOError:
                    pass
                CreateGameWaitUser.update()
            for s in CreateGameButtons.sprites():
                update: dict = s.update(EVENTS)
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

            for s in JoinGameButtons.sprites():
                update: dict = s.update(EVENTS)
                if update:
                    u = list(update.keys())[0]
                    if u == 'join':
                        if ':' in update[u]:
                            data = update[u].split(':', 1)
                            GameSettings['my socket'] = [data[0], int(data[1])]
                        else:
                            GameSettings['my socket'] = [update[u], 9998]

            if GameSettings['my socket'][0]:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sock.settimeout(3)
                    sock.connect(
                        (GameSettings['my socket'][0], GameSettings['my socket'][1]))
                    is_adm = False
                    game = True
                    join_game = False
                    me = 'client'
                    not_me = 'main'
                    shell_win.SendKeys("%")
                    win32gui.SetForegroundWindow(pygame.display.get_wm_info()['window'])
                except Exception as err:
                    ERRORS.append(f'Введите общедоступный IP адрес или хостинг!.\t{err}')
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
                    except (BlockingIOError, OSError):
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
                l = Label(Settings['Graphic']['Font'],
                          (size[0] / 2 - (size[0] * 0.2) / 2, size[1] * 0.5 - size[1] * 0.3 // 2, size[0] * 0.2, size[1] * 0.3),
                          'Вы проиграли!.' if send_data['end game'] == me else 'Вы выиграли!.', BACKGROUND, (0, 255, 255))
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
                    send_data = {'ships': {1: {}, 2: {}, 3: {}, 4: {}},
                                 'count': 0,
                                 'selects': [],
                                 'killed': {'blocks': [], 'ships': []},
                                 'die': {'blocks': [], 'ships': []},
                                 'move': 'build',
                                 'end game': False,
                                 'pass': False,
                                 'event': []}

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
                    if RandomChoiceButton.isCollide() & GameButtons.has(RandomChoiceButton) and mouse_left_press:
                        threading.Thread(target=RandomPlacing).start()
                        mouse_left_press = False
                        GameButtons.remove(RandomChoiceButton)
                    if ClearMapButton.isCollide() and mouse_left_press:
                        solo, duo, trio, quadro = [0] * 4
                        solo_ship, duo_ship, trio_ship, quadro_ship = SOLO, DUO, TRIO, QUADRO
                        ships = {1: {}, 2: {}, 3: {}, 4: {}}
                        mouse_left_press = False
                    if not GameButtons.has(RandomChoiceButton):
                        if not solo_ship + duo_ship + trio_ship + quadro_ship:
                            GameButtons.add(RandomChoiceButton)
                    GameButtons.update()
                    GameButtons.draw(screen)
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
                                if Settings['Sound']['Game'] and FineLoadGame:
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
                                            send_data['die']['ships'].append(
                                                send_data['ships'][type_ship][num_of_ship]['ship'])
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
                            if mouse_on_block not in send_data['selects'] and mouse_on_block not in send_data['killed']['blocks']:
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
                                        if Settings['Sound']['Game'] and FineLoadGame:
                                            Sounds['killed_sound'].set_volume(Settings['Sound']['Game'])
                                            Sounds['killed_sound'].play()
                                            send_data['event'].append(
                                                {'type': 'sound', 'event': 'killed_sound'})
                                    else:
                                        if Settings['Sound']['Game'] and FineLoadGame:
                                            Sounds['wounded_sound'].set_volume(Settings['Sound']['Game'])
                                            Sounds['wounded_sound'].play()
                                            send_data['event'].append(
                                                {'type': 'sound', 'event': 'wounded_sound'})
                                    send_data['pass'] = False
                                else:
                                    if Settings['Sound']['Game'] and FineLoadGame:
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
                        if mouse_on_block not in send_data['selects'] and mouse_on_block not in send_data['killed'][
                            'blocks']:
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
            if Settings['Sound']['Notification'] and FineLoadGame:
                Sounds['info_sound'].set_volume(Settings['Sound']['Notification'])
                Sounds['info_sound'].play()
            Notifications.add(Notification(Settings['Graphic']['Font'], (size[0] // 2 - size[0] * 0.4 // 2, size[1] * 0.07, size[0] * 0.4, size[1] * 0.1),
                                           er, (86, 86, 86), (0, 0, 0), (255, 255, 255)))
            shell_win.SendKeys("%")
            win32gui.SetForegroundWindow(pygame.display.get_wm_info()['window'])
            del ERRORS[n]
        for n, s in enumerate(reversed(Notifications.sprites())):
            if not n:
                if s.update(NotificationLeftPress):
                    NotificationLeftPress = False
            else:
                if s.update(False):
                    NotificationLeftPress = False
        Notifications.draw(screen)
        dsp.blit(screen, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    if sock:
        sock.close()
    if link:
        link.close()
except Exception as err:
    from datetime import datetime
    current_datetime = datetime.now()
    import traceback
    from ctypes import windll
    from report import *

    exc_type, exc_value, exc_tb = sys.exc_info()
    traceback_exception = ''.join(traceback.TracebackException(exc_type, exc_value, exc_tb).format())
    print(traceback_exception)
    send_message(['alexkim0710@gmail.com'],f'ERROR {type(err)}',
                 f'{traceback_exception}'
                 f'\n\ntime:\t {current_datetime}'
                 f'\nis adm:\t {bool(windll.shell32.IsUserAnAdmin())}',
                 version, 'logs.txt')
    windll.user32.MessageBoxW(pygame.display.get_wm_info()['windows'], traceback_exception, "ERROR INFO", 0)

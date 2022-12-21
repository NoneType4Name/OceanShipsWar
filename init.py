from Game import *
DISPLAY_SIZE = (get_monitors()[0].width, get_monitors()[0].height)
parser = reg.createParser()
namespace_args, unk = parser.parse_known_args()
run_with_links = namespace_args.links if namespace_args.links is not None else True if reg.get_value(reg.HKEY_CLASSES_ROOT, r'osw\shell\open\command', None) else False
size = SIZE((int(namespace_args.size.split('x')[0]), int(namespace_args.size.split('x')[1]))) if namespace_args.size else None
theme = float(namespace_args.theme) if namespace_args.theme is not None else None
lang = namespace_args.lang if namespace_args.lang else None
debug = namespace_args.debug if namespace_args.debug else 0
api_socket = None
if unk:
    log.warning(f'Unknown args: {"; ".join(unk)}, not parsed!.')

if run_with_links:
    api_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    api_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    try:
        log.debug(f'trying to create api handler.')
        api_socket.bind((API_HOST, API_PORT))
        api_socket.setblocking(False)
        api_socket.listen(1)
        log.debug(f'success create api handler.')
    except OSError:
        log.debug(f'error because, api handler instance is already running.')
        if namespace_args.DeepLinksApi:
            log.debug(f'connect to send args from this instance to main.')
            api_socket.connect((API_HOST, API_PORT))
            send = api_socket.send(namespace_args.DeepLinksApi.encode())
            log.debug(f'success send args: {namespace_args.DeepLinksApi}, len: {send}.')
            api_socket.close()
        sys.exit(0)

if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)
    MAIN_DIR = os.path.dirname(sys.executable)
    EXE = True
else:
    os.chdir(os.path.split(__file__)[0])
    MAIN_DIR = os.path.dirname(__file__)
    EXE = False

pygame.init()
sz_modes = pygame.display.list_modes()
if size and size not in sz_modes:
    sz_modes.insert(0, size)

language = Language(DEFAULT_LANGUAGES, DEFAULT_LANGUAGE)

Settings = DATA({
    'Graphic': {
        'WindowSize': {'value': DISPLAY_SIZE, 'type': List, 'values': dict(zip(sz_modes, [f'{val[0]} x {val[1]}' for val in sz_modes]))},
        'Language': {'value': language.Language, 'type': List, 'values': dict(zip(DEFAULT_LANGUAGES, language.LanguageList))},
        # 'Font': {'value': f'{FONT_PATH}', 'type': Path, 'title': 'Select Font (ttf)...', 'multiple': 0,
        #          'types': ['*.ttf']},
        'Theme': {'value': THEME_DARK, 'type': List, 'values': dict(zip(THEMES, language.ThemeList))}

    },
    'Sound': {
        'Notification': {'value': 1, 'type': Slide},
        'Game': {'value': 1, 'type': Slide}
    },
    'Other': {
        'Links': {'value': None,
                  'type': Switch},
        'Console': {'value': 0, 'type': Switch}
    }
})


language = Language(DEFAULT_LANGUAGES, DEFAULT_LANGUAGE)


if os.path.exists(os.path.join(MAIN_DIR, 'settings.json')):
    with open(os.path.join(MAIN_DIR, 'settings.json')) as cfg:
        Settings = settings_set_values(Settings, json.loads(cfg.read()))
else:
    path = Reg.get_value(Reg.HKEY_CURRENT_USER, r'SOFTWARE\NoneType4Name\OSW\Settings', 'Path').data
    if path and os.path.exists(path):
        with open(path) as cfg:
            Settings = settings_set_values(Settings, json.load(cfg))
    else:
        path = os.path.join(os.getenv('LOCALAPPDATA'), 'NoneType4Name', GAME_NAME, 'settings.json')
        if not os.path.exists(path):
            try:
                os.mkdir(os.path.join(os.getenv('LOCALAPPDATA'), 'NoneType4Name'))
            except FileExistsError:
                pass
            try:
                os.mkdir(os.path.join(os.getenv('LOCALAPPDATA'), 'NoneType4Name', GAME_NAME))
            except FileExistsError:
                pass
            with open(path, 'w') as cfg:
                cfg.write(json.dumps(settings_get_values(Settings)))
            Reg.set_value(Reg.HKEY_CURRENT_USER, r'SOFTWARE\NoneType4Name\OSW\Settings', 'Path', path)


Settings.Graphic.WindowSize.value = size if size else Settings.Graphic.WindowSize.value
Settings.Graphic.Language.value = lang if lang else Settings.Graphic.Language.value
Settings.Graphic.Theme.value = theme if theme else Settings.Graphic.Theme.value
Settings.Other.Console.value = debug if debug else Settings.Other.Console.value
Settings.Other.Links.value = (True if os.path.dirname(reg.get_value(reg.HKEY_CLASSES_ROOT, r'osw\shell\open\command', None).data) == MAIN_DIR and run_with_links else False) if Settings.Other.Links.value is None else Settings.Other.Links.value
language.SetLanguage(Settings.Graphic.Language.value)

LANGS = DATA(DEFAULT_LANGUAGES)

for file_name in map(os.path.basename, glob.glob(fr'{MAIN_DIR}/{DATAS_FOLDER_NAME}/*{LANGUAGE_FILE_MASK}')):
    with open(fr'{MAIN_DIR}/{DATAS_FOLDER_NAME}/{file_name}') as f:
        LANGS[file_name.replace(LANGUAGE_FILE_MASK, '')] = read_dictionary(DEFAULT_DICTIONARY, json.loads(f.read()))

Colors = Color({THEME_LIGHT:{
    'KilledShip': (60, 60, 60),
    'Lines': (26, 26, 26),
    'Background': (237, 222, 255),
    'Label': ((151, 119, 186), (161, 129, 196), (232, 234, 236), (232, 234, 236), False, (91, 92, 93), (), False, (108, 55, 166), ()),
    'Button': ((151, 119, 186), (237, 232, 255), (232, 234, 236), (0, 0, 0), False, (82, 41, 125), (), False, (108, 55, 166)),
    'ButtonRed': ((255, 0, 0, 100), (255, 0, 0, 100), (232, 234, 236), (255, 255, 255), False, (255, 0, 0), (), False, (255, 0, 0, 200)),
    'ButtonActive': ((255, 255, 255), (255, 255, 255), (91, 92, 93), (91, 92, 93), False, (100, 0, 200), (), False, (91, 92, 93)),
    'Switch': ((82, 41, 125), (148, 95, 206), (0, 255, 0), (255, 255, 255)),
    'Slide': ((82, 41, 125, 100), (148, 95, 206, 100), (82, 41, 125), (148, 95, 206)),
    'List': ((82, 41, 125), (148, 95, 206), (232, 234, 236), (255, 255, 255), (108, 55, 166), False, (255, 111, 146, 0), (), False, (89, 111, 146, 0), (), False, (0, 0, 0, 0), (), False, (255, 111, 146), ()),
    'Path': ((138, 180, 248), (53, 86, 140), (232, 234, 236)),
    'ProgressBar': ((255, 255, 255), (0, 255, 0)),
    'TextInput': ((151, 119, 186), (209, 166, 255), (200, 200, 200), (255, 255, 255), False, (82, 41, 125), (), False, (108, 55, 166), ()),
    'Red': (255, 0, 0),
    'Green': (0, 255, 0),
    'Blue': (0, 0, 255),
    'White': (0, 0, 255),
    'Scene': {
        'Load': {
            'Label': ((0, 0, 0, 0), (0, 0, 0, 0), (24, 24, 24), (0, 179, 255)),
            'ProgressBar': ((168, 130, 213), (255, 255, 255))},
        'Main': {
            'Button': ((209, 166, 255), (168, 130, 213), (255, 255, 255), (255, 255, 255), True, (237, 222, 255), (209, 166, 255), True, (237, 222, 255), (168, 130, 213)),
        }
    }
},
THEME_DARK: {
    'KilledShip': (60, 60, 60),
    'Lines': (255, 255, 255),
    'Background': (24, 24, 24),
    'Label': ((41, 42, 43), (91, 92, 93), (232, 234, 236), (232, 234, 236), False, (91, 92, 93), (), False, (255, 255, 255), ()),
    'Button': ((41, 42, 43), (255, 255, 255), (232, 234, 236), (0, 0, 0), False, (91, 92, 93), (91, 92, 93), False, (91, 92, 93)),
    'ButtonRed': ((255, 0, 0, 20), (255, 0, 0, 20), (232, 234, 236), (255, 255, 255), False, (255, 0, 0), (), False, (255, 0, 0, 200)),
    'ButtonActive': ((255, 255, 255), (255, 255, 255), (91, 92, 93), (91, 92, 93), False, (100, 0, 200), (), False, (91, 92, 93)),
    'Switch': ((64, 64, 64), (64, 64, 64), (0, 255, 0), (255, 255, 255)),
    'Slide': ((53, 86, 140, 100), (53, 86, 140, 100), (38, 80, 148), (138, 180, 248)),
    'List': ((29, 29, 31), (29, 29, 31), (232, 234, 236), (255, 255, 255), (41, 42, 45), False, (89, 111, 146), (), False, (89, 111, 146), (), False, (89, 111, 146, 0), (), False, (89, 111, 146), ()),
    'Path': ((138, 180, 248), (53, 86, 140), (232, 234, 236)),
    'ProgressBar': ((255, 255, 255), (0, 255, 0)),
    'TextInput': ((24, 24, 24), (24, 24, 24), (155, 155, 155), (255, 255, 255), False, (100, 0, 255, 100), (), False, (100, 0, 255), ()),
    'Red': (255, 0, 0),
    'Green': (0, 255, 0),
    'Blue': (0, 0, 255),
    'White': (0, 0, 255),
    'Scene':{
        'Load':{
            'Label': ((0, 0, 0, 0), (0, 0, 0, 0), (0, 179, 255), (0, 200, 255)),
            'ProgressBar': ((24, 24, 24), (0, 255, 0))},
        'Main':{
            'Button':((0, 0, 0), (0, 0, 0), (255, 255, 255), (100, 0, 200), True, (24, 24, 24), (0, 0, 0), True, (24, 24, 24), (0, 0, 0)),
        }
    }
}
}, Settings.Graphic.Theme.value)

game = Game(__file__, Settings, language, Colors, MAIN_DIR, EXE, debug)


def work_with_links(url):
    log.debug(f'api not parsed uri: {url}.')
    request = urlparse(url)
    log.debug(f'api request: {request}.')
    query = parse_qs(request.query)
    log.debug(f'api query: {query}.')
    for qr in query:
        log.info(f'run {qr} with args: {query[qr]}.')
        if qr == API_METHOD_CONNECT:
            adr = query[qr][0].split('|')
            adr_external = GetIpFromString(adr[0])
            udp_external = GetIpFromString(adr[1])
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((GAME_HOST, GAME_PORT))
                sock.settimeout(0.1)
                sock, ex_ip, ex_port, source_ip, port = GetIP(sock, GAME_HOST, GAME_PORT)
                tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                tcp_socket.connect((AROUND_NAT_SERVER_IP, AROUND_NAT_SERVER_PORT))
                game.SetScene(PLAY, socket=sock, enemy=udp_external, link=[ex_ip, ex_port, tcp_socket, *adr_external])
                log.info(f'Api method CONNECT will be called, args: {query[qr]}.')
            except Exception:
                log.debug(f'connection is over.', exc_info=True, stack_info=True)
                game.AddNotification(game.Language.CreateGameConnectionError)

        else:
            log.warning(f'unknown request: {qr} with args: {" ".join(query[qr])}.')
    else:
        log.debug(f'null args.')


args_parsed = False
game.init(GAME_NAME, ICON_PATH, SIZE(Settings.Graphic.WindowSize.value), pygame.SRCALPHA)
game.MixerInit()

while game.RUN:
    try:

        if not args_parsed and not game.Blocked and namespace_args.DeepLinksApi:
            threading.Thread(target=work_with_links, args=[namespace_args.DeepLinksApi], daemon=True).start()
            args_parsed = True
        if api_socket:
            try:
                threading.Thread(target=work_with_links, args=[api_socket.accept()[0].recv(1024 * 2).decode()], daemon=True).start()
            except BlockingIOError:
                pass
        game.update()
    except Exception as err:
        log.critical(err, stack_info=True, exc_info=True)
        game.Report(err)

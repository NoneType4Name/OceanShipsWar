from Game import *
DISPLAY_SIZE = (get_monitors()[0].width, get_monitors()[0].height)
parser = reg.createParser()
namespace_args = parser.parse_args()
run_with_links = namespace_args.links if namespace_args.links is not None else True if reg.get_value(reg.HKEY_CLASSES_ROOT, r'osw\shell\open\command', None) else False
size = SIZE((int(namespace_args.size.split('x')[0]), int(namespace_args.size.split('x')[1])) if namespace_args.size else DISPLAY_SIZE)
theme = float(namespace_args.theme) if namespace_args.theme is not None else 1
lang = namespace_args.lang if namespace_args.lang else LANG_RUS
debug = namespace_args.debug if namespace_args.debug else 0
demo = namespace_args.demo if namespace_args.demo else False
api_socket = None

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
if size not in sz_modes:
    sz_modes.insert(0, size)

Language = Language(DEFAULT_LANGUAGES, DEFAULT_LANGUAGE, False)


Settings = DATA({
    'Graphic': {
        'WindowSize': {'value': size, 'type': List, 'values': dict(zip(sz_modes, [f'{val[0]} x {val[1]}' for val in sz_modes]))},
        'Language': {'value': lang, 'type': List, 'values': dict(zip(DEFAULT_LANGUAGES, Language.LanguageList))},
        # 'Font': {'value': f'{FONT_PATH}', 'type': Path, 'title': 'Select Font (ttf)...', 'multiple': 0,
        #          'types': ['*.ttf']},
        'Theme': {'value': theme, 'type': List, 'values': dict(zip(THEMES, Language.ThemeList))}

    },
    'Sound': {
        'Notification': {'value': 1, 'type': Slide},
        'Game': {'value': 0, 'type': Slide}
    },
    'Other': {
        'Links': {'value': True if reg.get_value(reg.HKEY_CLASSES_ROOT, r'osw\shell\open\command', None).data == MAIN_DIR and run_with_links else False,
                  'type': Switch},
        'Console': {'value': debug, 'type': Switch}
    }
})

LANGS = DATA(DEFAULT_LANGUAGES)

for file_name in map(os.path.basename, glob.glob(fr'{MAIN_DIR}/{DATAS_FOLDER_NAME}/*{LANGUAGE_FILE_MASK}')):
    with open(fr'{MAIN_DIR}/{DATAS_FOLDER_NAME}/{file_name}') as f:
        LANGS[file_name.replace(LANGUAGE_FILE_MASK, '')] = read_dictionary(DEFAULT_DICTIONARY, json.loads(f.read()))

if theme == THEME_LIGHT:
    if theme == THEME_LIGHT:
        Colors = DATA({
            'KilledShip': (60, 60, 60),
            'Lines': (26, 26, 26),
            'Background': (222, 228, 231),
            'Label': ((41, 42, 43), (91, 92, 93), (232, 234, 236), (232, 234, 236), False, (91, 92, 93), (), False,(255, 255, 255), ()),
            'Button': ((41, 42, 43), (255, 255, 255), (232, 234, 236), (0, 0, 0), False, (91, 92, 93), (91, 92, 93), False, (91, 92, 93)),
            'ButtonRed': ((255, 0, 0, 20), (255, 0, 0, 20), (232, 234, 236), (255, 255, 255), (255, 0, 0), (232, 234, 236)),
            'ButtonActive': ((255, 255, 255), (255, 255, 255), (91, 92, 93), (91, 92, 93), False, (100, 0, 200), (), False, (91, 92, 93)),
            'Switch': ((64, 64, 64), (64, 64, 64), (0, 255, 0), (255, 255, 255)),
            'Slide': ((53, 86, 140, 100), (53, 86, 140, 100), (38, 80, 148), (138, 180, 248)),
            'List': ((29, 29, 31), (29, 29, 31), (232, 234, 236), (255, 255, 255), (41, 42, 45), False, (89, 111, 146), (), False, (89, 111, 146), (), False, (89, 111, 146), (), False, (89, 111, 146), ()),
            'Path': ((138, 180, 248), (53, 86, 140), (232, 234, 236)),
            'ProgressBar': ((255, 255, 255), (0, 255, 0)),
            'TextInput': ((24, 24, 24), (24, 24, 24), (155, 155, 155), (255, 255, 255), False, (100, 0, 255, 100), (), False,(100, 0, 255), ()),
            'Red': (255, 0, 0),
            'Green': (0, 255, 0),
            'Blue': (0, 0, 255),
            'White': (0, 0, 255),
            'Scene': {
                'Load': {
                    'Label': ((0, 0, 0, 0), (0, 0, 0, 0), (24, 24, 24), (0, 179, 255)),
                    'ProgressBar': ((124, 153, 171), (255, 255, 255))},
                'Main': {
                    'Button': ((124, 153, 171), (124, 153, 171), (255, 255, 255), (213, 240, 177), True, (222, 228, 231), (124, 153, 171), True, (222, 228, 231), (124, 153, 171)),
                }
            }
        })
elif theme == THEME_DARK:
    Colors = DATA({
        'KilledShip': (60, 60, 60),
        'Lines': (255, 255, 255),
        'Background': (24, 24, 24),
        'Label': ((41, 42, 43), (91, 92, 93), (232, 234, 236), (232, 234, 236), False, (91, 92, 93), (), False, (255, 255, 255), ()),
        'Button': ((41, 42, 43), (255, 255, 255), (232, 234, 236), (0, 0, 0), False, (91, 92, 93), (91, 92, 93), False, (91, 92, 93)),
        'ButtonRed': ((255, 0, 0, 20), (255, 0, 0, 20), (232, 234, 236), (255, 255, 255), (255, 0, 0), (232, 234, 236)),
        'ButtonActive': ((255, 255, 255), (255, 255, 255), (91, 92, 93), (91, 92, 93), False, (100, 0, 200), (), False, (91, 92, 93)),
        'Switch': ((64, 64, 64), (64, 64, 64), (0, 255, 0), (255, 255, 255)),
        'Slide': ((53, 86, 140, 100), (53, 86, 140, 100), (38, 80, 148), (138, 180, 248)),
        'List': ((29, 29, 31), (29, 29, 31), (232, 234, 236), (255, 255, 255), (41, 42, 45), False, (89, 111, 146), (), False, (89, 111, 146), (), False, (89, 111, 146), (), False, (89, 111, 146), ()),
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
    })

game = Game(__file__, Settings, Language, Colors, MAIN_DIR, EXE, debug)


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
                sock.settimeout(0.01)
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
game.demo = demo
game.init(GAME_NAME, ICON_PATH, size, pygame.SRCALPHA)
game.MixerInit()

while game.RUN:
    if not args_parsed and not game.Blocked and namespace_args.DeepLinksApi:
        threading.Thread(target=work_with_links, args=[namespace_args.DeepLinksApi], daemon=True).start()
        args_parsed = True
    if api_socket:
        try:
            threading.Thread(target=work_with_links, args=[api_socket.accept()[0].recv(1024 * 2).decode()], daemon=True).start()
        except BlockingIOError:
            pass
    game.update()

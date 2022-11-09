from Game import *

DISPLAY_SIZE = (get_monitors()[0].width, get_monitors()[0].height)
parser = reg.createParser()
namespace_args = parser.parse_args()
run_with_links = namespace_args.links if namespace_args.links is not None else True if reg.get_value(reg.HKEY_CLASSES_ROOT, r'osw\shell\open\command', None) else False
size = SIZE((int(namespace_args.size.split('x')[0]), int(namespace_args.size.split('x')[1])) if namespace_args.size else DISPLAY_SIZE)
theme = float(namespace_args.theme) if namespace_args.theme is not None else 0
lang = namespace_args.lang if namespace_args.lang else LANG_RUS
debug = namespace_args.debug if namespace_args.debug else False

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
        'WindowSize': {'value': size, 'type': List, 'values': dict(zip(DEFAULT_LANGUAGES, Language.LanguageList))},
        'Language': {'value': lang, 'type': List, 'values': dict(zip(sz_modes, [f'{val[0]} x {val[1]}' for val in sz_modes]))},
        'Font': {'value': f'{FONT_PATH}', 'type': Path, 'title': 'Select Font (ttf)...', 'multiple': 0,
                 'types': ['*.ttf']},
        'Theme': {'value': theme, 'type': List, 'values': dict(zip(THEMES, Language.DefaultDict.ThemeList))}

    },
    'Sound': {
        'Notification': {'value': 1, 'type': Slide},
        'Game': {'value': 1, 'type': Slide}
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
    Colors = DATA({
        'KilledShip': (200, 200, 200),
        'Lines': (24, 24, 24),
        'Background': (227, 227, 227),
        'Label': ((214, 213, 212), (23, 21, 19), [(0, 0, 0), (200, 200, 200)]),
        'Button': ((214, 213, 212), (214, 213, 212), (23, 21, 19), (0, 0, 0), (164, 163, 162), (23, 21, 19)),
        'ButtonRed': ((255, 100, 100, 20), (255, 100, 100, 20), (23, 21, 19), (0, 0, 0), (255, 0, 0), (23, 21, 19)),
        'ButtonActive': ((0, 0, 0), (164, 163, 162), (0, 0, 0), (164, 163, 162), (23, 21, 19), (23, 21, 19)),
        'Switch': ((0, 255, 0), (0, 0, 0), (191, 191, 191)),
        'Slide': ((117, 75, 7), (202, 169, 115)),
        'List': ((23, 21, 19), (226, 226, 224), (214, 213, 210)),
        'Path': ((117, 75, 7), (202, 169, 115), (23, 21, 19)),
        'ProgressBar': ((24, 24, 24), (0, 255, 0)),
        'Red': (255, 0, 0),
        'Green': (0, 255, 0),
        'Blue': (0, 0, 255),
        'White': (0, 0, 255),
        'Scene':{
            'Load':{
                'Label': ((0, 0, 0, 0), (0, 255, 0)),
                'ProgressBar': ((24, 24, 24), (0, 255, 0))},
            'Main':{
                'Button':((177, 220, 237), (255, 255, 255), (64, 64, 64), (255, 255, 255), (127, 127, 127), (0, 0, 0)),
            }
        }
    })
elif theme == THEME_DARK:
    Colors = DATA({
        'KilledShip': (60, 60, 60),
        'Lines': (255, 255, 255),
        'Background': (24, 24, 24),
        'Label': ((41, 42, 43), (232, 234, 236), [(255, 255, 255), (91, 92, 93)]),
        'Button': ((41, 42, 43), (41, 42, 43), (232, 234, 236), (255, 255, 255), (91, 92, 93), (232, 234, 236)),
        'ButtonRed': ((255, 0, 0, 20), (255, 0, 0, 20), (232, 234, 236), (255, 255, 255), (255, 0, 0), (232, 234, 236)),
        'ButtonActive': ((255, 255, 255), (255, 255, 255), (91, 92, 93), (91, 92, 93), True, (232, 234, 236), (255, 255, 255), True, (232, 234, 236), (255, 255, 255)),
        'Switch': ((0, 255, 0), (255, 255, 255), (64, 64, 64)),
        'Slide': ((138, 180, 248), (53, 86, 140)),
        'List': ((232, 234, 236), (29, 29, 31), (41, 42, 45)),
        'Path': ((138, 180, 248), (53, 86, 140), (232, 234, 236)),
        'ProgressBar': ((255, 255, 255), (0, 255, 0)),
        'Red': (255, 0, 0),
        'Green': (0, 255, 0),
        'Blue': (0, 0, 255),
        'White': (0, 0, 255),
        'Scene':{
            'Load':{

                'Label': ((0, 0, 0, 0), (0, 255, 0)),
                'ProgressBar': ((24, 24, 24), (0, 255, 0))},
            'Main':{
                'Button':((0, 0, 0), (0, 0, 0), (255, 255, 255), (100, 0, 200), True, (24, 24, 24), (0, 0, 0), True, (24, 24, 24), (0, 0, 0)),
            }
        }
    })

game = Game(Settings, Language, Colors, MAIN_DIR, EXE, debug)
game.init(GAME_NAME, ICON_PATH, size, pygame.SRCALPHA)
game.MixerInit()
while game.RUN:
    game.update()

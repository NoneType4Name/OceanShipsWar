from functions import *
# from scene.Play import PlayGame
from scene.Menu import MainScene
from scene.Load import LoadScene
from scene.JoinGame import JoinGame
from scene.Converter import ConvertScene
from scene.CreateGame import CreateGame
from scene.Notification import Notifications


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


class Game:
    def __init__(self, settings: DATA, language: Language, colors: DATA, main_dir: str, exe: bool, debug=0):
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
        consoleHandler.setLevel(self.debug)

        self.Settings = settings
        self.Colors = colors
        self.Sounds = {
            SOUND_TYPE_NOTIFICATION:{},
            SOUND_TYPE_GAME:{}
                       }
        self.SOUND = False
        print(1)
        self.Notifications = pygame.sprite.Group()
        self.GameEvents = []
        self.Properties = reg.getFileProperties(sys.executable)
        self.version = Version(str(self.Properties.FileVersion))
        self.VERSION = self.version.string_version
        self.MAIN_DIR = main_dir
        self.EXE = exe
        self.Language = DATA(replace_str_var(language.__dict__, self))
        self.Scene = DATA(
            {
                INIT: InitScene,
                MAIN: MainScene,
                LOAD: LoadScene,
                CREATE: CreateGame,
                JOIN: JoinGame,
                SETTINGS: Settings,
                # PLAY: PlayGame
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

        self.mouse_wheel_x = 0
        self.mouse_wheel_y = 0

        self.mouse_pos = pygame.mouse.get_pos()
        self.cursor = pygame.SYSTEM_CURSOR_ARROW
        self.events = pygame.event.get()
        if self.events:
            log.debug(self.events)
        for event in self.events:
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

    def update(self):
        self.UpdateEvents()
        try:
            self.ConvertScene.update()
        except Exception as err:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback_exception = ''.join(traceback.TracebackException(exc_type, exc_value, exc_tb).format())
            log.critical(err, exc_info=True, stack_info=True)
            if self.EXE:
                send_message(['alexkim0710@gmail.com'], f'ERROR {type(err)}',
                             f'{traceback_exception}'
                             f'\nis adm:\t {windll.shell32.IsUserAnAdmin()}',
                             reg.getFileProperties(sys.executable).StringFileInfo.ProductVersion,
                             fr'{self.MAIN_DIR}\logs\{os.getpid()}log.txt')
            self.AddNotification('ERROR: %s' % err)
            self.SetScene(MAIN)
        self.Notifications.update(self.mouse_left_press)
        self.screen.blit(self.ConvertScene.image, (0, 0))
        pygame.mouse.set_cursor(self.cursor)
        self.Notifications.draw(self.screen)
        pygame.display.flip()
        self.clock.tick(self.FPS)

    def EditSettings(self, setting_type, name, value):
        self.Settings[setting_type][name]['value'] = value
        self.Settings = DATA(self.Settings.__dict__)

    def EditWindowSize(self, size):
        pass
        # self.ConvertScene = ConvertScene(self, self.Scene[self.])


class InitScene:
    def __init__(self, parent: Game, *kwargs):
        self.type = INIT
        self.parent = parent
        self.image = pygame.Surface((0, 0), pygame.SRCALPHA)

    def update(self, active, args):
        self.image.fill(self.parent.Colors.Background)
        return self.image

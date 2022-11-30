import psutil

import log
from functions import *
from scene.Menu import MainScene
from scene.Load import LoadScene
from scene.Converter import ConvertScene
from scene.CreateGame import CreateGame
from scene.Play import PlayGame
from scene.Notification import Notifications


def LoadNewVersion(self, version):
    b = 0
    self.ProgressBar.value = 0
    self.PercentLabel.value = self.parent.Language.LoadVersionPercent.format(percent=0)
    self.TextLabel.value = self.parent.Language.LoadVersionTextConnect
    while True:
        file = requests.get('https://github.com/NoneType4Name/OceanShipsWar/releases/latest/download/OceanShipsWar.exe', stream=True)
        self.TextLabel.value = self.parent.Language.LoadVersionTextLoad
        break
    with open(fr'{self.parent.MAIN_DIR}\{GAME_NAME} {version.string_version}.exe', 'wb') as f:
        for chunk in file.iter_content(4096):
            f.write(chunk)
            b += 4096
            self.PercentLabel.value = self.parent.Language.LoadVersionPercent.format(percent=round((b / int(file.headers["Content-Length"])) * 100))
            self.ProgressBar.value = b / int(file.headers['Content-Length'])
    self.parent.AddNotification(self.parent.Language.LoadVersionLaunchNotification)
    self.TextLabel.value = self.parent.Language.LoadVersionTextLaunch
    if (windll.user32.MessageBoxW(self.parent.GAME_HWND,
                                  self.parent.Language.LoadVersionLaunchYNMessageBoxText.format(version=version.string_version),
                                  self.parent.Language.LoadVersionLaunchYNMessageBoxTitle, 33)) == 1:
        subprocess.Popen(fr'{self.parent.MAIN_DIR}\{GAME_NAME} {version.string_version}.exe')
        self.parent.RUN = False


class Version:
    def __init__(self, string_version: str):
        vers = {
            'major': 0,
            'minor': 0,
            'micro': 0,
            'type': 0,
                }
        [vers.update({list(vers.keys())[key_n]: value}) for key_n, value in enumerate(map(int, string_version.split('.')))]
        self.major, self.minor, self.micro, self.type = vers.values()
        st = '.'.join(list(map(str, vers.values()))[:-1])
        try:
            str_type = VERSIONS[int(self.type)]
        except KeyError:
            str_type = str(self.type)
        self.string_version = st + '.' + str_type

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
    def __init__(self, run_from, settings: DATA, language: Language, colors: DATA, main_dir: str, exe: bool, debug=0):
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

        self.CONSOLE_HWND = 0
        self.CONSOLE_PROCESS = None
        self.CONSOLE_PID = 0
        self.GAME_HWND = 0
        self.GAME_PROCESS = None
        self.GAME_PID = 0
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
        consoleHandler.setLevel(debug)

        self.parent_path = run_from
        self.Settings = settings
        self.Colors = colors
        self.Sounds = {
            SOUND_TYPE_NOTIFICATION:{},
            SOUND_TYPE_GAME:{}
                       }
        self.SCENE = INIT
        self.SOUND = None
        self.Blocked = False
        self.Notifications = Notifications(self)
        self.GameEvents = []
        self.Properties = reg.getFileProperties(sys.executable)
        self.version = Version(str('0.0.8.1'))
        self.VERSION = self.version.string_version
        self.MAIN_DIR = main_dir
        self.EXE = exe
        self.Language = language
        self.Scene = DATA(
            {
                INIT: InitScene,
                MAIN: MainScene,
                LOAD: LoadScene,
                CREATE: CreateGame,
                SETTINGS: Settings,
                PLAY: PlayGame
            })
        self.ConvertScene = ConvertScene(self, self.Scene[INIT])
        self.ConvertSceneThread = threading.Thread(target=lambda _:True)
        self.Ticker = None

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
        self.GAME_HWND = pygame.display.get_wm_info()['window']
        self.GAME_PID = get_pid_by_hwnd(self.GAME_HWND)
        self.GAME_PROCESS = psutil.Process(self.GAME_PID)
        for hw in get_hwnd_by_pid(self.GAME_PID):
            if hw != self.GAME_HWND:
                self.CONSOLE_HWND = hw
                break
        if not self.CONSOLE_HWND:
            for hw in get_hwnd_by_pid(self.GAME_PROCESS.ppid()):
                if hw != self.GAME_HWND:
                    self.CONSOLE_HWND = hw
                    break
        if not self.CONSOLE_HWND:
            for hw in get_hwnd_by_pid(psutil.Process(self.GAME_PROCESS.ppid()).ppid()):
                if hw != self.GAME_HWND:
                    self.CONSOLE_HWND = hw
                    break
        self.CONSOLE_PID = get_pid_by_hwnd(self.CONSOLE_HWND)
        self.CONSOLE_PROCESS = psutil.Process(self.CONSOLE_PID)
        self.ConsoleOC()
        self.RUN = True
        self.ConvertScene.NewScene(self.Scene[INIT], None)
        self.Ticker = Ticker((0, self.size.h * 0.9, self.size.w, self.size.h * 0.05), self.Language.Demo, 0.5, (200, 200, 200), (255, 0, 0))

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

        Load = 0
        scene.PercentLabel.value = ''
        scene.TextLabel.value = ''
        while self.RUN:
            scene.TextLabel.value = self.Language.InitTextLabelConnect
            try:
                requests.get(GITHUB_REPOS_URL + 'releases/latest')
                scene.TextLabel.value = self.Language.InitTextLabelSuccessConnect
                break
            except requests.exceptions.ConnectionError:
                pass

        MaxLoad = len(list(itertools.chain(*SoundsDict.values()))) * 2
        for sound_type in SoundsDict:
            for sound_name in SoundsDict[sound_type]:
                scene.TextLabel.value = self.Language.InitTextLabelSearch.format(file=os.path.join(".", SOUNDS_DIR, sound_type, sound_name+"."+SOUNDS_TYPE))
                while self.RUN:
                    if os.path.exists(f'{os.path.join(".", DATAS_FOLDER_NAME, SOUNDS_DIR, sound_type, sound_name+"."+SOUNDS_TYPE)}'):
                        Load += 1
                        break
                    elif os.path.exists(f'{os.path.join(self.MAIN_DIR, DATAS_FOLDER_NAME, SOUNDS_DIR, sound_type, sound_name+"."+SOUNDS_TYPE)}'):
                        SoundsDict[sound_type][sound_name] = 1
                        Load += 1
                        break
                scene.ProgressBar.value = Load / MaxLoad
                scene.PercentLabel.value = self.Language.InitPercentLabel.format(percent=round(Load / MaxLoad * 100))

        for sound_type in SoundsDict:
            for sound_name in SoundsDict[sound_type]:
                scene.TextLabel.value = self.Language.InitTextLabelLoad.format(file=os.path.join(SOUNDS_DIR, sound_type, sound_name+"."+SOUNDS_TYPE))
                if SoundsDict[sound_type][sound_name]:
                    sound = pygame.mixer.Sound(f'{os.path.join(self.MAIN_DIR, DATAS_FOLDER_NAME, SOUNDS_DIR, sound_type, sound_name+"."+SOUNDS_TYPE)}')
                else:
                    sound = pygame.mixer.Sound(f'{os.path.join(DATAS_FOLDER_NAME, SOUNDS_DIR, sound_type, sound_name+"."+SOUNDS_TYPE)}')
                self.Sounds[sound_type][sound_name] = sound
                Load += 1
                scene.ProgressBar.value = Load / MaxLoad
                scene.PercentLabel.value = self.Language.InitPercentLabel.format(percent=round(Load / MaxLoad * 100))
        self.Sounds = DATA(self.Sounds)
        self.SOUND = pygame.mixer.get_init()
        return

    def AddNotification(self, notification_text):
        self.Notifications.add(Notification(self, (self.size[0] * 0.3, self.size[1] * 0.07,
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
        possible_version = Version(json.loads(requests.get(
            'https://api.github.com/repos/NoneType4Name/OceanShipsWar/releases/latest').content)['tag_name'])
        if self.version < possible_version:
            self.AddNotification(self.Language.UpdateNotificationFine)
            if (windll.user32.MessageBoxW(self.GAME_HWND,
                                          self.Language.UpdateNotificationYNMessageBoxText.format(version=possible_version.string_version),
                                          self.Language.UpdateNotificationYNMessageBoxTitle.format(version=possible_version.string_version), 33)) == 1:
                self.SetScene(LOAD, func=LoadNewVersion, args=[possible_version])
        else:
            self.AddNotification(self.Language.UpdateNotificationNotFine)

    def ConsoleOC(self):
        win32gui.ShowWindow(self.CONSOLE_HWND, 8 if self.debug else 0)
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
        self.Notifications.update()
        self.screen.blit(self.ConvertScene.image, (0, 0))
        if type(self.cursor) is int:
            pygame.mouse.set_cursor(self.cursor)
            pygame.mouse.set_visible(True)
        elif type(self.cursor) is bool:
            pygame.mouse.set_visible(self.cursor)
        self.Notifications.draw(self.screen)
        self.Ticker.update()
        self.screen.blit(self.Ticker.image, self.Ticker.rect)
        pygame.display.flip()
        self.clock.tick(self.FPS)

    def EditSettings(self, setting_type, name, value):
        self.Settings[setting_type][name]['value'] = value
        self.Settings = DATA(self.Settings.__dict__)
        if name == 'Console':
            self.ConsoleOC()
        elif name == 'Links':
            if self.EXE:
                file_name = ''
            else:
                file_name = self.parent_path
            if windll.shell32.IsUserAnAdmin():
                if value:
                    reg.init_deep_links(f'{sys.executable} {file_name}'.replace('  ', ' '))
                else:
                    reg.del_deep_link()
            else:
                if (windll.shell32.ShellExecuteW(pygame.display.get_wm_info()['window'], "runas", sys.executable,
                                                 file_name + ' ' + ' '.join(sys.argv[1:]), None, True)) == 42:
                    self.RUN = False
                else:
                    self.AddNotification(self.Language.Sudo)
                    self.Settings[setting_type][name]['value'] = False
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

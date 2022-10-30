from Game import *


class SceneInit:
    def __init__(self, main_self):
        self.parent = main_self
        self.MaxLoad = 0
        self.Load = 0
        self.PercentTextLabel = ''
        self.TextLabel = ''
        sz = self.parent.Settings.Graphic.WindowSize
        self.ProgressBar = ProgressBar(self.parent.Settings.Graphic.Font, (size[0] // 2 - size[0] * 0.2 / 2, size[1] * 0.6, size[0] * 0.2, size[1] * 0.05), '0 %',
                                       (0, 0, 0, 0), (0, 255, 0), center=True)

    def update(self):


class Game:
    def __init__(self, settings):
        self.screen = None
        self.colors = None
        self.sounds = None
        self.window_hwnd = None
        # self.Language = Language(language_name, language_dict)
        sz_modes = pygame.display.list_modes()
        # if size not in sz_modes:
        #     sz_modes.insert(0, size)
        # self.
        self.scene = GAME_SCENE_INIT
        self.notifications = []
        self.GameEvents = []


    def init(self, caption, icon_path, size, flag):
        if self.screen is not None:
            pygame.display.quit()
        pygame.display.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode(size, flag)
        self.window_hwnd = pygame.display.get_wm_info()['window']
        pygame.display.set_icon(pygame.image.load(icon_path))
        pygame.display.set_caption(caption)

    def update(self):
        self.screen.fill()
        pass

    def SetForegroundWindow(self):
        win32com.client.Dispatch("WScript.Shell").SendKeys("%")
        windll.user32.SetForegroundWindow(self.window_hwnd)

    def GameEvent(self, **kwargs):
        self.GameEvents.append(DATA(kwargs))

    def AddNotification(self, notification_text, notification_type):
        self.notifications.append(notification_text)
        self.GameEvent(event=GAME_EVENT_NOTIFICATION, type=notification_type, content=notification_text)

    def SetScene(self, scene):
        self.scene = scene

    def LoadSettings(self):
        if os.path.exists('./settings.json'):
            try:
                with open('./settings.json') as f:
                    t_s = json.loads(f.read())
                for k in t_s:
                    for v in t_s[k]:
                        self.Settings[k][v] = t_s[k][v]
            except json.decoder.JSONDecodeError as err:
                self.AddNotification(f'Ошибка инициализации json конфига\tСтрока:{err.lineno}\tСтолбец:{err.colno}\tСимвол:{err.pos}\tОшибка:{err.msg}')

    def init_files(self, list_of_load, dict_for_loaded_files):
        self.scene = GAME_SCENE_INIT
        self.MaxLoad = 0
        self.Load = 0
        self.PercentTextLabel = ''
        self.TextLabel = ''
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAITARROW)
        while RUN:
            self.TextLabel = 'Подключение...'
            try:
                requests.get('https://api.github.com/repos/NoneType4Name/OceanShipsWar/releases/latest')
                self.TextLabel = ''
                break
            except requests.exceptions.ConnectionError:
                pass
        self.MaxLoad = len(list_of_load)*2
        for var in list_of_load:
            self.TextLabel = f'Search: ./{DATAS_FOLDER_NAME}/{var}'
            while RUN:
                if os.path.exists(f'./{DATAS_FOLDER_NAME}/{var}.{list_of_load[var]["type"]}'):
                    self.MaxLoad += 1
                    break
                elif os.path.exists(f'{MAIN_DIR}/{var}.{list_of_load[var]["type"]}'):
                    list_of_load[var]['path'] = 1
                    self.MaxLoad += 1
                    break
        for var in list_of_load:
            self.TextLabel = f'Load: ./{DATAS_FOLDER_NAME}/{var}'
            if list_of_load[var]['path']:
                dict_for_loaded_files[var] = pygame.mixer.Sound(f'{MAIN_DIR}/{DATAS_FOLDER_NAME}/{var}.{list_of_load[var]["type"]}')
            else:
                dict_for_loaded_files[var] = pygame.mixer.Sound(f'./{DATAS_FOLDER_NAME}/{var}.{list_of_load[var]["type"]}')
            self.Load += 1
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
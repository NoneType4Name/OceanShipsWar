from functions import *
from Gui import *


class LoadScene:
    def __init__(self, parent, input_scene, kwargs):
        self.type = LOAD
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)
        self.InputScene = input_scene
        self.parent = parent
        self.func = kwargs.get('func')
        self.kwargs = kwargs
        self.Thread = None
        log.debug(f'New Scene: {self.type}, last {self.InputScene}, dict:{kwargs}.')

        self.ProgressBar = ProgressBar((parent.size.w * 0.4, parent.size.h * 0.7,
                                        parent.size.w * 0.2, parent.size.h * 0.05),
                                       *parent.Colors.Scene.Load.ProgressBar,
                                       value=0
                                       )
        self.PercentLabel = Label(self,
                                  *[(parent.size[0] * 0.4, parent.size[1] * 0.6, parent.size[0] * 0.2, parent.size[1] * 0.05)] * 2,
                                  0.5,
                                  self.parent.Language.InitTextLabelDefault,
                                  *parent.Colors.Scene.Load.Label,
                                  )
        self.TextLabel = Label(self,
                               (parent.size[0] * 0.4, parent.size[1] * 0.65, parent.size[0] * 0.2, parent.size[1] * 0.05),
                               (parent.size[0] * 0.4, parent.size[1] * 0.65, parent.size[0] * 0.2, parent.size[1] * 0.05),
                               0.5,
                               self.parent.Language.InitPercentLabelDefault.format(percent=0),
                               *parent.Colors.Scene.Load.Label)
        self.Elements = pygame.sprite.Group([self.ProgressBar, self.PercentLabel, self.TextLabel])
        if self.func:
            log.debug(f'Start custom func {self.func}, with args:{self.kwargs.get("args")}')
            self.Thread = threading.Thread(target=self.func, args=[self, *self.kwargs.get('args')])
        else:
            log.debug(f'Sound init func start, args:{self.kwargs}')
            self.Thread = threading.Thread(target=self.parent.mixer_init_thread, args=[self, self.kwargs], daemon=True)
        self.Thread.start()

    def update(self, active, *args):
        self.image.fill(self.parent.Colors.Background)
        self.Elements.update()
        self.Elements.draw(self.image)
        if not self.Thread.is_alive():
            self.parent.SetScene(self.InputScene)
            self.parent.cursor = pygame.SYSTEM_CURSOR_ARROW
        else:
            self.parent.cursor = pygame.SYSTEM_CURSOR_WAITARROW
        return self.image

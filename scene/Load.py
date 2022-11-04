from Gui import *
import threading


class LoadScene:
    def __init__(self, parent, input_scene, kwargs):
        self.type = LOAD
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)
        self.InputScene = input_scene.type
        self.parent = parent
        self.func = kwargs.get('func')
        self.kwargs = kwargs
        self.Thread = None
        self.ProgressBar = ProgressBar(None,
                                       (parent.size.w * 0.4, parent.size.h * 0.7,
                                        parent.size.w * 0.2, parent.size.h * 0.05),
                                       *parent.Colors.Scene.Load.ProgressBar,
                                       value=0
                                       )
        self.PercentLabel = Label(FONT_PATH,
                                  (parent.size[0] * 0.4, parent.size[1] * 0.6,
                                   parent.size[0] * 0.2, parent.size[1] * 0.05),
                                  '0%',
                                  *parent.Colors.Scene.Load.Label,
                                  center=True
                                  )
        self.TextLabel = Label(FONT_PATH,
                               (parent.size[0] * 0.4, parent.size[1] * 0.65,
                                parent.size[0] * 0.2, parent.size[1] * 0.05),
                               '1',
                               *parent.Colors.Scene.Load.Label,
                               center=True)
        self.Elements = pygame.sprite.Group([self.ProgressBar, self.PercentLabel, self.TextLabel])
        if self.func:
            self.Thread = threading.Thread(target=self.func, args=[self, self.parent, self.kwargs.get('args')])
        else:
            self.Thread = threading.Thread(target=self.parent.mixer_init_thread, args=[self, self.kwargs])
        self.Thread.start()

    def update(self, event=False):
        self.image.fill(self.parent.Colors.Background)
        self.Elements.update()
        self.Elements.draw(self.image)
        if not self.Thread.is_alive():
            self.parent.SetScene(self.InputScene)
        return self.image

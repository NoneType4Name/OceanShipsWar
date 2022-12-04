from functions import *
from Gui import *


class ConvertScene:
    def __init__(self, parent, new):
        self.old = None
        self.image = None
        self.parent = parent
        self.new = new(parent)
        self.new_alpha = 0
        self.step = SPEED_MERGE_SCENE
        self.new_parent = None
        self.new_object = None
        self.new_kwargs = {}
        log.debug(f'ConvertScene speed: {self.step}.')

    def NewScene(self, new, kwargs):
        self.new_kwargs = kwargs
        self.new_object = new
        self.image = pygame.Surface(self.parent.size, pygame.SRCALPHA)
        self.old = self.new
        self.new_parent = self.old.type
        if kwargs and 'parent' in kwargs:
            self.new_parent = kwargs.get('parent')
            del kwargs['parent']
        self.new = new(self.parent, self.new_parent, self.new_kwargs)
        self.parent.Blocked = self.parent.blocked_scene[self.new.type]
        log.debug(f'Installed new scene: {self.new.type}, old: {self.old.type}')
        self.new_alpha = 0

    def ReNew(self, parent):
        self.parent = parent
        self.new = self.new_object(self.parent, self.new_parent, self.new_kwargs)

    # def ReSize(self):

    def update(self, *args):
        if self.new_alpha + self.step < 255:  # self.old_alpha - self.step > 0
            self.new_alpha += self.step
            # self.old_alpha -= self.step
        elif self.new_alpha != 255:
            self.new_alpha = 255
            self.parent.SCENE = self.new.type
        # if self.old_alpha:
            image_old = self.old.update(False, [])
        #     image_old.set_alpha(self.old_alpha)
            self.image.blit(image_old, (0, 0))
        image_new = self.new.update(True, args)
        image_new.set_alpha(self.new_alpha)
        self.image.blit(image_new, (0, 0))
        return self.image

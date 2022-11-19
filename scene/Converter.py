from functions import *
from Gui import *


class ConvertScene:
    def __init__(self, parent, new):
        self.old = None
        self.image = None
        self.parent = parent
        self.new = new(parent)
        self.old_alpha = 255
        self.new_alpha = 0
        self.step = SPEED_MERGE_SCENE

    def NewScene(self, new, kwargs):
        self.image = pygame.Surface(self.parent.size, pygame.SRCALPHA)
        self.old = self.new
        kwargs:dict
        if kwargs and 'parent' in kwargs:
            last = kwargs.get('parent')
            del kwargs['parent']
            self.new = new(self.parent, last, kwargs)
        else:
            self.new = new(self.parent, self.old.type, kwargs)
        self.old_alpha = 255
        self.new_alpha = 0

    # def ReSize(self):


    def update(self, *args):
        if self.old_alpha - self.step > 0 and self.new_alpha + self.step < 255:
            self.new_alpha += self.step
            self.old_alpha -= self.step
        elif self.old_alpha and self.new_alpha != 255:
            self.old_alpha = 0
            self.new_alpha = 255
        if self.old_alpha:
            image_old = self.old.update(False, [])
            image_old.set_alpha(self.old_alpha)
            self.image.blit(image_old, (0, 0))
        image_new = self.new.update(True, args)
        image_new.set_alpha(self.new_alpha)
        self.image.blit(image_new, (0, 0))
        return self.image

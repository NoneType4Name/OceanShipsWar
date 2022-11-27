from Gui import *


class Notifications(pygame.sprite.Group):
    def __init__(self, parent, *sprites: [pygame.sprite.Sprite]):
        super().__init__(sprites)
        self.parent = parent

    def update(self):
        for n, s in enumerate(reversed(self.sprites())):
            if not n:
                s.update(self.parent.mouse_left_release)
            s.update(False)

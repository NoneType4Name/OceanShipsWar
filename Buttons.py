import pyperclip
import time
import pygame

PUNCTUATION = list('''!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ ''')
default_font = 'asets/notosans.ttf'
pygame.font.init()


def RoundedRect(rect, color, radius=0.4) -> pygame.Surface:
    """
    RoundedRect(surface,rect,color,radius=0.4)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect = pygame.Rect(0, 0, rect[2], rect[3])
    color = pygame.Color(*color)
    alpha = color.a
    color.a = 0
    rectangle = pygame.Surface(rect.size, pygame.SRCALPHA)

    circle = pygame.Surface([min(rect.size) * 3] * 2, pygame.SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle, [int(min(rect.size) * radius)] * 2)

    radius = rectangle.blit(circle, (0, 0))
    radius.bottomright = rect.bottomright
    rectangle.blit(circle, radius)
    radius.topright = rect.topright
    rectangle.blit(circle, radius)
    radius.bottomleft = rect.bottomleft
    rectangle.blit(circle, radius)

    rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
    rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))

    rectangle.fill(color, special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MIN)

    return rectangle


class button(pygame.sprite.Sprite):
    def __init__(self, rect, text, color1, color2, text_color, color1_act, color2_act, color_act_text):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.color1 = pygame.Color(color1)
        self.color2 = pygame.Color(color2)
        self.color1_act = pygame.Color(color1_act)
        self.color2_act = pygame.Color(color2_act)
        self.text_color = pygame.Color(text_color)
        self.color_act_text = pygame.Color(color_act_text)
        self.text = text
        for s in range(1000):
            self.font = pygame.font.Font(default_font, s)
            self.size = self.font.size(self.text)
            if self.size[0] >= self.rect.w - self.rect.h * 0.1 * 4 or self.size[
                1] >= self.rect.h - self.rect.h * 0.1 * 4:
                self.font = pygame.font.Font(default_font, s - 1)
                self.size = self.font.size(self.text)
                break

    def update(self):
        if self.isCollide():
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color1_act), (0, 0))
            self.image.blit(
                RoundedRect((0, 0, self.rect.w - self.rect.h * 0.1, self.rect.h - self.rect.h * 0.1),
                            self.color2_act), (self.rect.h * 0.06, self.rect.h * 0.06))
            self.image.blit(self.font.render(self.text, True, self.color_act_text),
                            (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))
        else:
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color1), (0, 0))
            self.image.blit(
                RoundedRect((0, 0, self.rect.w - self.rect.h * 0.1, self.rect.h - self.rect.h * 0.1),
                            self.color2), (self.rect.h * 0.06, self.rect.h * 0.06))
            self.image.blit(self.font.render(self.text, True, self.text_color),
                            (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))

    def isCollide(self):
        if self.rect.x < pygame.mouse.get_pos()[0] < self.rect.x + self.rect.width and self.rect.y < \
                pygame.mouse.get_pos()[
                    1] < self.rect.y + self.rect.height:
            return True
        else:
            return False


class switch(pygame.sprite.Sprite):
    def __init__(self, rect, color_on, color_off, background, name, power=False):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.color_on = pygame.Color(color_on)
        self.color_off = pygame.Color(color_off)
        self.background = pygame.Color(background)
        self.name = name
        self.power = power

    def isCollide(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        else:
            return False

    def update(self, mouse):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.power:
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
            # self.image.blit(RoundedRect((0,0,self.rect.w-self.rect.w*0.2,self.rect.h-self.rect.h*0.2),self.background,1),(self.rect.w*0.1,self.rect.h*0.1))
            pygame.draw.circle(self.image, self.color_on, (self.rect.w / 2 + self.rect.h * 0.55, self.rect.h / 2),
                               self.rect.h / 2 - self.rect.h * 0.1)
        elif not self.power:
            # self.image.blit(RoundedRect((0, 0, self.rect.w - self.rect.w * 0.1, self.rect.h - self.rect.h * 0.1), self.background, 1),(self.rect.w * 0.1, self.rect.h * 0.1))
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
            pygame.draw.circle(self.image, self.color_off, (self.rect.w / 2 - self.rect.h / 2, self.rect.h / 2),
                               self.rect.h / 2 - self.rect.h * 0.1)
        if self.isCollide() and mouse:
            self.power = not self.power
            return self.name


class label(pygame.sprite.Sprite):
    def __init__(self, rect, text, color, text_color, center=False):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.text = text
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.color = pygame.Color(color)
        self.text_color = pygame.Color(text_color)
        self.center = center
        if self.center:
            for s in range(1000):
                self.font = pygame.font.Font(default_font, s)
                self.size = self.font.size(self.text)
                if self.size[0] > self.rect.w or self.size[1] > self.rect.h:
                    self.font = pygame.font.Font(default_font, s - 1)
                    self.size = self.font.size(self.text)
                    break
        else:
            for s in range(1000):
                self.font = pygame.font.Font(default_font, s)
                self.size = self.font.size(self.text)
                if self.size[0] > self.rect.w - self.rect.w * 0.1 or self.size[1] > self.rect.h:
                    self.font = pygame.font.Font(default_font, s - 1)
                    self.size = self.font.size(self.text)
                    break

    def update(self):
        if self.size != self.font.size(self.text):
            if self.center:
                for s in range(1000):
                    self.font = pygame.font.Font(default_font, s)
                    self.size = self.font.size(self.text)
                    if self.size[0] > self.rect.w or self.size[1] > self.rect.h:
                        self.font = pygame.font.Font(default_font, s - 1)
                        self.size = self.font.size(self.text)
                        break
            else:
                for s in range(1000):
                    self.font = pygame.font.Font(default_font, s)
                    self.size = self.font.size(self.text)
                    if self.size[0] > self.rect.w - self.rect.w * 0.1 or self.size[1] > self.rect.h:
                        self.font = pygame.font.Font(default_font, s - 1)
                        self.size = self.font.size(self.text)
                        break
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color, 1), (0, 0))
        self.image.blit(self.font.render(self.text, True, self.text_color),
                        (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))


class Slide(pygame.sprite.Sprite):
    def __init__(self, rect, slide_color, background, base_data, name):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.slide_color = pygame.Color(slide_color)
        self.background = pygame.Color(background)
        self.base_data = base_data
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.name = name

    def update(self, mouse):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
        self.image.blit(RoundedRect((0, 0, self.rect.w * self.base_data, self.rect.h),
                                    (255 - self.background[0], 255 - self.background[1], 255 - self.background[2]), 1),
                        (0, 0))
        pygame.draw.circle(self.image, self.slide_color,
                           (self.rect.w * self.base_data - self.rect.h / 2, self.rect.h / 2), self.rect.h / 2, 0)
        if mouse and self.isCollide():
            self.base_data = self.isCollide()
            return self.name, self.base_data
        return False

    def isCollide(self):
        if self.rect.x < pygame.mouse.get_pos()[0] < self.rect.x + self.rect.w and self.rect.y < pygame.mouse.get_pos()[1] < self.rect.y + self.rect.h:
            return round((pygame.mouse.get_pos()[0] - self.rect.x) / self.rect.w, 1)
        else:
            return False


class List(pygame.sprite.Sprite):
    def __init__(self, rect, base_text, texts, text_color, background, bg_list, name):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.name = str(name)
        self.base_text = str(base_text)
        self.texts = texts
        self.text_color = text_color
        self.bg_list = bg_list
        self.background = background
        self.active = False
        for s in range(1000):
            self.font = pygame.font.Font(default_font, s)
            self.size = self.font.size(self.base_text)
            if self.size[0] > self.rect.w or self.size[1] > self.rect.h:
                self.font = pygame.font.Font(default_font, s - 1)
                self.size = self.font.size(self.base_text)
                break
        self.image = pygame.Surface(
            (self.rect.w, self.rect.h + self.size[1] * len(self.texts) + self.size[1] * 0.1 * len(self.texts)),
            pygame.SRCALPHA)

    def update(self, mouse):
        if mouse and self.isCollide():
            if self.active:
                a = f'{self.name}:{self.isCollide()}'
                self.active = not self.active
                return a
            else:
                self.active = not self.active
        self.image = pygame.Surface(
            (self.rect.w, self.rect.h + self.size[1] * len(self.texts)),
            pygame.SRCALPHA)
        if self.active:
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
            self.image.blit(self.font.render(self.base_text, True, self.text_color),
                            (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))
            # self.image.blit(RoundedRect((0,0,self.rect.w,self.size[1] * len(self.texts)),self.bg_list,0.5),(0,self.rect.h))
            for n, tx in enumerate(self.texts):
                tx = str(tx)
                self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), (255, 255, 255), 0.5),
                                (0, self.rect.h + self.rect.h * n))
                self.image.blit(
                    RoundedRect((0, 0, self.rect.w - self.rect.w * 0.1, self.rect.h - self.rect.h * 0.1), self.bg_list,
                                0.5), (self.rect.w * 0.06, (self.rect.h + self.rect.h * n) + self.rect.h * 0.05))
                self.image.blit(self.font.render(tx, True, self.text_color), (self.rect.w // 2 - self.size[0] // 2,
                                                                              self.rect.h + self.rect.h * n + 1 - self.rect.h // 2 - self.rect.h * 0.05 +
                                                                              self.size[1] // 2))
        else:
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.background, 1), (0, 0))
            self.image.blit(self.font.render(self.base_text, True, self.text_color),
                            (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))

    def isCollide(self):
        if self.active:
            for n, rc in enumerate(self.texts):
                if self.rect.bottomleft[0] < pygame.mouse.get_pos()[0] < self.rect.bottomright[0] and \
                        self.rect.bottomleft[1] + \
                        self.size[1] * n < pygame.mouse.get_pos()[1] < self.rect.bottomright[1] + self.size[1] * (
                        n + 1):
                    return rc
                elif self.rect.x < pygame.mouse.get_pos()[0] < self.rect.x + self.rect.width and self.rect.y < \
                        pygame.mouse.get_pos()[
                            1] < self.rect.y + self.rect.height:
                    return self.base_text
            else:
                return False
        else:
            if self.rect.x < pygame.mouse.get_pos()[0] < self.rect.x + self.rect.width and self.rect.y < \
                    pygame.mouse.get_pos()[
                        1] < self.rect.y + self.rect.height:
                return True
            else:
                return False


class TextInput(pygame.sprite.Sprite):
    def __init__(self, rect, background, around, text_color, name, base_text='', text=''):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.rectInner = pygame.Rect(self.rect.h * 0.04, self.rect.h * 0.04, self.rect.w - self.rect.h * 0.1,
                                     self.rect.h - self.rect.h * 0.1)
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.background = pygame.Color(background)
        self.around = pygame.Color(around)
        self.text_color = pygame.Color(text_color)
        self.base_text = base_text
        self.text = text
        self.active = False
        self.cursor = 0
        self.name = name
        for s in range(0, 1000):
            self.font = pygame.font.Font(default_font, s)
            self.size = self.font.size(self.text if self.text else self.base_text)
            if self.size[0] >= self.rectInner.w - self.rectInner.x or self.size[
                1] >= self.rectInner.h * 0.8 - self.rectInner.y:
                self.font = pygame.font.Font(default_font, s - 1)
                self.size = self.font.size(self.text if self.text else self.base_text)
                break

    def update(self, event):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.isCollide() and event.type == pygame.MOUSEBUTTONDOWN and not self.active:
            if event.button == 1:
                self.active = True
                pygame.key.start_text_input()
                pygame.key.set_repeat(500, 50)
        elif not self.isCollide() and event.type == pygame.MOUSEBUTTONDOWN and self.active:
            if event.button == 1:
                self.active = False
                pygame.key.set_repeat(0, 0)
                pygame.key.stop_text_input()
                return f'{self.name}:{self.text}'
        if self.active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE and self.cursor:
                    if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        for n, sim in enumerate(self.text[::-1]):
                            if sim in PUNCTUATION:
                                self.text = self.text[:self.cursor - (n if n != 0 else 1)] + self.text[self.cursor:]
                                self.cursor -= n if n != 0 else 1
                                break
                        else:
                            self.text = ''
                            self.cursor = 0
                    else:
                        self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
                        self.cursor -= 1
                elif event.key == pygame.K_LEFT:
                    if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        for n, sim in enumerate(self.text[:self.cursor][::-1]):
                            if sim in PUNCTUATION:
                                self.cursor -= n if n != 0 else 1
                                break
                        else:
                            self.cursor = 0
                    elif self.cursor - 1 >= 0:
                        self.cursor -= 1
                elif event.key == pygame.K_RIGHT:
                    if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        for n, sim in enumerate(self.text[self.cursor:]):
                            if sim in PUNCTUATION:
                                self.cursor += n if n != 0 else 1
                                break
                        else:
                            self.cursor = len(self.text)
                    elif self.cursor + 1 <= len(self.text):
                        self.cursor += 1
                elif event.key == pygame.K_DELETE:
                    if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        for n, sim in enumerate(self.text[self.cursor:]):
                            if sim in PUNCTUATION:
                                self.text = self.text[:self.cursor] + self.text[self.cursor + n if n != 0 else 1:]
                                break
                        else:
                            self.text = self.text[:self.cursor]
                    else:
                        self.text = self.text[:self.cursor] + self.text[self.cursor + 1:]
                elif event.key == pygame.K_HOME:
                    self.cursor = 0
                elif event.key == pygame.K_END:
                    self.cursor = len(self.text)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:  # or event.key == pygame.K_ESCAPE
                    self.active = False
                    pygame.key.set_repeat(0, 0)
                    pygame.key.stop_text_input()
                    return f'{self.name}:{self.text}'
                elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                    paste_text = pyperclip.paste()
                    if paste_text:
                        self.text = self.text = self.text[:self.cursor] + paste_text + self.text[self.cursor:]
                        self.cursor += len(paste_text)
            if event.type == pygame.TEXTINPUT:
                self.text = self.text[:self.cursor] + event.text + self.text[self.cursor:]
                self.cursor += 1 if event.text else 0
            for s in range(0, 1000):
                self.font = pygame.font.Font(default_font, s)
                self.size = self.font.size(self.text if self.text else self.base_text)
                if self.size[0] >= self.rectInner.w - self.rectInner.x or self.size[
                    1] >= self.rectInner.h * 0.8 - self.rectInner.y:
                    self.font = pygame.font.Font(default_font, s - 1)
                    self.size = self.font.size(self.text if self.text else self.base_text)
                    break
        if self.active:
            self.image.blit(RoundedRect(self.rect, (0, 255, 0), .5), (0, 0))
            self.image.blit(
                RoundedRect((0, 0, self.rectInner.w + self.rectInner.x, self.rectInner.h + self.rectInner.y),
                            self.background, .5),
                (self.rectInner.x, self.rectInner.y))
        else:
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.around, .5), (0, 0))
            self.image.blit(
                RoundedRect((0, 0, self.rectInner.w + self.rectInner.x, self.rectInner.h + self.rectInner.y),
                            self.background, .5),
                (self.rectInner.x, self.rectInner.y))

        if self.text:
            self.image.blit(self.font.render(self.text, True, self.text_color),
                            (self.rect.h * 0.1, self.rect.h // 2 - self.size[1] // 2))
        else:
            self.image.blit(
                self.font.render(self.base_text, True, (self.text_color.r - 100 if self.text_color.r - 100 > 0 else 100,
                                                        self.text_color.g - 100 if self.text_color.g - 100 > 0 else 100,
                                                        self.text_color.b - 100 if self.text_color.b - 100 > 0 else 100)),
                (self.rect.h * 0.1, self.rect.h // 2 - self.size[1] // 2))

        if self.active:
            pygame.draw.line(self.image,
                             (self.background.r - 100 if self.background.r - 100 > 0 else 100,
                              self.background.g - 100 if self.background.g - 100 > 0 else 100,
                              self.background.b - 100 if self.background.b - 100 > 0 else 100),

                             (self.rect.h * 0.05 + self.font.size(self.text[:self.cursor])[0] +
                              self.font.size(self.text[:self.cursor])[1] * 0.1,
                              (self.rect.h // 2 - self.size[1] // 2)),
                             (self.rect.h * 0.05 + self.font.size(self.text[:self.cursor])[0] +
                              self.font.size(self.text[:self.cursor])[1] * 0.1,
                              (self.rect.h // 2 - self.size[1] // 2) + (
                                          self.rect.h - (self.rect.h // 2 - self.size[1] // 2) * 2)),
                             int(self.font.size(self.text[:self.cursor])[1] * 0.1))

    def isCollide(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        else:
            return False


class Notification(pygame.sprite.Sprite):
    def __init__(self, rect, text, background, around, font_color):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect[0], rect[1] - rect[3], rect[2], rect[3] * 3)
        self.NotificationRect = pygame.Rect(rect)
        self.StartRect = pygame.Rect(rect)
        self.NotificationRect.y = -rect[1]
        self.NotificationRect.x = 0
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.background = pygame.Color(background)
        self.background.a = 240
        self.around = pygame.Color(around)
        self.FontColor = pygame.Color(font_color)
        self.text = {}
        self.StartTime = None
        self.end = False
        self.height_font = 0
        self.step = self.StartRect.h // 4
        self.max = ''  # max(max(self.text.values()))
        self.draw_point = 0
        for n, element in enumerate(str(text).split('\t')):
            string_n = element.split(' ')
            self.text[n] = [' '.join(string_n[x:x + 5]) for x in range(0, len(string_n), 5)]
            self.height_font += len(self.text[n]) + 0.5
        for el in max(self.text.values()):
            if len(self.max) < len(el):
                self.max = el

        for s in range(0, 1000):
            self.font = pygame.font.Font(default_font, s)
            self.size = list(self.font.size(self.max))
            self.size[1] = self.size[1] * self.height_font  # + self.size[1] * 0.2 * len(self.text)
            if self.size[0] >= self.NotificationRect.w * 0.9 or self.size[1] >= self.NotificationRect.h * 0.9:
                self.font = pygame.font.Font(default_font, s - 1)
                self.size = list(self.font.size(self.max))
                self.StartSize = self.font.size(self.max)
                self.size[1] = self.size[1] * self.height_font  # + self.size[1] * 0.2 * len(self.text)
                break

    def update(self, mouse):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.isCollide():
            if mouse:
                self.end = True
        if not self.StartTime and self.NotificationRect.y < self.StartRect.y:
            if self.NotificationRect.y + self.step >= self.StartRect.y:
                self.NotificationRect.y = self.StartRect.y
                self.StartTime = time.time()
            else:
                self.NotificationRect.y += self.step
        elif (time.time() - self.height_font > self.StartTime and self.NotificationRect.y >= self.rect.y - self.StartRect.h and not self.isCollide()) or (
                self.end and self.NotificationRect.y >= self.rect.y - self.StartRect.h):
            self.NotificationRect.y -= self.step
        elif (time.time() - self.height_font > self.StartTime and self.NotificationRect.y < self.rect.y - self.StartRect.h) or (
                self.NotificationRect.y <= self.rect.y - self.StartRect.h and self.end):
            self.kill()
            return True
        self.image.blit(RoundedRect(self.NotificationRect, self.background, 0.3), (0, self.NotificationRect.y))
        self.draw_point = 0
        for point in self.text:
            pygame.draw.circle(self.image, self.FontColor, (self.rect.w * 0.03,
                                                            self.NotificationRect.y + self.NotificationRect.h * 0.1 +
                                                            self.StartSize[1] * self.draw_point + self.StartSize[
                                                                1] // 2), self.StartSize[1] * 0.2)
            for text in self.text[point]:
                self.image.blit(self.font.render(text, True, self.FontColor), (
                self.rect.w * 0.1, self.NotificationRect.y + self.NotificationRect.h * 0.1 + self.StartSize[1] * self.draw_point))
                self.draw_point += 1
            self.draw_point += 0.5

    def isCollide(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.x <= mouse_pos[0] <= self.rect.x + self.rect.w and self.NotificationRect.y + self.rect.y <= \
                mouse_pos[1] <= self.NotificationRect.y + self.NotificationRect.h + self.rect.y:
            return True
        else:
            return False


class ProgressBar(pygame.sprite.Sprite):
    def __init__(self, rect, around, progress_color, value):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.around = pygame.Color(around)
        self.progress_color = pygame.Color(progress_color)
        self.value = value

    def update(self):
        self.image.blit(RoundedRect(self.rect, self.around), (0, 0))
        self.image.blit(
            RoundedRect((0, 0, (self.rect.w - self.rect.h * 0.1) * self.value, self.rect.h - self.rect.h * 0.1),
                        self.progress_color), (self.rect.h * 0.06, self.rect.h * 0.06))

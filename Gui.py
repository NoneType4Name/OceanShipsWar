import os.path
import easygui
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from platform import python_version
from ast import literal_eval
import pyperclip
import time
import pygame
import copy

PUNCTUATION = string.punctuation
pygame.font.init()


def draw_round_rect(rect, color, radius):
    rect = pygame.Rect(rect)
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


def RoundedRect(rect, color, radius=0.4, width=0, inner_color=(0, 0, 0)) -> pygame.Surface:
    """
    RoundedRect(rect,color,radius=0.4,width=0)

    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    width   : width
    """
    rect = pygame.Rect(0, 0, rect[2], rect[3])
    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    surf.blit(draw_round_rect(rect, color, radius), (0, 0))
    if width:
        surf.blit(draw_round_rect((0, 0, rect.w - width * 2, rect.h - width * 2), inner_color, radius), (width, width))
    return surf


class Button(pygame.sprite.Sprite):
    def __init__(self, default_font, rect, text, color1, color2, text_color, color1_act, color2_act, color_act_text,
                 radius=0.5):
        pygame.sprite.Sprite.__init__(self)
        self.default_font = default_font
        self.rect = pygame.Rect(rect)
        wh = (int(self.rect.w + self.rect.h) // 100)
        wh = wh if wh else 1
        self.rectInner = pygame.Rect(wh, wh, self.rect.w - wh * 2,
                                     self.rect.h - wh * 2)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.color1 = pygame.Color(color1)
        self.color2 = pygame.Color(color2)
        self.color1_act = pygame.Color(color1_act)
        self.color2_act = pygame.Color(color2_act)
        self.text_color = pygame.Color(text_color)
        self.color_act_text = pygame.Color(color_act_text)
        self.text = text
        self.wh = int((self.rect.w + self.rect.h) / 100)
        self.wh = self.wh if self.wh else 1
        self.radius = radius
        for s in range(1000):
            self.font = pygame.font.Font(default_font, s)
            self.size = self.font.size(self.text)
            if self.size[0] >= self.rect.w - self.rect.h * 0.1 * 4 or self.size[
                1] >= self.rect.h - self.rect.h * 0.1 * 4:
                self.font = pygame.font.Font(default_font, s - 1)
                self.size = self.font.size(self.text)
                break

    def update(self):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.isCollide():
            self.image.blit(RoundedRect(self.rect, self.color1_act, self.radius, self.wh, self.color2_act), (0, 0))
            self.image.blit(self.font.render(self.text, True, self.color_act_text),
                            (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))
        else:
            self.image.blit(RoundedRect(self.rect, self.color1, self.radius, self.wh, self.color2), (0, 0))
            self.image.blit(self.font.render(self.text, True, self.text_color),
                            (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))

    def isCollide(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def RectEdit(self, x=0, y=0):
        self.rect.x += x
        self.rect.y += y


class Switch(pygame.sprite.Sprite):
    def __init__(self, rect, color_on, color_off, background, name, power=False):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.color_on = pygame.Color(color_on)
        self.color_off = pygame.Color(color_off)
        self.background = pygame.Color(background)
        self.name = name
        self.value = power

    def isCollide(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        else:
            return False

    def update(self, mouse):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.value:
            self.image.blit(RoundedRect(self.rect, self.background, 1), (0, 0))
            # self.image.blit(RoundedRect((0,0,self.rect.w-self.rect.w*0.2,self.rect.h-self.rect.h*0.2),self.background,1),(self.rect.w*0.1,self.rect.h*0.1))
            pygame.draw.circle(self.image, self.color_on, (self.rect.w / 2 + self.rect.h * 0.55, self.rect.h / 2),
                               self.rect.h / 2 - self.rect.h * 0.1)
        elif not self.value:
            # self.image.blit(RoundedRect((0, 0, self.rect.w - self.rect.w * 0.1, self.rect.h - self.rect.h * 0.1), self.background, 1),(self.rect.w * 0.1, self.rect.h * 0.1))
            self.image.blit(RoundedRect(self.rect, self.background, 1), (0, 0))
            pygame.draw.circle(self.image, self.color_off, (self.rect.w / 2 - self.rect.h / 2, self.rect.h / 2),
                               self.rect.h / 2 - self.rect.h * 0.1)
        if self.isCollide() and mouse:
            self.value = not self.value
            return {self.name: self.value}

    def RectEdit(self, x=0, y=0):
        self.rect.x += x
        self.rect.y += y


class Label(pygame.sprite.Sprite):
    def __init__(self, default_font, rect, text, color, text_color, width: list = False, center=False):
        pygame.sprite.Sprite.__init__(self)
        self.default_font = default_font
        self.rect = pygame.Rect(rect)
        self.text = str(text)
        self.color = pygame.Color(color)
        self.text_color = pygame.Color(text_color)
        if width:
            self.around = pygame.Color(width[0])
            self.around_main = pygame.Color(width[1])
            self.around.a = 100
            self.color.a = 100
            self.text_color.a = 100
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.center = center
        self.width = width
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
                if self.size[0] > self.rect.w - self.rect.w * 0.01 or self.size[1] > self.rect.h:
                    self.font = pygame.font.Font(default_font, s - 1)
                    self.size = self.font.size(self.text)
                    break

    def update(self, name=''):
        if self.width and (
                (self.rect.collidepoint(pygame.mouse.get_pos()) and not name) or (name and name == self.text)):
            # for i in range(self.val2):
            #     self.image.blit(RoundedRect((0, 0, self.rect.w - i * 2, self.rect.h - i * 2), (100, 20, 255, int(255 * (i/self.val2))), 1), (i, i))
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.around, 1, 1, self.around_main), (0, 0))
        else:
            if not self.width:
                self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color, 1), (0, 0))
        if self.center:
            self.image.blit(self.font.render(self.text, True, self.text_color),
                            (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))
        else:
            self.image.blit(self.font.render(self.text, True, self.text_color), (self.rect.w * 0.02,
                                                                                 self.rect.h // 2 - self.size[1] // 2))
        if self.size != self.font.size(self.text):
            if self.center:
                for s in range(1000):
                    self.font = pygame.font.Font(self.default_font, s)
                    self.size = self.font.size(self.text)
                    if self.size[0] > self.rect.w or self.size[1] > self.rect.h:
                        self.font = pygame.font.Font(self.default_font, s - 1)
                        self.size = self.font.size(self.text)
                        break
            else:
                for s in range(1000):
                    self.font = pygame.font.Font(self.default_font, s)
                    self.size = self.font.size(self.text)
                    if self.size[0] > self.rect.w - self.rect.w * 0.02 or self.size[1] > self.rect.h:
                        self.font = pygame.font.Font(self.default_font, s - 1)
                        self.size = self.font.size(self.text)
                        break

    def RectEdit(self, x=0, y=0):
        self.rect.x += x
        self.rect.y += y


class Slide(pygame.sprite.Sprite):
    def __init__(self, default_font, rect, slide_color, background, base_data, name):
        pygame.sprite.Sprite.__init__(self)
        self.default_font = default_font
        self.rect = pygame.Rect(rect[0], rect[1], rect[2] * 1.1, rect[3])
        self.slide_rect = pygame.Rect(rect[0], rect[1], rect[2], rect[3] * 0.4)
        # pygame.Rect(self.rect.w * 0.05, (self.rect.h / 2 - self.rect.h * 0.3 / 2 + 1), self.rect.w * 0.9, self.rect.h * 0.3)
        self.slide_color = pygame.Color(slide_color)
        self.background = pygame.Color(background)
        self.value = base_data
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.name = name
        self.active = False

    def update(self, mouse):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image.blit(RoundedRect((0, 0, self.rect.w, self.slide_rect.h), self.background, 1),
                        (0, self.rect.h / 2 - self.slide_rect.h / 2))
        self.image.blit(RoundedRect((0, 0, self.slide_rect.w * self.value + (self.rect.h * 1 if self.value else
                                                                             0), self.slide_rect.h),
                                    self.slide_color, 1), (0, self.rect.h / 2 - self.slide_rect.h / 2))
        pygame.draw.circle(self.image, self.slide_color,
                           (self.slide_rect.w * self.value + (self.rect.h // 2), self.rect.h // 2),
                           self.rect.h // 2)
        if self.active and mouse:
            self.value = self.GetValue()
        if not self.active and self.isCollide() and mouse:
            self.active = True
            self.value = self.GetValue()
            return True
        if self.active and not mouse:
            self.active = False
            return {self.name: self.value}

    def GetValue(self):
        rtn = round((pygame.mouse.get_pos()[0] - self.rect.x) / self.rect.w, 1)
        if 0 <= rtn <= 1:
            return rtn
        elif rtn < 0:
            return 0
        else:
            return 1

    def isCollide(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def RectEdit(self, x=0, y=0):
        self.rect.x += x
        self.rect.y += y


class Element(pygame.sprite.Sprite):
    def __init__(self, default_font, rect, real_rect, text, value, background, font_color, around, around_select):
        pygame.sprite.Sprite.__init__(self)
        self.default_font = default_font
        self.rect = pygame.Rect(rect)
        self.real_rect = pygame.Rect(real_rect)
        self.background = pygame.Color(background)
        self.font_color = pygame.Color(font_color)
        self.around = pygame.Color(around)
        self.around_select = pygame.Color(around_select)
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.text = text
        self.value = value
        for s in range(1000):
            self.font = pygame.font.Font(default_font, s)
            self.size = self.font.size(self.text)
            if self.size[0] > self.rect.w or self.size[1] > self.rect.h:
                self.font = pygame.font.Font(default_font, s - 1)
                self.size = self.font.size(self.text)
                break

    def update(self, mouse) -> str:
        val = int((self.rect.w + self.rect.h) / 100)
        if self.real_rect.collidepoint(pygame.mouse.get_pos()):
            self.image.blit(RoundedRect(self.rect, self.around_select, 1, (1 if not val else val),
                                        self.background), (0, 0))
            if mouse:
                return self.value
        else:
            self.image.blit(RoundedRect(self.rect, self.around, 1, (1 if not (val // 2) else val // 2),
                                        self.background), (0, 0))
        self.image.blit(self.font.render(self.text, True, self.font_color), (self.rect.w / 2 - self.size[0] / 2,
                                                                             self.rect.h / 2 - self.size[1] / 2))

    def RectEdit(self, x=0, y=0):
        self.real_rect.x += x
        self.real_rect.y += y


class List(pygame.sprite.Sprite):
    def __init__(self, default_font, rect, base_text, base_value, displays_name, values, text_color, background, bg_list, name):
        pygame.sprite.Sprite.__init__(self)
        self.default_font = default_font
        self.rect = pygame.Rect(rect)
        self.name = str(name)
        self.displayed = str(base_text)
        self.value = base_value
        self.texts = displays_name
        self.values = values
        self.text_color = text_color
        self.bg_list = bg_list
        self.background = background
        self.active = False
        for s in range(1000):
            self.font = pygame.font.Font(default_font, s)
            self.size = self.font.size(self.displayed)
            if self.size[0] > self.rect.w or self.size[1] > self.rect.h:
                self.font = pygame.font.Font(default_font, s - 1)
                self.size = self.font.size(self.displayed)
                break
        self.image = pygame.Surface(
            (self.rect.w, self.rect.h + self.size[1] * len(self.texts) + self.size[1] * 0.1 * len(self.texts)),
            pygame.SRCALPHA)
        self.elements = pygame.sprite.Group()
        for n, tx in enumerate(self.texts):
            tx = str(tx)
            self.elements.add(
                Element(self.default_font, (0, rect[3] * (n + 1), rect[2], rect[3]),
                        (self.rect.x, self.rect.y + self.rect.h * (n + 1),
                         self.rect.w, self.rect.h), tx, self.values[n], self.bg_list,
                        self.text_color, self.bg_list, (89, 111, 146)))

    def update(self, mouse):
        self.image = pygame.Surface(
            (self.rect.w,
             self.rect.h + self.size[1] * len(self.texts) + self.size[1] * 0.1 * len(self.texts)),
            pygame.SRCALPHA)
        self.image.blit(RoundedRect(self.rect, self.background, 1), (0, 0))
        self.image.blit(self.font.render(str(self.displayed), True, self.text_color),
                        (self.rect.w // 2 - self.size[0] // 2, self.rect.h // 2 - self.size[1] // 2))
        if not self.active and mouse and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.active = True
            return 1
        elif self.active:
            for sprite in self.elements.sprites():
                sprite: Element
                update = sprite.update(mouse)
                if update is not None:
                    self.active = False
                    self.displayed = sprite.text
                    self.value = sprite.value
                    return {self.name: self.value}
            else:
                if mouse:
                    self.active = False
                    return True
            self.elements.draw(self.image)

    def isCollide(self):
        if self.rect.x < pygame.mouse.get_pos()[0] < self.rect.x + self.rect.width and self.rect.y < \
                pygame.mouse.get_pos()[1] < self.rect.y + self.rect.height:
            return True
        else:
            return False

    def RectEdit(self, x=0, y=0):
        self.rect.x += x
        self.rect.y += y

        for p in self.elements.sprites():
            p.RectEdit(x, y)


class TextInput(pygame.sprite.Sprite):
    def __init__(self, default_font, rect, background, around, text_color, name, base_text='', text=''):
        pygame.sprite.Sprite.__init__(self)
        self.default_font = default_font
        self.rect = pygame.Rect(rect)
        wh = int(self.rect.w + self.rect.h) // 100
        wh = wh if wh else 1
        self.rectInner = pygame.Rect(wh, wh, self.rect.w - wh * 2,
                                     self.rect.h - wh * 2)
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.background = pygame.Color(background)
        self.around = pygame.Color(around)
        self.text_color = pygame.Color(text_color)
        self.base_text = base_text
        self.value = text
        self.active = False
        self.cursor = 0
        self.name = name
        for s in range(0, 1000):
            self.font = pygame.font.Font(default_font, s)
            self.size = self.font.size(self.value if self.value else self.base_text)
            if self.size[0] > self.rectInner.w - self.rectInner.x or self.size[
                1] > self.rectInner.h * 0.8 - self.rectInner.y:
                self.font = pygame.font.Font(default_font, s - 1)
                self.size = self.font.size(self.value if self.value else self.base_text)
                break

    def update(self, events):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.active:
            self.image.blit(RoundedRect(self.rect, (0, 255, 0), .5, self.rectInner.x, self.background), (0, 0))
            pygame.draw.line(self.image,
                             (self.background.r - 100 if self.background.r - 100 > 0 else 100,
                              self.background.g - 100 if self.background.g - 100 > 0 else 100,
                              self.background.b - 100 if self.background.b - 100 > 0 else 100),

                             (self.rect.h * 0.05 + self.font.size(self.value[:self.cursor])[0] +
                              self.font.size(self.value[:self.cursor])[1] * 0.1,
                              (self.rect.h // 2 - self.size[1] // 2)),
                             (self.rect.h * 0.05 + self.font.size(self.value[:self.cursor])[0] +
                              self.font.size(self.value[:self.cursor])[1] * 0.1,
                              (self.rect.h // 2 - self.size[1] // 2) + (
                                      self.rect.h - (self.rect.h // 2 - self.size[1] // 2) * 2)),
                             int(self.font.size(self.value[:self.cursor])[1] * 0.1))
        else:
            self.image.blit(RoundedRect(self.rect, self.around, .5, self.rectInner.x, self.background), (0, 0))

        if self.value:
            self.image.blit(self.font.render(self.value, True, self.text_color),
                            (self.rect.h * 0.1, self.rect.h // 2 - self.size[1] // 2))
        else:
            self.image.blit(
                self.font.render(self.base_text, True, (self.text_color.r - 100 if self.text_color.r - 100 > 0 else 100,
                                                        self.text_color.g - 100 if self.text_color.g - 100 > 0 else 100,
                                                        self.text_color.b - 100 if self.text_color.b - 100 > 0 else 100)),
                (self.rect.h * 0.1, self.rect.h // 2 - self.size[1] // 2))
        for event in events:
            if self.isCollide() and event.type == pygame.MOUSEBUTTONDOWN and not self.active:
                if event.button == 1:
                    self.active = True
                    self.cursor = len(self.value)
                    pygame.key.start_text_input()
                    pygame.key.set_repeat(500, 50)
            elif not self.isCollide() and event.type == pygame.MOUSEBUTTONDOWN and self.active:
                if event.button == 1:
                    self.active = False
                    pygame.key.set_repeat(0, 0)
                    pygame.key.stop_text_input()
                    return {self.name: self.value}
            if self.active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE and self.cursor:
                        if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                            for n, sim in enumerate(self.value[::-1]):
                                if sim in PUNCTUATION:
                                    self.value = self.value[:self.cursor - (n if n != 0 else 1)] + self.value[
                                                                                                   self.cursor:]
                                    self.cursor -= n if n != 0 else 1
                                    break
                            else:
                                self.value = ''
                                self.cursor = 0
                        else:
                            self.value = self.value[:self.cursor - 1] + self.value[self.cursor:]
                            self.cursor -= 1
                        self.re_font()
                    elif event.key == pygame.K_LEFT:
                        if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                            for n, sim in enumerate(self.value[:self.cursor][::-1]):
                                if sim in PUNCTUATION:
                                    self.cursor -= n if n != 0 else 1
                                    break
                            else:
                                self.cursor = 0
                        elif self.cursor - 1 >= 0:
                            self.cursor -= 1
                    elif event.key == pygame.K_RIGHT:
                        if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                            for n, sim in enumerate(self.value[self.cursor:]):
                                if sim in PUNCTUATION:
                                    self.cursor += n if n != 0 else 1
                                    break
                            else:
                                self.cursor = len(self.value)
                        elif self.cursor + 1 <= len(self.value):
                            self.cursor += 1
                    elif event.key == pygame.K_DELETE:
                        if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                            for n, sim in enumerate(self.value[self.cursor:]):
                                if sim in PUNCTUATION:
                                    self.value = self.value[:self.cursor] + self.value[
                                                                            self.cursor + n if n != 0 else 1:]
                                    break
                            else:
                                self.value = self.value[:self.cursor]
                        else:
                            self.value = self.value[:self.cursor] + self.value[self.cursor + 1:]
                        self.re_font()
                    elif event.key == pygame.K_HOME:
                        self.cursor = 0
                    elif event.key == pygame.K_END:
                        self.cursor = len(self.value)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:  # or event.key == pygame.K_ESCAPE
                        if self.value:
                            self.active = False
                            pygame.key.set_repeat(0, 0)
                            pygame.key.stop_text_input()
                            return {self.name: self.value}
                        elif pygame.key.get_mods() & pygame.KMOD_LCTRL:
                            self.value = self.base_text
                            self.cursor = len(self.value)
                            self.re_font()
                    elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        paste_text = pyperclip.paste()
                        if paste_text:
                            self.value = self.value = self.value[:self.cursor] + paste_text + self.value[self.cursor:]
                            self.cursor += len(paste_text)
                            self.re_font()
                if event.type == pygame.TEXTINPUT:
                    self.value = self.value[:self.cursor] + event.text + self.value[self.cursor:]
                    self.cursor += 1 if event.text else 0
                    self.re_font()

    def isCollide(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        else:
            return False

    def re_font(self):
        for s in range(0, 1000):
            self.font = pygame.font.Font(self.default_font, s)
            self.size = self.font.size(self.value if self.value else self.base_text)
            if self.size[0] >= self.rectInner.w - self.rectInner.x or self.size[
                1] >= self.rectInner.h * 0.8 - self.rectInner.y:
                self.font = pygame.font.Font(self.default_font, s - 1)
                self.size = self.font.size(self.value if self.value else self.base_text)
                break


class Notification(pygame.sprite.Sprite):
    def __init__(self, default_font, rect, text, background, around, font_color):
        pygame.sprite.Sprite.__init__(self)
        self.default_font = default_font
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
        elif (
                time.time() - self.height_font > self.StartTime and self.NotificationRect.y >= self.rect.y - self.StartRect.h and not self.isCollide()) or (
                self.end and self.NotificationRect.y >= self.rect.y - self.StartRect.h):
            self.NotificationRect.y -= self.step
        elif (
                time.time() - self.height_font > self.StartTime and self.NotificationRect.y < self.rect.y - self.StartRect.h) or (
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
                    self.rect.w * 0.1,
                    self.NotificationRect.y + self.NotificationRect.h * 0.1 + self.StartSize[1] * self.draw_point))
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
    def __init__(self, default_font, rect, around, progress_color, value):
        pygame.sprite.Sprite.__init__(self)
        self.default_font = default_font
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.around = pygame.Color(around)
        self.progress_color = pygame.Color(progress_color)
        self.value = value
        self.wh = int((self.rect.w + self.rect.h) / 100)

    def update(self):
        self.image.blit(RoundedRect(self.rect, self.around), (0, 0))
        self.image.blit(
            RoundedRect((0, 0, (self.rect.w - self.wh * 2) * self.value, self.rect.h - self.wh * 2),
                        self.progress_color), (self.wh, self.wh))


class Path(pygame.sprite.Sprite):
    def __init__(self, default_font, rect, around, color, font_color, display, name, value, types, typ, multiple):
        pygame.sprite.Sprite.__init__(self)
        self.default_font = default_font
        self.rect = pygame.Rect(rect)
        wh = int(self.rect.w + self.rect.h) // 100
        self.wh = wh if wh else 1
        self.rect_inner = pygame.Rect(rect[0] + self.wh, rect[1] + self.wh, rect[2] - self.wh * 2,
                                      rect[3] - self.wh * 2)
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.around_color = pygame.Color(around)
        self.color = pygame.Color(color)
        self.font_color = pygame.Color(font_color)
        self.types = types
        self.typ = typ
        self.name = name
        self.display = display
        self.value = value
        self.multiple = multiple
        for s in range(1000):
            self.font = pygame.font.Font(default_font, s)
            self.size = self.font.size(self.value)
            if self.size[0] > self.rect_inner.w or self.size[1] > self.rect_inner.h:
                self.font = pygame.font.Font(default_font, s - 1)
                self.size = self.font.size(self.value)
                break

    def update(self, mouse):
        if os.path.splitext(self.value)[1] in self.typ:
            self.image.blit(RoundedRect(self.rect, self.around_color, 1, self.wh, self.color), (0, 0))
        else:
            self.image.blit(RoundedRect(self.rect, (255, 0, 0), 1, self.wh, self.color), (0, 0))
        if '\\' in self.value:
            sep = '\\'
        elif '/' in self.value:
            sep = '/'
        val = f'.../{"/".join(self.value.split(sep)[-3:])}'
        for s in range(1000):
            self.font = pygame.font.Font(self.default_font, s)
            self.size = self.font.size(val)
            if self.size[0] >= self.rect_inner.w or self.size[1] >= self.rect_inner.h:
                self.font = pygame.font.Font(self.default_font, s - 1)
                self.size = self.font.size(val)
                break

        self.image.blit(self.font.render(val, True, self.font_color), (self.rect_inner.w / 2 - self.size[0] / 2,
                                                                       self.rect_inner.h / 2 - self.size[1] / 2))
        if mouse and self.rect.collidepoint(pygame.mouse.get_pos()):
            value = easygui.fileopenbox(filetypes=self.types, multiple=self.multiple, title=self.display)
            if value:
                if os.path.splitext(value)[1] in self.typ:
                    self.value = value
                    return {self.name: self.value}
                else:
                    self.value = value


class Settings_class:
    def __init__(self, settings, set_of_settings, set_of_settings_type, set_for_lists, set_for_paths, game_language,
                 size, surface):
        settings = copy.deepcopy(settings)
        self.all_settings = {}
        self.default_font = settings['Graphic']['Font']
        self.set_of_settings = set_of_settings
        self.set_of_settings_type = set_of_settings
        self.set_for_lists = set_of_settings_type
        self.set_for_paths = set_for_paths
        self.settings = settings
        self.active_settings = list(self.settings.keys())[0]
        self.active_element = None
        self.upper = pad = buttons_pad = set_of_settings['up margin']
        self.game_language = game_language
        self.surface = surface
        self.mouse = False
        BaseRect = pygame.Rect(size[0] // 2 - size[0] // 1.92 // 2, size[1] * pad, size[0] // 1.92, size[1] // 36)
        SettingsButtons = []
        for type_settings in settings:
            pad = self.upper
            temp_g = []
            SettingsElements = []
            Labels = []
            SettingsButtons.append(
                Button(self.default_font, (size[0] * 0.05, size[1] * buttons_pad, BaseRect.h * 5, BaseRect.h),
                       game_language[type_settings],
                       *set_of_settings[
                           'buttons active' if type_settings == self.active_element else 'buttons'],
                       1, ))
            for element in settings[type_settings]:
                BaseRect = pygame.Rect(size[0] // 2 - size[0] // 1.92 // 2, size[1] * pad, size[0] // 1.92,
                                       size[1] // 36)
                if set_of_settings_type[type_settings][element] is Switch:
                    SettingsElements.append(
                        Switch((BaseRect.x + BaseRect.w - (BaseRect.h * 2 - BaseRect.h * 0.1) - 1,
                                BaseRect.y + 1,
                                BaseRect.h * 2 - BaseRect.h * 0.1,
                                BaseRect.h - 2),
                               *set_of_settings['switches'],
                               name=f'{type_settings} {element}',
                               power=settings[type_settings][element]))
                elif set_of_settings_type[type_settings][element] is List:
                    temp_g.append(
                        List(self.default_font, (BaseRect.x + BaseRect.w - (BaseRect.h * 4 - BaseRect.h * 0.1) - 1,
                                                 BaseRect.y + 1,
                                                 BaseRect.h * 4 - BaseRect.h * 0.1,
                                                 BaseRect.h - 2),
                             set_for_lists[element][settings[type_settings][element]],
                             settings[type_settings][element],
                             [v for v in set_for_lists[element].values()],
                             [v for v in set_for_lists[element].keys()],
                             *set_of_settings['lists'],
                             f'{type_settings} {element}'))
                elif set_of_settings_type[type_settings][element] is Slide:
                    SettingsElements.append(Slide(self.default_font,
                                                  (BaseRect.x + BaseRect.w - (BaseRect.h - 2) * 11.5 - 1,
                                                   BaseRect.y + 1,
                                                   (BaseRect.h - 2) * 10,
                                                   BaseRect.h - 2),
                                                  *set_of_settings['slides'],
                                                  base_data=settings[type_settings][element],
                                                  name=f'{type_settings} {element}'))
                elif set_of_settings_type[type_settings][element] is Path:
                    SettingsElements.append(Path(self.default_font,
                                                 (BaseRect.x + BaseRect.w - (BaseRect.h - 2) * 11.5 - 1,
                                                  BaseRect.y + 1,
                                                  (BaseRect.h - 2) * 10,
                                                  BaseRect.h - 2),
                                                 *set_of_settings['path'], value=settings[type_settings][element],
                                                 display=set_for_paths[element]['name'],
                                                 name=f'{type_settings} {element}',
                                                 multiple=set_for_paths[element]['multiple'],
                                                 types=set_for_paths[element]['types'],
                                                 typ=set_for_paths[element]['values']))
                else:
                    print(type_settings, element, type(set_of_settings_type[type_settings][element]))
                    raise SystemError
                Labels.append(
                    Label(self.default_font, BaseRect, game_language[f'{type_settings} {element}'], *set_of_settings['label'], False))
                pad += BaseRect.h / size[1] * 1.1
            buttons_pad += (BaseRect.h / size[1] * 1.1)
            for el in reversed(temp_g):
                SettingsElements.append(el)
            self.all_settings[type_settings] = {}
            self.all_settings[type_settings]['labels'] = Labels
            self.all_settings[type_settings]['buttons'] = SettingsButtons
            self.all_settings[type_settings]['elements'] = SettingsElements

    def update(self, mouse, events):
        self.mouse = mouse
        for label in self.all_settings[self.active_settings]['labels']:
            if self.active_element:
                label.update(self.game_language[self.active_element])
            else:
                label.update()
            self.surface.blit(label.image, label.rect)

        sett = self.all_settings[self.active_settings]
        for sprite in sett['buttons']:
            sprite.update()
            if sprite.isCollide() and self.mouse:
                for n, i in enumerate(self.game_language.values()):
                    if i == sprite.text:
                        break
                el = list(self.game_language.keys())[n]
                self.active_settings = el
                self.mouse = False
            self.surface.blit(sprite.image, sprite.rect)

        for n, sprite in enumerate(sett['elements']):
            self.surface.blit(sprite.image, sprite.rect)
            if not self.active_element:
                name = sprite.name.split(' ')
                if sprite.value != self.settings[name[0]][name[1]]:
                    sprite.value = self.settings[name[0]][name[1]]
                SpriteUpdate: dict = sprite.update(self.mouse)
                if SpriteUpdate:
                    if type(SpriteUpdate) is bool:
                        self.active_element = sprite.name
                    elif type(SpriteUpdate) is int:
                        self.active_element = sprite.name
                        self.mouse = False
                    elif type(SpriteUpdate) is dict:
                        temp = tuple(SpriteUpdate.keys())[0]
                        if temp:
                            temp2 = temp.split(' ')
                            self.settings[temp2[0]][temp2[1]] = SpriteUpdate[temp]
                            self.all_settings[self.active_settings]['elements'][n].value = SpriteUpdate[temp]
                        self.mouse = False
            else:
                if sprite.name != self.active_element:
                    sprite.update(False)
                else:
                    SpriteUpdate: dict = sprite.update(self.mouse)
                    if SpriteUpdate:
                        if type(SpriteUpdate) != bool:
                            temp = tuple(SpriteUpdate.keys())[0]
                            temp2 = temp.split(' ')
                            self.settings[temp2[0]][temp2[1]] = SpriteUpdate[temp]
                            self.all_settings[self.active_settings]['elements'][n].value = SpriteUpdate[temp]
                            self.active_element = None
                            self.mouse = False
                        else:
                            self.active_element = None
                            self.mouse = False

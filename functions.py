import os
import log
import sys
import glob
import copy
import json
import stun
import time
import socket
import psutil
import pygame
import random
import win32gui
import requests
import threading
import traceback
import Reg as reg
import subprocess
import win32process
import win32com.client
from constants import *
from ctypes import windll
from scene.Settings import *
from ast import literal_eval
from report import send_message
from screeninfo import get_monitors
from urllib.parse import urlparse, parse_qs
from netifaces import interfaces, ifaddresses, AF_INET
from log import log, consoleHandler, fileHandler, print


class DATA(dict):
    def __init__(self, data):
        for name, value in data.items():
            try:
                setattr(self, name, self._wrap(value))
            except TypeError:
                break
        super().__init__(data)

    def __getattr__(self, item):
        return self.get(str(item))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return DATA(value) if isinstance(value, dict) else value


class SIZE(tuple):
    def __init__(self, data):
        self.w = data[0]
        self.h = data[1]


def read_dictionary(exemplar_dict, dictionary):
    for key in dictionary:
        exemplar_dict[key] = dictionary[key]
    return exemplar_dict


def replace_str_var(dictionary, self=None):
    str_dict = str(dictionary)
    if '$' in str_dict:
        split_by_md = str_dict.split('$')
        for md in split_by_md:
            if '%' in md:
                md = md.split('%')[0]
                try:
                    if self is not None:
                        str_dict = str_dict.replace(f'${md}%', getattr(self, md))
                    else:
                        str_dict = str_dict.replace(f'${md}%', eval(md))
                except NameError:
                    log.error(f'UNKNOWN VARIABLE: {self}.{md}')
    return literal_eval(str_dict)


class Language(DATA):
    def __init__(self, dict_of_all_languages: dict, default_language, replace_str_to_var=True):
        langs_dict = {}
        for language in dict_of_all_languages:
            dictionary = dict_of_all_languages[language]
            exemplar_dict = copy.deepcopy(DEFAULT_DICTIONARY)
            for key in dictionary:
                exemplar_dict[key] = dictionary[key]
            if replace_str_to_var:
                langs_dict[language] = replace_str_var(exemplar_dict)
            else:
                langs_dict[language] = exemplar_dict
        langs_dict = langs_dict | DATA(langs_dict[default_language])
        super().__init__(langs_dict)
        self.LanguageList = list(dict_of_all_languages.keys())
        self.Language = default_language


def get_hwnd_by_pid(pid):
    hwnd = []
    win32gui.EnumWindows(lambda hw, null: hwnd.append(
        hw if ((win32process.GetWindowThreadProcessId(hw)[1] == pid) and (win32gui.IsWindowVisible(hw))) else 0), None)
    return max(hwnd)

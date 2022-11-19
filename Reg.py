from winreg import *
import argparse
import win32api
import log

APP_NAME = 'osw'


class Data:
    def __init__(self, value, data_type, error=None):
        log.debug(f'value of reg: {value}, type:{data_type}, is error: {error}')
        self.data = value
        self.type = data_type
        self.error = error

    def __repr__(self):
        return self.data

    def __str__(self):
        return str(self.data)


def set_value(key, path, name, value):
    try:
        log.debug(f'setting value with: key:{key}, path: {path}, name: {name}, value: {value}')
        CreateKey(key, path)
        registry_key = OpenKey(key, path, 0, KEY_WRITE)
        SetValueEx(registry_key, name, 0, REG_SZ, value)
        CloseKey(registry_key)
        return True
    except Exception as err:
        log.debug(f'error: {err}.')
        return False


def get_value(key, path, name):
    try:
        log.debug(f'getting value with key: {key}, path: {path}, name: {name}')
        registry_key = OpenKey(key, path, 0, KEY_READ)
        value, regtype = QueryValueEx(registry_key, name)
        CloseKey(registry_key)
        return Data(value, regtype)
    except Exception as err:
        log.debug(f'error: {err}')
        return Data(None, None, err)


def delete_key(key, path):
    try:
        log.debug(f'deleting value with key: {str(key)}, path: {path}')
        registry_key = OpenKey(key, path, 0, KEY_ALL_ACCESS)
        for x in range(QueryInfoKey(registry_key)[0]):
            subkey = EnumKey(registry_key, 0)
            try:
                DeleteKey(registry_key, subkey)
            except Exception:
                delete_key(HKEY_CLASSES_ROOT, fr'{path}\{subkey}')
        log.debug(f'success deleted folder {str(key) + path}, count of keys: {x}')
        DeleteKey(registry_key, "")
        registry_key.Close()
    except Exception as err:
        log.debug(f'error {err}.')
        return err.args


def init_deep_links(path_exe):
    log.debug(f'init deep links api support with reg. path: {path_exe}')
    if path_exe not in str(get_value(HKEY_CLASSES_ROOT, APP_NAME + r'\shell\open\command', None).data):
        log.debug(f'deep links api support is not inited in reg. start init it.')
        set_value(HKEY_CLASSES_ROOT, APP_NAME, None, 'Deep Links')
        set_value(HKEY_CLASSES_ROOT, APP_NAME, 'URL Protocol', None)
        set_value(HKEY_CLASSES_ROOT, APP_NAME + r'\DefaultIcon', None, f'{path_exe}, 1')
        set_value(HKEY_CLASSES_ROOT, APP_NAME + r'\shell\open\command', None, f'{path_exe} --DeepLinksApi "%1"')
    else:
        log.debug(f'deep links api support is already inited in reg.')


def del_deep_link():
    log.debug(f'deleting deep links api support with reg.')
    if get_value(HKEY_CLASSES_ROOT, APP_NAME + r'\shell\open\command', None):
        delete_key(HKEY_CLASSES_ROOT, fr'{APP_NAME}')
    else:
        log.debug(f'deep links api support is not in reg.')


def createParser():
    log.debug(f'inited arg parser.')
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--links', dest='links', action='store_false')
    parser.add_argument('-s', '--size', dest='size')
    parser.add_argument('-t', '--theme', dest='theme', action='store_true')
    parser.add_argument('-L', '--lang', dest='lang', choices=['русский', 'english'])
    parser.add_argument('--DeepLinksApi', dest='DeepLinksApi')
    parser.add_argument('--debug', '-d', dest='debug', type=int)
    log.debug(f'arg parser is inited. to get supported args, restart exe with arg -h/--help')
    return parser


class DATA:
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return DATA(value) if isinstance(value, dict) else value

    def __repr__(self):
        return '{%s}' % str(', '.join("'%s': %s" % (k, repr(v)) for (k, v) in self.__dict__.items()))


def getFileProperties(name:str):
    """
    Read all properties of the given file return them as a dictionary.
    """
    propNames = ('Comments', 'InternalName', 'ProductName',
                 'CompanyName', 'LegalCopyright', 'ProductVersion',
                 'FileDescription', 'LegalTrademarks', 'PrivateBuild',
                 'FileVersion', 'OriginalFilename', 'SpecialBuild')

    props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}

    try:
        fixedInfo = win32api.GetFileVersionInfo(name, '\\')
        props['FixedFileInfo'] = fixedInfo
        props['FileVersion'] = "%d.%d.%d.%d" % (fixedInfo['FileVersionMS'] / 65536,
                                                fixedInfo['FileVersionMS'] % 65536, fixedInfo['FileVersionLS'] / 65536,
                                                fixedInfo['FileVersionLS'] % 65536)
        strInfo = {}
        for propName in propNames:
            strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (*win32api.GetFileVersionInfo(name, '\\VarFileInfo\\Translation')[0], propName)
            strInfo[propName] = win32api.GetFileVersionInfo(name, strInfoPath)

        props['StringFileInfo'] = strInfo
    except Exception:
        pass
    return DATA(props)

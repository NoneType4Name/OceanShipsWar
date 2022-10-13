import winreg as reg
import argparse
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
        reg.CreateKey(key, path)
        registry_key = reg.OpenKey(key, path, 0, reg.KEY_WRITE)
        reg.SetValueEx(registry_key, name, 0, reg.REG_SZ, value)
        reg.CloseKey(registry_key)
        return True
    except Exception as err:
        log.debug(f'error: {err}.')
        return False


def get_value(key, path, name):
    try:
        log.debug(f'getting value with key: {key}, path: {path}, name: {name}')
        registry_key = reg.OpenKey(key, path, 0, reg.KEY_READ)
        value, regtype = reg.QueryValueEx(registry_key, name)
        reg.CloseKey(registry_key)
        return Data(value, regtype)
    except Exception as err:
        log.debug(f'error: {err}')
        return Data(None, None, err)


def delete_key(key, path):
    try:
        log.debug(f'deleting value with key: {str(key)}, path: {path}')
        registry_key = reg.OpenKey(key, path, 0, reg.KEY_ALL_ACCESS)
        for x in range(reg.QueryInfoKey(registry_key)[0]):
            subkey = reg.EnumKey(registry_key, 0)
            try:
                reg.DeleteKey(registry_key, subkey)
            except Exception:
                delete_key(reg.HKEY_CLASSES_ROOT, fr'{path}\{subkey}')
        log.debug(f'success deleted folder {str(key)+path}, count of keys: {x}')
        reg.DeleteKey(registry_key, "")
        registry_key.Close()
    except Exception as err:
        log.debug(f'error {err}.')
        return err.args


def init_deep_links(path_exe):
    log.debug(f'init deep links api support with reg. path: {path_exe}')
    if path_exe not in str(get_value(reg.HKEY_CLASSES_ROOT, APP_NAME+r'\shell\open\command', None).data):
        log.debug(f'deep links api support is not inited in reg. start init it.')
        set_value(reg.HKEY_CLASSES_ROOT, APP_NAME, None, 'Deep Links')
        set_value(reg.HKEY_CLASSES_ROOT, APP_NAME, 'URL Protocol', None)
        set_value(reg.HKEY_CLASSES_ROOT, APP_NAME+r'\DefaultIcon', None, f'{path_exe}, 1')
        set_value(reg.HKEY_CLASSES_ROOT, APP_NAME+r'\shell\open\command', None, f'{path_exe} --DeepLinksApi "%1"')
    else:
        log.debug(f'deep links api support is already inited in reg.')


def del_deep_link():
    log.debug(f'deleting deep links api support with reg.')
    if get_value(reg.HKEY_CLASSES_ROOT, APP_NAME+r'\shell\open\command', None):
        delete_key(reg.HKEY_CLASSES_ROOT, fr'{APP_NAME}')
    else:
        log.debug(f'deep links api support is not in reg.')


def createParser():
    log.debug(f'inited arg parser.')
    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--links', dest='links', action='store_false')
    parser.add_argument('-s','--size', dest='size')
    parser.add_argument('-t','--theme', dest='theme', action='store_true')
    parser.add_argument('-L','--lang', dest='lang', choices=['rus','eng'])
    parser.add_argument('--DeepLinksApi', dest='DeepLinksApi')
    parser.add_argument('--debug', '-d', dest='debug', action='store_true')
    log.debug(f'arg parser is inited. to get supported args, restart exe with arg -h/--help')
    return parser

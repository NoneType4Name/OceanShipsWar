import winreg as reg
APP_NAME = 'OceanShipsWar'


class Data:
    def __init__(self, value, data_type, error=None):
        self.data = value
        self.type = data_type
        self.error = error

    def __repr__(self):
        return self.data


def set_value(key, path, name, value):
    try:
        reg.CreateKey(key, path)
        registry_key = reg.OpenKey(reg.HKEY_CLASSES_ROOT, path, 0, reg.KEY_WRITE)
        reg.SetValueEx(registry_key, name, 0, reg.REG_SZ, value)
        reg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False


def get_value(key, path, name):
    try:
        registry_key = reg.OpenKey(key, path, 0, reg.KEY_READ)
        value, regtype = reg.QueryValueEx(registry_key, name)
        reg.CloseKey(registry_key)
        return Data(value, regtype)
    except Exception as err:
        return Data(None, None, err)


def delete_key(key, path):
    registry_key = reg.OpenKey(key, path, 0, reg.KEY_ALL_ACCESS)
    for x in range(reg.QueryInfoKey(registry_key)[0]):
        subkey = reg.EnumKey(registry_key, 0)
        try:
            reg.DeleteKey(registry_key, subkey)
        except Exception:
            delete_key(reg.HKEY_CLASSES_ROOT, fr'{path}\{subkey}')

    reg.DeleteKey(registry_key, "")
    registry_key.Close()


def init_deep_links():
    if not get_value(reg.HKEY_CLASSES_ROOT, APP_NAME+r'\shell\open\command', None).data:
        set_value(reg.HKEY_CLASSES_ROOT, APP_NAME, None, 'Deep Links')
        set_value(reg.HKEY_CLASSES_ROOT, APP_NAME, 'URL Protocol', None)

        set_value(reg.HKEY_CLASSES_ROOT, APP_NAME+r'\DefaultIcon', None, 'APP_PATH, 1')
        set_value(reg.HKEY_CLASSES_ROOT, APP_NAME+r'\shell\open\command', None, 'APP_PATH "%1"')


init_deep_links()


def del_deep_link():
    if get_value(reg.HKEY_CLASSES_ROOT, APP_NAME+r'\shell\open\command', None).data:
        delete_key(reg.HKEY_CLASSES_ROOT, fr'{APP_NAME}')


del_deep_link()

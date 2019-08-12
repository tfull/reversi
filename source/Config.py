import yaml

DATA = None

class ConfigError(Exception):
    pass

def load():
    global DATA
    with open("config.yml", "r") as f:
        DATA = yaml.load(f, Loader = yaml.FullLoader)

def get(names, must=False, default=None):
    global DATA
    if DATA is None:
        load()

    if type(names) == str:
        name_list = names.split("/")
    else:
        name_list = []
        for name in names:
            name_list.extend(name.split("/"))

    target = DATA

    for name in name_list:
        if type(target) == dict and name in target:
            target = target[name]
        else:
            if default is not None:
                return default
            else:
                if must:
                    raise ConfigError("no field {}".format("/".join(name_list)))
                else:
                    return None

    return target

def get_global(*names, must=False, default=None):
    return get(["global"] + list(names), must=must, default=default)

def get_player(*names, must=False, default=None):
    return get(["players"] + list(names), must=must, default=default)

def get_process(*names, must=False, default=None):
    return get(["processes"] + list(names), must=must, default=default)

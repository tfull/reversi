import os
import yaml


class ConfigError(Exception):
    pass


class Config:
    DATA = None

    @classmethod
    def load(cls):
        with open(os.path.dirname(__file__) + "/../data/config.yml", "r") as f:
            cls.DATA = yaml.load(f, Loader = yaml.FullLoader)

    @classmethod
    def get(cls, names, must=False, default=None):
        if cls.DATA is None:
            cls.load()

        if type(names) == str:
            name_list = names.split("/")
        else:
            name_list = []
            for name in names:
                name_list.extend(name.split("/"))

        target = cls.DATA

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

    @classmethod
    def get_global(cls, *names, must=False, default=None):
        return cls.get(["global"] + list(names), must=must, default=default)

    @classmethod
    def get_player(cls, *names, must=False, default=None):
        return cls.get(["players"] + list(names), must=must, default=default)

    @classmethod
    def get_process(cls, *names, must=False, default=None):
        return cls.get(["processes"] + list(names), must=must, default=default)

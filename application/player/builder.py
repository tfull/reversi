from ..system import Config

class Builder:

    @classmethod
    def build_player(cls, game_config, name, mode = "test"):
        engine = Config.get_player(name, "engine")
        if engine == "RandomPlayer":
            return cls.build_random_player(game_config, name)
        elif engine == "DeepLearningPlayer":
            return cls.build_deep_learning_player(game_config, name, mode = mode)
        elif engine == "KerasPlayer":
            return cls.build_keras_player(game_config, name, mode = mode)
        else:
            raise Exception("not implemented")

    @classmethod
    def build_gui_player(cls, game_config, name):
        from .gui_player import GuiPlayer
        return GuiPlayer(game_config, name = name)

    @classmethod
    def build_random_player(cls, game_config, name):
        from .random_player import RandomPlayer
        return RandomPlayer(game_config, name=name)

    @classmethod
    def build_deep_learning_player(cls, game_config, name, mode="test"):
        from .deep_learning_player import DeepLearningPlayer

        options = { "mode": mode }
        load = Config.get_player(name, "load", must=True)
        if load is not None:
            model_dir = Config.get_global("model_directory", default="model")
            if load == "max":
                filename_list = glob.glob("{0}/{1}/model_*.h5".format(model_dir, name))
                if len(filename_list) > 0:
                    max_count = 0
                    for filename in filename_list:
                        match = re.search(r"model_(\d+)\.h5", filename)
                        max_count = max(max_count, int(match.group(1)))
                    options["load"] = max_count
            else:
                filename_list = glob.glob("{0}/{1}/model_{2}.h5".format(model_dir, name, load))
                if len(file_name_list) != 1:
                    raise Exception("no model {0}".format(load))
                options["load"] = int(load)

        additional_options = Config.get_player(name, "options", default={})
        options = dict(options, **additional_options)

        return DeepLearningPlayer(game_config, name=name, options = options)

    @classmethod
    def build_keras_player(cls, game_config, name, mode="test"):
        from .keras_player import KerasPlayer

        options = { "mode": mode }
        load = Config.get_player(name, "load", must=True)
        if load is not None:
            model_dir = Config.get_global("model_directory", default="model")
            if load == "max":
                filename_list = glob.glob("{0}/{1}/model_*.h5".format(model_dir, name))
                if len(filename_list) > 0:
                    max_count = 0
                    for filename in filename_list:
                        match = re.search(r"model_(\d+)\.h5", filename)
                        max_count = max(max_count, int(match.group(1)))
                    options["load"] = max_count
            else:
                filename_list = glob.glob("{0}/{1}/model_{2}.h5".format(model_dir, name, load))
                if len(file_name_list) != 1:
                    raise Exception("no model {0}".format(load))
                options["load"] = int(load)

        additional_options = Config.get_player(name, "options", default={})
        options = dict(options, **additional_options)

        return KerasPlayer(game_config, name=name, options = options)

import plaidml.keras
plaidml.keras.install_backend()

import random
import os
import numpy as np

import Config
from Player import Player

class KerasPlayer(Player):
    def __init__(self, config, piece = None, name = "keras", options = None):
        super(KerasPlayer, self).__init__(config, piece)
        self.name = name
        options = {} if options is None else options
        self.batch_size = options.get("batch_size") or 100
        self.checkpoint = options.get("checkpoint_interval") or 10000
        self.load_checkpoint = options.get("load")
        self.train_piece = options.get("train_piece") or "single"
        self.model_type = options.get("model") or "Mini"
        self.train_count = 0
        self.policy = build_policy(options.get("policy") or { "mode": "linear_epsilon_greedy", "max": { "count": 0 , "probability": 1.0 }, "min": { "count": 100000, "probability": 0.1 } })
        self.set_mode(options.get("mode") or "train")
        self.setup_brain()

    def debug_string(self):
        st = self.status()
        keys = ["piece", "train_count"]
        return ", ".join(["{0}: {1}".format(key, st[key]) for key in keys])

    def status(self):
        st = super(KerasPlayer, self).status()
        st["train_count"] = self.train_count
        return st

    def print_status(self):
        status = self.status()
        order = ["game_count", "train_count"]
        print(self.name + ":")
        for key in order:
            if key in status:
                print("  {0}: {1}".format(key, status[key]))

    def set_mode(self, mode):
        if mode == "train":
            self.initialize_train_data()
        elif mode == "test":
            pass
        else:
            raise PlayerException("mode: train or test")

        self.mode = mode

    def initialize_train_data(self):
        self.train_x = []
        self.train_y = []

    def random_or_choice(self):
        if self.policy(self.train_count):
            return "choice"
        else:
            return "random"

    def select(self):
        if self.mode == "train":
            movable = self.board.get_movable(self.piece)
            if len(movable) > 0:
                if self.random_or_choice() == "random":
                    return random.choice(movable)
                else:
                    return self.select_by_brain(movable)
            else:
                return None
        else:
            movable = self.board.get_movable(self.piece)
            if len(movable) > 0:
                return self.select_by_brain(movable)
            else:
                return None

    def select_by_brain(self, movable):
        move_board_array = []
        for x, y in movable:
            self.board.move(self.piece, x, y)
            move_board_array.append([self.board.get_array(self.piece)])
            self.board.undo()
        index_argmax = self.brain.argmax(np.array(move_board_array, dtype=np.float32))
        return movable[index_argmax]

    def setup_brain(self):
        self.brain = Model(self.board.size)
        if self.load_checkpoint is not None:
            self.load()

    def learn(self):
        pieces = [self.piece, self.piece.opposite()] if self.train_piece == "both" else [self.piece]
        for piece in pieces:
            history = self.board.get_history_array(piece)
            train_array = [[h] for h in history[1:]]
            self.train_x.extend(train_array)
            score = self.board.get_score(piece) / self.board.size ** 2
            test_array = [[score] for _ in train_array]
            self.train_y.extend(test_array)

        self.train_count += 1

        if self.train_count % self.batch_size == 0:
            self.train()
            self.initialize_train_data()
        if self.train_count % self.checkpoint == 0:
            self.save()

    def train(self):
        train_x = np.array(self.train_x, dtype=np.float32)
        train_y = np.array(self.train_y, dtype=np.float32)
        self.brain.fit(train_x, train_y)

    def complete(self):
        super(KerasPlayer, self).complete()
        if self.mode == "train":
            self.learn()

    def save(self):
        model_dir = Config.get_global("model_directory")
        os.makedirs("{0}/{1}".format(model_dir, self.name), exist_ok=True)
        self.brain.save("{0}/{1}/model_{2}.h5".format(model_dir, self.name, self.train_count))

    def load(self):
        model_dir = Config.get_global("model_directory")
        os.makedirs("{0}/{1}".format(model_dir, self.name), exist_ok=True)
        self.brain.load("{0}/{1}/model_{2}.h5".format(model_dir, self.name, self.load_checkpoint))
        self.train_count = self.load_checkpoint

def build_policy(parameter):
    mode = parameter.get("mode")
    if mode is None:
        raise PlayerException("no policy mode")
    if mode != "linear_epsilon_greedy":
        raise PlayerException("policy {} not implemented".format(mode))

    min_probability = parameter["min"]["probability"]
    min_count = parameter["min"]["count"]
    max_probability = parameter["max"]["probability"]
    max_count = parameter["max"]["count"]

    dc = min_count - max_count
    dp = min_probability - max_probability

    return lambda x: np.clip(dp / dc * (x - max_count) + max_probability, min_probability, max_probability) < random.random()

class Model:
    def __init__(self, size):
        from keras.models import Sequential
        from keras.layers import Reshape, Conv2D, Dropout, MaxPooling2D, Flatten, Dense

        self.model = Sequential([
            Reshape((size, size, 1), input_shape = (1, size, size)),
            Conv2D(3, (3, 3), padding = "same", activation = "relu"),
            Dropout(0.3),
            Conv2D(16, (3, 3), padding = "same", activation = "relu"),
            Dropout(0.3),
            Conv2D(32, (3, 3), padding = "same", activation = "relu"),
            Dropout(0.3),
            Conv2D(64, (3, 3), padding = "same", activation = "relu"),
            MaxPooling2D(pool_size = (2, 2)),
            Flatten(),
            Dense(1024, activation = "relu"),
            Dropout(0.3),
            Dense(128, activation = "relu"),
            Dropout(0.3),
            Dense(32, activation = "relu"),
            Dropout(0.3),
            Dense(1)
        ])

        self.model.compile("adam", "mean_squared_error")

    def fit(self, train_x, train_y):
        self.model.fit(train_x, train_y)

    def argmax(self, test_x):
        prediction = self.model.predict(test_x)
        length = len(prediction)
        return prediction.reshape((length,)).argmax()

    def save(self, path):
        self.model.save_weights(path)

    def load(self, path):
        self.model.load_weights(path)

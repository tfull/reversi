import random
import os
import numpy as np
from chainer import Chain, Variable, optimizers, serializers
import chainer.links as L
import chainer.functions as F

import Config
from Player import *

class DeepLearningPlayer(Player):
    def __init__(self, config, piece=None, name="deep", options = None):
        super(DeepLearningPlayer, self).__init__(config, piece)
        self.name = name
        options = {} if options is None else options
        self.batch_size = options.get("batch_size") or 100
        self.checkpoint = options.get("checkpoint") or 1000
        self.load_checkpoint = options.get("load")
        self.train_x = []
        self.train_y = []
        self.train_count = 0
        self.set_mode(options.get("mode") or "train")
        self.setup_brain()

    def status(self):
        st = super(DeepLearningPlayer, self).status()
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
        if mode not in ["train", "test"]:
            raise Exception("train or test")
        self.mode = mode

    def random_or_choice(self):
        if max(0.1, 1 - (0.9 / 100000) * self.train_count) < random.random():
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
        self.brain = Brain()
        self.brain_optimizer = optimizers.Adam()
        self.brain_optimizer.setup(self.brain)
        if self.load_checkpoint is not None:
            self.load()

    def save(self):
        model_dir = Config.get_global("model_directory")
        os.makedirs("{0}/{1}".format(model_dir, self.name), exist_ok=True)
        serializers.save_hdf5("{0}/{1}/model_{2}.h5".format(model_dir, self.name, self.train_count), self.brain)
        serializers.save_hdf5("{0}/{1}/optimizer_{2}.h5".format(model_dir, self.name, self.train_count), self.brain_optimizer)

    def load(self):
        model_dir = Config.get_global("model_directory")
        os.makedirs("{0}/{1}".format(model_dir, self.name), exist_ok=True)
        serializers.load_hdf5("{0}/{1}/model_{2}.h5".format(model_dir, self.name, self.load_checkpoint), self.brain)
        serializers.load_hdf5("{0}/{1}/optimizer_{2}.h5".format(model_dir, self.name, self.load_checkpoint), self.brain_optimizer)
        self.train_count = self.load_checkpoint

    def learn(self):
        history = self.board.get_history_array(self.piece)
        train_array = [[h] for h in history[1:]]
        self.train_x.extend(train_array)
        score = self.board.get_score(self.piece) / self.board.size ** 2
        test_array = [[score] for _ in train_array]
        self.train_y.extend(test_array)
        self.train_count += 1
        if self.train_count % self.batch_size == 0:
            self.train(np.array(self.train_x, dtype=np.float32), np.array(self.train_y, dtype=np.float32))
            self.train_x = []
            self.train_y = []
        if self.train_count % self.checkpoint == 0:
            self.save()

    def train(self, train_x, train_y):
        loss = self.brain.loss(train_x, train_y)
        self.brain.cleargrads()
        loss.backward()
        self.brain_optimizer.update()

    def complete(self):
        super(DeepLearningPlayer, self).complete()
        if self.mode == "train":
            self.learn()

class Brain(Chain):
    def __init__(self):
        super(Brain, self).__init__(
            conv1 = L.Convolution2D(1, 3, ksize=3, pad=1),
            conv2 = L.Convolution2D(3, 2, ksize=3, pad=1),
            l1 = L.Linear(None, 32),
            l2 = L.Linear(32, 1)
        )

    def __call__(self, x):
        return self.forward(x)

    def forward(self, x):
        h = F.relu(self.conv1(x))
        h = F.max_pooling_2d(F.relu(self.conv2(h)), 2)
        h = F.relu(self.l1(h))
        return self.l2(h)

    def argmax(self, x):
        h = self.forward(x)
        length = len(h)
        return h.data.reshape((length,)).argmax()

    def loss(self, x, y):
        return F.mean_squared_error(self.forward(x), Variable(y))

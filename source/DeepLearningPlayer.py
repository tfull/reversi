from chainer import Chain, Variable, optimizers
import chainer.links as L
import chainer.functions as F
import numpy as np
import random

from Player import Player

class DeepLearningPlayer(Player):
    def __init__(self, config, piece=None, options = None):
        super(DeepLearningPlayer, self).__init__(config, piece)
        options = {} if options is None else options
        self.batch_size = options.get("batch_size") or 100
        self.checkpoint = options.get("checkpoint") or 10000
        self.name = options.get("name") or "deep"
        self.train_x = []
        self.train_y = []
        self.mode = "train"

    def set_mode(self, mode):
        self.mode = mode

    def select(self):
        if self.mode == "train":
            movable = self.board.get_movable(self.piece)
            if len(movable) > 0:
                return random.choice(movable)
            else:
                return None
        else:
            movable = self.board.get_movable(self.piece)
            if len(movable) > 0:
                move_board_array = []
                for x, y in movable:
                    self.board.move(self.piece, x, y)
                    move_board_array.append([self.board.get_array(self.piece)])
                    self.board.undo()
                index_argmax = self.brain.argmax(np.array(move_board_array, dtype=np.float32))
                return movable[index_argmax]
            else:
                return None

    def setup_brain(self):
        self.brain = Brain()
        self.brain_optimizer = optimizers.Adam()
        self.brain_optimizer.setup(self.brain)

    def learn(self):
        history = self.board.get_history_array(self.piece)
        train_array = [[h] for h in history[1:]]
        self.train_x.extend(train_array)
        score = self.board.get_score(self.piece) / self.board.size ** 2
        test_array = [[score] for _ in train_array]
        self.train_y.extend(test_array)
        if len(self.train_x) >= self.batch_size:
            self.train(np.array(self.train_x, dtype=np.float32), np.array(self.train_y, dtype=np.float32))
            self.train_x = []
            self.train_y = []

    def train(self, train_x, train_y):
        loss = self.brain.loss(train_x, train_y)
        self.brain.cleargrads()
        loss.backward()
        self.brain_optimizer.update()

    def save(self):
        pass

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

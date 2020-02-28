import queue
import threading

from ..core import *
from .default_player import DefaultPlayer


class GuiPlayer(DefaultPlayer):
    def __init__(self, config, piece=None, name="gui", options=None):
        super(GuiPlayer, self).__init__(config, piece)
        options = {} if options is None else options
        self.name = name
        self.engine = "GuiPlayer"
        self.config = config

    def set_queue(self, read_queue, write_queue):
        self.read_queue = read_queue
        self.write_queue = write_queue

    def move(self, piece, x, y):
        super(GuiPlayer, self).move(piece, x, y)
        self.write_queue.put("flip")
        print("player: move", (x, y), self.piece.description())

    def select(self):
        if self.board.full():
            return None

        movable = self.board.get_movable(self.piece)

        # debug
        """
        import random
        return random.choice(movable) if len(movable) > 0 else None
        """

        while True:
            try:
                self.read_queue.get_nowait()
            except queue.Empty:
                break

        while True:
            action = self.read_queue.get()
            print("player:", action, str(movable))

            if action == "surrender":
                return "surrender"

            if action in movable:
                print("player: act")
                return action

            if action == "pass" and len(movable) == 0:
                return None

    def complete(self):
        super(GuiPlayer, self).complete()
        self.write_queue.put("complete")

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

    """
    def game_loop(self):
        self.gui_color()
        if self.piece == Piece.BLACK:
            self.initialize(Piece.BLACK)
            self.opponent.initialize(Piece.WHITE)
            self.render_field()
        else:
            self.initialize(Piece.WHITE)
            self.opponent.initialize(Piece.BLACK)
            self.render_field()

        game = Game(self.config, self if self.piece == Piece.BLACK else self.opponent, self.opponent if self.piece == Piece.BLACK else self)
        game.play()
    """

    def move(self, piece, x, y):
        super(GuiPlayer, self).move(piece, x, y)
        # + sleep
        self.write_queue.put("flip")
        print("player: move", (x, y), self.piece.description())
        # self.render_field()

    def select(self):
        movable = self.board.get_movable(self.piece)

        while True:
            try:
                self.read_queue.get_nowait()
            except queue.Empty:
                break

        while True:
            action = self.read_queue.get()
            print("player:", action, str(movable))
            if action in movable:
                print("player: act")
                return action

            if action == "pass" and len(movable) == 0:
                return None

        """
        import random
        if len(movable) > 0:
            return random.choice(movable)
        else:
            return None
        """

    """
    def render_field(self):
        h = self.height
        self.canvas.create_rectangle(0, 0, h, h, fill = "gray")
        margin = h // 10
        size = self.board.size

        for i in range(size):
            for j in range(size):
                cell_size = (8 * h) // (10 * size)
                top = margin + i * cell_size
                left = margin + j * cell_size
                piece = self.board.get(j, i)

                if piece == Piece.BLACK:
                    color = "black"
                elif piece == Piece.WHITE:
                    color = "white"
                else:
                    color = "green"

                self.canvas.create_rectangle(left, top, left + cell_size, top + cell_size, fill = color)

    def gui_color(self):
        height = self.height
        self.mode = "color"
        self.canvas.create_rectangle(0, 0, height // 2, height, fill = "black")
        self.canvas.create_rectangle(height // 2, 0, height, height, fill = "white")
        self.status = "receive"

        while True:
            x, y = self.queue.get()
            self.status = "suspend"

            if x < height // 2:
                self.piece = Piece.BLACK
                return
            elif x < height:
                self.piece = Piece.WHITE
                return
            else:
                self.status = "receive"

    def set_opponent(self, opponent):
        self.opponent = opponent

    def click(self, x, y):
        print("clicked")
        if self.status == "receive" and self.queue.empty():
            self.queue.put((x, y))

    def mainloop(self):
        self.canvas.mainloop()
    """

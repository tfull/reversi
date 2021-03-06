import tkinter as tk
import queue
import threading
from enum import Enum

from ..core import *


class Scene(Enum):
    COLOR = 0
    BOARD = 1
    RESULT = 2


class GuiAgent:
    WIDTH = 1280
    HEIGHT = 720

    def __init__(self, gui_player, other_player):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.title("Reversi")

        self.canvas = tk.Canvas(self.root, width = self.WIDTH, height = self.HEIGHT)
        self.canvas.pack()

        self.draw_count = (0, 0)

        self.gui_player = gui_player
        self.other_player = other_player

        def click(event):
            self.click(event.x, event.y)

        self.canvas.bind("<Button-1>", click)

        self.set_scene(Scene.COLOR)

        self.write_queue = queue.Queue()
        self.read_queue = queue.Queue()
        self.gui_player.set_queue(self.write_queue, self.read_queue)

        self.draw_thread = threading.Thread(target = self.draw_loop)
        self.draw_thread.start()

        self.game_thread = None

        self.click_valid = True

    def click(self, x, y):
        if not self.click_valid:
            return

        self.click_valid = False

        self.act_scene(x, y)

        self.click_valid = True

    def act_scene(self, x, y):
        if self.scene == Scene.COLOR:
            self.act_scene_color(x, y)
        elif self.scene == Scene.BOARD:
            self.act_scene_board(x, y)
        elif self.scene == Scene.RESULT:
            self.act_scene_result(x, y)

    def act_scene_color(self, x, y):
        h = self.HEIGHT

        if x < h // 2:
            self.gui_player.initialize(Piece.BLACK)
            self.other_player.initialize(Piece.WHITE)
            self.game = Game(self.gui_player.config, self.gui_player, self.other_player)
        else:
            self.gui_player.initialize(Piece.WHITE)
            self.other_player.initialize(Piece.BLACK)
            self.game = Game(self.gui_player.config, self.other_player, self.gui_player)

        if self.game_thread is not None:
            self.game_thread.join()

        self.game_thread = threading.Thread(target = self.game.play)
        self.game_thread.start()

        self.set_scene(Scene.BOARD)

    def act_scene_board(self, x, y):
        print("act_scene_board", x, y)

        h = self.HEIGHT
        size = self.game.board.size
        margin = h // 10
        cell_size = (8 * h) // (10 * size)
        x_board = (x - margin) // cell_size
        y_board = (y - margin) // cell_size

        print("x_board:", x_board, ", y_board:", y_board)

        if x_board in range(size) and y_board in range(size):
            self.write_queue.put((x_board, y_board))

    def act_scene_result(self, x, y):
        h = self.HEIGHT
        if x >= h and x < (11 * h) // 10 and y >= 0 and y <= h // 10:
            self.set_scene(Scene.COLOR)

    def set_scene(self, scene):
        self.draw_scene(scene)
        self.scene = scene

    def draw_scene(self, scene):
        latest = self.update_draw_count()

        if scene == Scene.COLOR:
            self.draw_scene_color(latest)
        elif scene == Scene.BOARD:
            self.draw_scene_board(latest)
        elif scene == Scene.RESULT:
            self.draw_scene_result(latest)
        else:
            raise Exception("not implemented")

        self.delete_old_elements()

    def draw_scene_color(self, latest):
        h = self.HEIGHT

        tag = "draw_{}".format(latest)
        black = self.canvas.create_rectangle(0, 0, h // 2, h, fill = "black", tags = tag)
        white = self.canvas.create_rectangle(h // 2, 0, h, h, fill = "white", tags = tag)

    def draw_scene_board(self, latest):
        self.draw_board(latest)

    def draw_scene_result(self, latest):
        tag = "draw_{}".format(latest)

        h = self.HEIGHT
        self.draw_board(latest)
        self.canvas.create_rectangle(h, 0, (11 * h) // 10, h // 10, fill = "red", tags = tag)

    def draw_board(self, count):
        piece_margin = 2
        h = self.HEIGHT
        size = self.game.board.size
        margin = h // 10
        cell_size = (8 * h) // (10 * size)

        tag = "draw_{}".format(count)

        self.canvas.create_rectangle(margin - 3, margin - 3, h - margin + 3, h - margin + 3, fill = "#004400", width = 0, tags = tag)

        for i in range(size):
            for j in range(size):
                top = margin + i * cell_size
                left = margin + j * cell_size
                piece = self.game.board.get(j, i)

                self.canvas.create_rectangle(left, top, left + cell_size, top + cell_size, fill = "green", outline = "#004400", tags = tag)

                if piece == Piece.BLACK:
                    pm = piece_margin
                    color = "black"
                    border = "white"
                    self.canvas.create_oval(left + pm, top + pm, left + cell_size - pm, top + cell_size - pm, fill = color, outline = border, tags = tag)
                elif piece == Piece.WHITE:
                    pm = piece_margin
                    color = "white"
                    border = "black"
                    self.canvas.create_oval(left + pm, top + pm, left + cell_size - pm, top + cell_size - pm, fill = color, outline = border, tags = tag)

    def draw_loop(self):
        while True:
            item = self.read_queue.get()

            if item == "end":
                return
            elif item == "complete":
                self.set_scene(Scene.RESULT)
            else:
                print("draw_loop:", item)
                latest = self.update_draw_count()
                self.draw_scene_board(latest)

    def update_draw_count(self):
        latest, deleted = self.draw_count
        self.draw_count = (latest + 1, deleted)
        return latest + 1

    def delete_old_elements(self):
        latest, deleted = self.draw_count
        for count in range(deleted, latest):
            self.canvas.delete("draw_{}".format(count))
            deleted = count

        self.draw_count = (latest, deleted)

    def main_loop(self):
        self.canvas.mainloop()
        self.draw_thread.join()

    def quit(self):
        self.read_queue.put("end")
        self.write_queue.put("surrender")

        if self.game_thread is not None:
            self.game_thread.join()

        self.root.destroy()

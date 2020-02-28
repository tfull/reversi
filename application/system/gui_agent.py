import tkinter as tk
import queue
import threading

from ..core import *

class Scene:
    COLOR = 0
    BOARD = 1
    RESULT = 2

class GuiAgent:
    WIDTH = 1280
    HEIGHT = 720

    def __init__(self, gui_player, other_player):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        self.canvas = tk.Canvas(self.root, width = self.WIDTH, height = self.HEIGHT)
        self.canvas.pack()

        self.gui_player = gui_player
        self.other_player = other_player

        def click(event):
            self.click(event.x, event.y)

        self.canvas.bind("<Button-1>", click)

        self.element = {
            Scene.COLOR: [],
            Scene.BOARD: [],
            Scene.RESULT: []
        }

        self.set_scene(Scene.COLOR)

        self.write_queue = queue.Queue()
        self.read_queue = queue.Queue()
        self.gui_player.set_queue(self.write_queue, self.read_queue)

        self.draw_thread = threading.Thread(target = self.draw_loop)
        self.draw_thread.start()

        self.game_thread = None

        self.draw_count = (0, 0) # now tag number, last deleted tag number

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
        if scene == Scene.COLOR:
            self.draw_scene_color()
        elif scene == Scene.BOARD:
            self.draw_scene_board()
        elif scene == Scene.RESULT:
            self.draw_scene_result()

    def draw_scene_color(self):
        if len(self.element[Scene.RESULT]) > 0:
            old = self.element[Scene.RESULT]
            self.element[Scene.RESULT] = []
        else:
            old = []

        h = self.HEIGHT

        black = self.canvas.create_rectangle(0, 0, h // 2, h, fill = "black")
        white = self.canvas.create_rectangle(h // 2, 0, h, h, fill = "white")

        self.element[Scene.COLOR] = [black, white]

        self.delete_elements(old)

    def draw_scene_board(self):
        old = []
        if len(self.element[Scene.COLOR]) > 0:
            old += self.element[Scene.COLOR]
            self.element[Scene.COLOR] = []

        if len(self.element[Scene.BOARD]) > 0:
            old += self.element[Scene.BOARD]
            self.element[Scene.BOARD] = []

        self.draw_board(self.element[Scene.BOARD])

        self.delete_elements(old)

    def draw_scene_result(self):
        if len(self.element[Scene.BOARD]) > 0:
            old = self.element[Scene.BOARD]
            self.element[Scene.BOARD] = []
        else:
            old = []

        h = self.HEIGHT
        self.draw_board(self.element[Scene.RESULT])
        button = self.canvas.create_rectangle(h, 0, (11 * h) // 10, h // 10, fill = "red")
        self.element[Scene.RESULT].append(button)
        self.delete_elements(old)

    def draw_board(self, elements):
        h = self.HEIGHT
        size = self.game.board.size
        margin = h // 10
        cell_size = (8 * h) // (10 * size)

        for i in range(size):
            for j in range(size):
                top = margin + i * cell_size
                left = margin + j * cell_size
                piece = self.game.board.get(j, i)

                if piece == Piece.BLACK:
                    color = "black"
                elif piece == Piece.WHITE:
                    color = "white"
                else:
                    color = "green"

                cell = self.canvas.create_rectangle(left, top, left + cell_size, top + cell_size, fill = color)
                elements.append(cell)

    def draw_loop(self):
        while True:
            item = self.read_queue.get()

            if item == "end":
                return
            elif item == "complete":
                self.set_scene(Scene.RESULT)
            else:
                print("draw_loop:", item)
                self.draw_scene_board()

    def delete_elements(self, elements):
        for e in elements:
            self.canvas.delete(e)

    def main_loop(self):
        self.canvas.mainloop()
        self.draw_thread.join()

    def quit(self):
        self.read_queue.put("end")
        self.write_queue.put("surrender")

        if self.game_thread is not None:
            self.game_thread.join()

        self.root.destroy()

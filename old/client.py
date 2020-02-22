import sys
import socket
import yaml
import random
from io import StringIO

def opposite_piece(piece):
    if piece == "x":
        return "o"
    elif piece == "o":
        return "x"
    else:
        return None 

def encode_place(x, y):
    return chr(y + ord("A")) + str(x + 1)

def decode_place(code):
    return (int(code[1]) - 1, ord(code[0]) - ord("A"))

class ClientError(Exception):
    pass

class Client:
    def __init__(self, sock):
        self.socket = sock
        self.buffer = ""

    def receive(self):
        while True:
            ix = self.buffer.find("\n\n")
            if ix >= 0:
                string = self.buffer[:ix + 2]
                self.buffer = self.buffer[ix + 2:]
                return yaml.load(string)
            received = self.socket.recv(1024)
            if received == b"":
                raise ClientError("network disconnected")
            self.buffer += str(received, "UTF-8")

    def wait(self, status):
        entry = self.receive()
        assert(entry["status"] == status)
        return entry

    def send(self, entry):
        self.socket.send(bytes(yaml.dump(entry, default_flow_style=False), "UTF-8") + b"\n")

    def main_loop(self):
        self.wait("connected")
        entry = self.wait("request")
        self.send({ "status": "request", "board_size": 8, "piece": None })
        entry = self.wait("start")
        self.game = Game(entry)
        self.game_loop()

    def game_loop(self):
        while True:
            self.game.print_board()
            entry = self.receive()
            if entry["status"] == "you":
                moves = self.game.get_movable_places()
                if len(moves) == 0:
                    self.send({ "status": "move", "code": "pass" })
                else:
                    x, y = random.choice(moves)
                    self.game.put_piece(self.game.piece, x, y)
                    self.send({ "status": "move", "code": encode_place(x, y) })
                self.receive()
            elif entry["status"] == "opposite":
                opposite_entry = self.receive()
                if opposite_entry["code"] != "pass":
                    x, y = decode_place(opposite_entry["code"])
                    self.game.put_piece(self.game.opposite, x, y)
            else:
                print(entry["result"])
                return

class GameError(Exception):
    pass

class Game:
    def __init__(self, entry):
        self.board_size = entry["board_size"]
        board_string = entry["board_string"]
        self.board = [[board_string[i * self.board_size + j] for j in range(self.board_size)] for i in range(self.board_size)]
        self.piece = entry["piece"]
        self.opposite = opposite_piece(self.piece)

    def print_board(self):
        print("  " + "".join([str(x + 1) for x in range(self.board_size)]))
        print("-+" + "-" * self.board_size)
        for y in range(self.board_size):
            print(chr(ord("A") + y) + "|" +  "".join(self.board[y]))

    def get_movable_places(self):
        return [(x, y) for y in range(self.board_size) for x in range(self.board_size) if self.put_piece(self.piece, x, y, True)]

    def valid_board_range(self, x, y):
        return 0 <= x and x < self.board_size and 0 <= y and y < self.board_size

    def put_piece(self, piece, x, y, test=False):
        if self.board[y][x] != ".":
            if test:
                return False
            else:
                raise GameError("already put piece")

        targets = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                px = x + dx
                py = y + dy

                if not (self.valid_board_range(px, py) and self.board[py][px] == opposite_piece(piece)):
                    continue

                targets_direction = []

                while True:
                    targets_direction.append((px, py))
                    px += dx
                    py += dy
                    if not (self.valid_board_range(px, py) and self.board[py][px] == opposite_piece(piece)):
                        break

                if self.valid_board_range(px, py) and self.board[py][px] == piece:
                    targets.append(targets_direction)

        moves = [p for ts in targets for p in ts]

        if len(moves) == 0:
            if test:
                return False
            else:
                raise GameError("no turn pieces")
        else:
            if not test:
                for (mx, my) in moves:
                    self.board[my][mx] = piece
                self.board[y][x] = piece
            return True

def main(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        client = Client(sock)
        client.main_loop()

if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))

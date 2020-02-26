import sys
import threading

from application.system import Config, Process, GuiAgent

def main(process_name):
    process = Process(process_name)

    names = list(process.players.keys())

    if process.players[names[0]].engine == "GuiPlayer":
        you = process.players[names[0]]
        opponent = process.players[names[1]]
    elif process.players[names[1]].engine == "GuiPlayer":
        you = process.players[names[1]]
        opponent = process.players[names[0]]
    else:
        raise Exception("no gui player")

    gui_agent = GuiAgent(you, opponent)

    """
    you.set_opponent(opponent)
    thread = threading.Thread(target = you.game_loop)
    thread.start()
    you.mainloop()
    thread.join()
    """

    gui_agent.main_loop()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("few arguments\n")
        sys.exit(1)

    main(sys.argv[1])

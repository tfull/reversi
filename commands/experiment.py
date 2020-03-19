import _common

import sys

from application.system.process import Process

def main(process_name):
    process = Process(process_name)
    process.run()

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        sys.stderr.write("Error: few arguments\n")
        sys.exit(1)

    main(sys.argv[1])

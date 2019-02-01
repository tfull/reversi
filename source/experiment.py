import sys

from Process import Process

def main(process_name):
    process = Process(process_name)
    process.run()

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        sys.stderr.write("Error: 2 arguments are required\n")
    main(sys.argv[1])

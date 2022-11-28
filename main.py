import sys
import threading

from base import *

def main():
    urls = sys.argv[1:]

    connections = []
    for url in urls:
        t = threading.Thread(target=download, args=(url,))
        t.start()
        connections.append(t)

    for thread in connections:
        thread.join()

if __name__ == '__main__':
    main()
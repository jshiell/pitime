import sys

from pitime import PiTime


def main(args):
    fullscreen = False

    if '--fullscreen' in args:
        fullscreen = True

    return PiTime(fullscreen).run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))

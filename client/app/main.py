import core.globals as g
from core.mother_base import MotherBase


mother_ws = 'ws://motherbase:1337/ws'


def main():
    g.init()
    matb = MotherBase(mother_ws)


if __name__ == "__main__":
    main()
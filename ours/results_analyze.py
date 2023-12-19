import sys
import pathlib


def print_best_hp(_path: str):
    print(_path)
    for _npz in pathlib.Path(_path).glob("*.npz"):
        print(_npz)
    


if __name__ == "__main__":
    print_best_hp(_path=sys.argv[0])
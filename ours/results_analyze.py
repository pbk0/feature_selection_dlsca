import sys
import pathlib
import numpy as np


def print_best_hp(_path: str):
    print(_path)
    for _npz in pathlib.Path(_path).glob("*"):
        if _npz.name.endswith(".log"):
            continue
        _data = np.load(_npz)["npz_dict"]
        print(_data["hp"])
    


if __name__ == "__main__":
    print_best_hp(_path=sys.argv[1])
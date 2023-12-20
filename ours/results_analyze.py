import sys
import pathlib
import numpy as np


def print_best_hp(_path: str):
    _nt_attack = np.inf
    _best_results = None
    _total_experiments = 0
    for _npz in pathlib.Path(_path).glob("*"):
        if _npz.name.endswith(".log"):
            continue
        _total_experiments += 1
        _data = np.load(_npz, allow_pickle=True)["npz_dict"][()]
        if _data["nt_attack"] < _nt_attack:
            _nt_attack = _data["nt_attack"]
            _best_results = _data
    print("total experiments", _total_experiments)
    for _k, _v in _best_results.items():
        print("   >> ", _k, _v)
    


if __name__ == "__main__":
    
    _path = sys.argv[1]
    _mode = sys.argv[2]
    
    if _mode == "pbhp":
        print_best_hp(_path=_path)
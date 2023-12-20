import sys
import pathlib
import numpy as np


def print_best_hp(_path: str):
    _nt_attack = np.inf
    _best_results = None
    _best_results_file = None
    _total_experiments = 0
    for _npz in pathlib.Path(_path).glob("*"):
        if not _npz.name.endswith(".npz"):
            continue
        _total_experiments += 1
        _data = np.load(_npz, allow_pickle=True)["npz_dict"][()]
        if _data["nt_attack"] < _nt_attack:
            _nt_attack = _data["nt_attack"]
            _best_results = _data
            _best_results_file = _npz
    print("total experiments", _total_experiments)
    print("best results for", _best_results_file)
    for _k, _v in _best_results.items():
        if isinstance(_v, list):
            print("   >> ", _k, np.asarray(_v))
        else:
            print("   >> ", _k, _v)
    

def best_model_runs(_path: str):
    _total_experiments = 0
    _results = {
        "mlp": {"ID": [], "HW": []},
        "cnn": {"ID": [], "HW": []},
    }
    for _npz in pathlib.Path(_path).glob("*"):
        if not _npz.name.endswith(".npz"):
            continue
        _tokens = _npz.name.split("_")
        _model_type = _tokens[0]
        _lk_model = _tokens[1]
        _total_experiments += 1
        _data = np.load(_npz, allow_pickle=True)["npz_dict"][()]
        _results[_model_type][_lk_model].append(
            _data["nt_attack"]
        )
    print(_results)
    

if __name__ == "__main__":

    _mode = sys.argv[1]
    _path = sys.argv[2]
    
    if _mode == "pbhp":
        print_best_hp(_path=_path)
    elif _mode == "bmr":
        best_model_runs(_path=_path)
    else:
        raise Exception(f"Unsupported {_mode=}")
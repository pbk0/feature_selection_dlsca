import subprocess
import sys
import pathlib
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


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
    _results = {
        "MLP:ID": {"nt_attack": [], "failed": 0, "total": 0},
        "MLP:HW": {"nt_attack": [], "failed": 0, "total": 0},
        "CNN:ID": {"nt_attack": [], "failed": 0, "total": 0},
        "CNN:HW": {"nt_attack": [], "failed": 0, "total": 0},
    }
    for _npz in pathlib.Path(_path).glob("*"):
        if not _npz.name.endswith(".npz"):
            continue
        _tokens = _npz.name.split("_")
        _key = f"{_tokens[0].upper()}:{_tokens[1]}"
        _data = np.load(_npz, allow_pickle=True)["npz_dict"][()]
        _nt_attack = _data["nt_attack"]
        _results[_key]["nt_attack"].append(_nt_attack)
        if _nt_attack >= 3000:
            _results[_key]["failed"] += 1
        _results[_key]["total"] += 1
        
    # make dataframe
    _df = pd.DataFrame()
    _df["MLP:ID"] = _results["MLP:ID"]["nt_attack"]
    _df["MLP:HW"] = _results["MLP:HW"]["nt_attack"]
    _df["CNN:ID"] = _results["CNN:ID"]["nt_attack"]
    _df["CNN:HW"] = _results["CNN:HW"]["nt_attack"]
    _df[_df >= 1000] = np.inf
    
    # customizing runtime configuration stored
    # in matplotlib.rcParams
    # plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    
    # violin plot
    _catplot = sns.swarmplot(
        data=_df,
        alpha=0.5, s=2,
    )
    # for ax in _catplot.fig.axes:
    #     ax.set_yscale('log')
    
    for _k in _results.keys():
        print(_results[_k])
        _failed_percent = _results[_k]["failed"] / _results[_k]["total"]
        _nt_attack = _results[_k]["nt_attack"]
        _failed = _failed_percent > 0
        _color = "red" if _failed else "blue"
        _fontsize = 8
        _offset = _fontsize + 2
        for _i, _msg in enumerate([
            f"failed: {_failed_percent:.2f}%",
            f"min: {min(_nt_attack)}",
            f"max: {'NA' if _failed else max(_nt_attack)}",
        ]):
            _catplot.text(
                _k, 1000 + (_i+1)*_offset, _msg,
                    fontsize=_fontsize,  # Size
                    fontstyle="oblique",  # Style
                    color=_color,  # Color
                    ha="center",  # Horizontal alignment
                    va="center",  # Vertical alignment
            )
    
    fig1 = plt.figure()
    plt.plot([17, 45, 7, 8, 7], color='orange')
    
    fig2 = plt.figure()
    plt.plot([13, 25, 1, 6, 3], color='blue')
    
    Fig3 = plt.figure()
    plt.plot([22, 11, 2, 1, 23], color='green')
    
    # PdfPages is a wrapper around pdf
    # file so there is no clash and create
    # files with no error.
    _pdf_file = pathlib.Path(_path) / "best_model_runs.pdf"
    _pdf_file.unlink(missing_ok=True)
    _p = PdfPages(_pdf_file)
    
    # get_fignums Return list of existing
    # figure numbers
    fig_nums = plt.get_fignums()
    figs = [plt.figure(n) for n in fig_nums]
    
    # iterating over the numbers in list
    for fig in figs:
        # and saving the files
        fig.savefig(_p, format='pdf', dpi=300)
        
        # close the object
    _p.close()
    
    subprocess.run(["xdg-open", _pdf_file.absolute().resolve().as_posix()])
    

if __name__ == "__main__":

    _mode = sys.argv[1]
    _path = sys.argv[2]
    
    if _mode == "pbhp":
        print_best_hp(_path=_path)
    elif _mode == "bmr":
        best_model_runs(_path=_path)
    else:
        raise Exception(f"Unsupported {_mode=}")
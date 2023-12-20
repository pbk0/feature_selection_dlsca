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
        
    # make dataframe
    _df = pd.DataFrame()
    _df["MLP:ID"] = _results["mlp"]["ID"]
    _df["MLP:HW"] = _results["mlp"]["HW"]
    _df["CNN:ID"] = _results["cnn"]["ID"]
    _df["CNN:HW"] = _results["cnn"]["HW"]
    
    # customizing runtime configuration stored
    # in matplotlib.rcParams
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    
    # violin plot
    _catplot = sns.catplot(
        data=_df, kind='swarm',
        alpha=0.5, linewidth=1, height=1, aspect=0.7, s=1,
    )
    # for ax in _catplot.fig.axes:
    #     ax.set_yscale('log')
    
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
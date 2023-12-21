import subprocess
import sys
import pathlib
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


_REPORTED = {
    "ASCADf": {
        "MLP:HW": 480,
        "MLP:ID": 104,
        "CNN:HW": 744,
        "CNN:ID": 87,
    },
    "ASCADr": {
        "MLP:HW": 328,
        "MLP:ID": 129,
        "CNN:HW": 538,
        "CNN:ID": 78,
    },
    "CHESCTF": {
        "MLP:HW": 27,
        "MLP:ID": 1905,
        "CNN:HW": 462,
        "CNN:ID": ">3000",
    },
}

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
    

def test_runs(_exp_type: str, _mode: str, ):
    
    # PdfPages is a wrapper around pdf
    # file so there is no clash and create
    # files with no error.
    _pdf_file = pathlib.Path(f"_results/opoi_{_exp_type}_{_mode}.pdf")
    _pdf_file.unlink(missing_ok=True)
    
    with PdfPages(_pdf_file) as _pdf:
        for _ds in [
            "ASCADf", "ASCADr", "CHESCTF"
        ]:
            # plt.rcParams['text.usetex'] = True
            _fig = test_runs_for_dataset(_dataset=_ds, _exp_type=_exp_type, _mode=_mode)
            _pdf.savefig(figure=_fig, dpi=300)
            _fig.clear()
            
            # We can also set the file's metadata via the PdfPages object:
            # d = _pdf.infodict()
            # d['Title'] = 'Multipage PDF Example'
            # d['Author'] = 'Jouni K. Sepp\xe4nen'
            # d['Subject'] = 'How to create a multipage pdf file and set its metadata'
            # d['Keywords'] = 'PdfPages multipage keywords author title subject'
    
    subprocess.run(["xdg-open", _pdf_file.absolute().resolve().as_posix()])
    

def test_runs_for_dataset(_dataset: str, _exp_type: str, _mode: str, ) -> plt.Figure:
    _reported = _REPORTED[_dataset]
    _results = {
        "MLP:ID": {"nt_attack": [], "failed": 0, "total": 0},
        "MLP:HW": {"nt_attack": [], "failed": 0, "total": 0},
        "CNN:ID": {"nt_attack": [], "failed": 0, "total": 0},
        "CNN:HW": {"nt_attack": [], "failed": 0, "total": 0},
    }
    for _npz in pathlib.Path(f"_results/{_dataset}/opoi/{_exp_type}/{_mode}").glob("*"):
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
    _df["MLP:HW"] = _results["MLP:HW"]["nt_attack"]
    _df["MLP:ID"] = _results["MLP:ID"]["nt_attack"]
    _df["CNN:HW"] = _results["CNN:HW"]["nt_attack"]
    _df["CNN:ID"] = _results["CNN:ID"]["nt_attack"]
    _df[_df >= 1000] = np.inf
    
    # customizing runtime configuration stored
    # in matplotlib.rcParams
    # plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    
    # violin plot
    _catplot = sns.swarmplot(
        data=_df,
        alpha=0.5, s=3,
    )
    _catplot.set(title=_dataset)
    _fontsize = 8
    _offset = _fontsize * 4
    _annotation_y = 1000
    _catplot.set(ylim=(0, _annotation_y + 6*_offset))
    # for ax in _catplot.fig.axes:
    #     ax.set_yscale('log')
    
    for _k in _results.keys():
        _failed_percent = (_results[_k]["failed"] / _results[_k]["total"]) * 100
        _nt_attack = _results[_k]["nt_attack"]
        _failed = _failed_percent > 0
        _color = "red" if _failed else "blue"
        _median = int(np.median(_nt_attack))
        if _median >= 3000:
            _median = ">3000"
        _min = min(_nt_attack)
        if _min >= 3000:
            _min = ">3000"
        for _i, _msg in enumerate([
            f"[reported: {_reported[_k]}]",
            f"min: {_min}",
            f"median: {_median}",
            f"max: {'>3000' if _failed else max(_nt_attack)}",
            f"failed: {_failed_percent:.2f}%",
        ]):
            _catplot.text(
                _k, _annotation_y + (_i+1)*_offset, _msg,
                fontsize=_fontsize,  # Size
                fontstyle="oblique",  # Style
                color=_color,  # Color
                ha="center",  # Horizontal alignment
                va="center",  # Vertical alignment
            )
    
    return _catplot.get_figure()


def main():

    _mode = sys.argv[1]
    
    if _mode == "print_best_hp":
        print_best_hp(_path=sys.argv[2])
    elif _mode in [
        "best_model_runs",
    ]:
        test_runs(_exp_type=sys.argv[2], _mode=_mode, )
    else:
        raise Exception(f"Unsupported {_mode=}")
    
    

if __name__ == "__main__":
    
    main()
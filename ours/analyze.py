import subprocess
import sys
import pathlib
import numpy as np
import typing as t

from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


_REPORTED = {
    "OPOI": {
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
    },
    "NOPOI": {
        "ASCADf": {
            "MLP:HW": 7,
            "MLP:ID": 1,
            "CNN:HW": 7,
            "CNN:ID": 1,
        },
        "ASCADr": {
            "MLP:HW": 6,
            "MLP:ID": 1,
            "CNN:HW": 7,
            "CNN:ID": 1,
        },
        "CHESCTF": {
            "MLP:HW": 8,
            "MLP:ID": 13,
            "CNN:HW": 238,
            "CNN:ID": ">3000",
        },
    },
}


class ResultStruct(t.NamedTuple):
    experiment_id: int
    ntge_zero: int
    train_loss: t.List[float]
    val_loss: t.List[float]
    train_acc: t.List[float]
    val_acc: t.List[float]
    best_epoch: int = None
    

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
    
    # plt.rcParams['text.usetex'] = True
    
    with PdfPages(_pdf_file) as _pdf:
        for _ds in [
            "ASCADf", "ASCADr", "CHESCTF"
        ]:
            # for rank
            _fig = test_runs_for_dataset_rank(_dataset=_ds, _exp_type=_exp_type, _mode=_mode)
            _pdf.savefig(figure=_fig, dpi=300)
            _fig.clear()
            
            # loop over each model type
            for _model_type in [
                "MLP:HW", "MLP:ID", "CNN:HW", "CNN:ID",
            ]:
                # for acc
                _fig = test_runs_for_dataset_acc_nd_loss(_dataset=_ds, _exp_type=_exp_type, _mode=_mode, _model_type=_model_type)
                _pdf.savefig(figure=_fig, dpi=300)
                _fig.clear()
            
            # We can also set the file's metadata via the PdfPages object:
            # d = _pdf.infodict()
            # d['Title'] = 'Multipage PDF Example'
            # d['Author'] = 'Jouni K. Sepp\xe4nen'
            # d['Subject'] = 'How to create a multipage pdf file and set its metadata'
            # d['Keywords'] = 'PdfPages multipage keywords author title subject'
    
    subprocess.run(["xdg-open", _pdf_file.absolute().resolve().as_posix()])
    

def test_runs_for_dataset_acc_nd_loss(_dataset: str, _exp_type: str, _mode: str, _model_type: str) -> plt.Figure:
    
    _results = {
        "nt_attack": [],
        "train_loss": [],
        "val_loss": [],
        "train_acc": [],
        "val_acc": [],
        "failed": 0,
        "total": 0,
    }
    if _exp_type == "es":
        _results["best_epoch"] = []

    for _npz in pathlib.Path(f"_results/{_dataset}/opoi/{_exp_type}/{_mode}").glob("*"):
        if not _npz.name.endswith(".npz"):
            continue
        _tokens = _npz.name.split("_")
        if _model_type != f"{_tokens[0].upper()}:{_tokens[1]}":
            continue
        _data = np.load(_npz, allow_pickle=True)["npz_dict"][()]
        _results["nt_attack"].append(_data["nt_attack"])
        _results["train_loss"].append(_data["loss"])
        _results["val_loss"].append(_data["val_loss"])
        _results["train_acc"].append(_data["accuracy"])
        _results["val_acc"].append(_data["val_accuracy"])
        if _data["nt_attack"] >= 3000:
            _results["failed"] += 1
        _results["total"] += 1
        if _exp_type == "es":
            _results["best_epoch"].append(_data["best_epoch"])
    
    # compute median and get the index of experiment
    if len(_results["nt_attack"]) % 2 == 0:
        # keeps the array with odd length so that the median is one of the results
        _median = np.median(_results["nt_attack"][:-1])
    else:
        _median = np.median(_results["nt_attack"])
    _median_index = np.where(np.asarray(_results["nt_attack"]) == int(_median))[0][0]
    
    # Create a figure with two subplots
    _fig, _axs = plt.subplots(nrows=1, ncols=2, figsize=(15, 6))
    
    # Plot the first set of time series on the first subplot
    for _i, _data in enumerate(_results["train_loss"]):
        if _i == _median_index:
            sns.lineplot(data=_data, ax=_axs[0], color='green', linewidth=1.5, alpha=1.0)
        else:
            sns.lineplot(data=_data, ax=_axs[0], color='green', linewidth=0.5, alpha=0.1)
    for _i, _data in enumerate(_results["val_loss"]):
        if _i == _median_index:
            sns.lineplot(data=_data, ax=_axs[0], color='blue', linewidth=1.5, alpha=1.0)
        else:
            sns.lineplot(data=_data, ax=_axs[0], color='blue', linewidth=0.5, alpha=0.1)
    _axs[0].set_title('Loss')
    _axs[0].set_xlabel('epoch')
    _axs[0].set_ylabel('loss')
    
    # Plot the second set of time series on the second subplot
    for _i, _data in enumerate(_results["train_acc"]):
        if _i == _median_index:
            sns.lineplot(data=_data, ax=_axs[1], color='green', linewidth=1.5, alpha=1.0)
        else:
            sns.lineplot(data=_data, ax=_axs[1], color='green', linewidth=0.5, alpha=0.1)
    for _i, _data in enumerate(_results["val_acc"]):
        if _i == _median_index:
            sns.lineplot(data=_data, ax=_axs[1], color='blue', linewidth=1.5, alpha=1.0)
        else:
            sns.lineplot(data=_data, ax=_axs[1], color='blue', linewidth=0.5, alpha=0.1)
    _axs[1].set_title('Accuracy')
    _axs[1].set_xlabel('epoch')
    _axs[1].set_ylabel('accuracy')
    
    # Overall title for the figure
    _failed_percent = (_results["failed"] / _results["total"]) * 100
    if _exp_type == "es":
        plt.suptitle(f"{_dataset} | {_model_type} | ES@{_results['best_epoch'][_median_index]} | (failed: {_failed_percent:.2f}%)")
    else:
        plt.suptitle(f"{_dataset} | {_model_type} | (failed: {_failed_percent:.2f}%)")
    
    # Adjust the layout
    plt.tight_layout(rect=(0., 0.03, 1., 0.95))
    
    # return
    return _fig
    

def test_runs_for_dataset_rank(_dataset: str, _exp_type: str, _mode: str, ) -> plt.Figure:
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
        _median = np.median(_nt_attack)
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


def violin_plot_for_rank(
    title: str,
    data: t.Dict[str, t.List[ResultStruct]],
    reported: t.Optional[t.Dict[str, int]],
    fail_when_above: int = 3000,
    display_until: int = 1000,
) -> plt.Figure:
    
    # make dataframe
    _df = pd.DataFrame()
    for _k, _v in data.items():
        _eids = [_.experiment_id for _ in data[_k]]
        print(title, _k, len(_eids))
        for _ in range(1, 101):
            if _ not in _eids:
                print("          ", _)
    for _k, _v in data.items():
        _df[_k] = [_.ntge_zero for _ in data[_k]]
    _df[_df >= display_until] = np.inf
    
    # customizing runtime configuration stored
    # in matplotlib.rcParams
    # plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    
    # violin plot
    _catplot = sns.swarmplot(
        data=_df,
        alpha=0.5, s=3,
    )
    _catplot.set(title=title)
    _fontsize = 8
    _offset = _fontsize * 4
    _annotation_y = 1000
    _catplot.set(ylim=(0, _annotation_y + 6 * _offset))
    # for ax in _catplot.fig.axes:
    #     ax.set_yscale('log')
    
    # loop for all plots
    for _k in data.keys():
        
        # get fail percentage
        _failed = 0
        _total = 0
        _ntge_zero_all = []
        for _ in data[_k]:
            _ntge_zero_all.append(_.ntge_zero)
            _total += 1
            if _.ntge_zero >= fail_when_above:
                _failed += 1
        _failed_percent = (_failed / _total) * 100
        
        # plot
        _color = "red" if _failed > 0 else "blue"
        _median = np.median(_ntge_zero_all)
        if _median >= fail_when_above:
            _median = f">{fail_when_above}"
        _min = min(_ntge_zero_all)
        if _min >= fail_when_above:
            _min = f">{fail_when_above}"
        _msgs = []
        if bool(reported):
            _msgs.append(f"[reported: {reported[_k]}]")
        _msgs += [
            f"min: {_min}",
            f"median: {_median}",
            f"max: {'>3000' if _failed else max(_ntge_zero_all)}",
            f"failed: {_failed_percent:.2f}%",
        ]
        for _i, _msg in enumerate(_msgs):
            _catplot.text(
                _k, _annotation_y + (_i + 1) * _offset, _msg,
                fontsize=_fontsize,  # Size
                fontstyle="oblique",  # Style
                color=_color,  # Color
                ha="center",  # Horizontal alignment
                va="center",  # Vertical alignment
            )
    
    # return
    return _catplot.get_figure()


def best_model_runs_report(
    dataset: str, feature_selection_type: str,
    fail_when_above: int = 3000, display_until: int = 1000,
):
    
    # validation
    if dataset not in ["ASCADf", "ASCADr", "CHESCTF"]:
        raise ValueError(f"Unrecognized value {dataset=}")
    if feature_selection_type not in ["OPOI", "NOPOI"]:
        raise ValueError(f"Unrecognized value {feature_selection_type=}")
    
    # fetch results from disk
    _results = {}
    for _exp_type in ["orig", "es"]:
        _results[_exp_type] = dict()  # type: t.Dict[str, t.List[ResultStruct]]
        for _npz in pathlib.Path(f"_results/{dataset}/{feature_selection_type}/{_exp_type}/best_model_runs").glob("*"):
            if not _npz.name.endswith(".npz"):
                continue
            _tokens = _npz.name.split("_")
            _model_type = f"{_tokens[0].upper()}:{_tokens[1]}"
            if _model_type not in _results[_exp_type].keys():
                _results[_exp_type][_model_type] = []
            _data = np.load(_npz, allow_pickle=True)["npz_dict"][()]
            _results[_exp_type][_model_type].append(
                ResultStruct(
                    experiment_id=int(_npz.name.split("_")[-1].split(".")[0]),
                    ntge_zero=_data["nt_attack"],
                    train_loss=_data["loss"],
                    val_loss=_data["val_loss"],
                    train_acc=_data["accuracy"],
                    val_acc=_data["val_accuracy"],
                    best_epoch=_data["best_epoch"] if _exp_type == "es" else None,
                )
            )
    
    # ...
    # PdfPages is a wrapper around pdf
    # file so there is no clash and create
    # files with no error.
    _pdf_file = pathlib.Path(__file__).parent / "analyze" / "best_model_runs" / f"{dataset}_{feature_selection_type}.pdf"
    _pdf_file.parent.mkdir(parents=True, exist_ok=True)
    _pdf_file.unlink(missing_ok=True)
    
    # plt.rcParams['text.usetex'] = True
    
    with PdfPages(_pdf_file) as _pdf:
        
        for _exp_type in ["orig", "es"]:
            
            _fig = violin_plot_for_rank(
                title=f"{dataset} | {feature_selection_type} ({_exp_type})",
                reported=_REPORTED[feature_selection_type][dataset],
                data=_results[_exp_type], fail_when_above=fail_when_above, display_until=display_until,
            )
            _pdf.savefig(figure=_fig, dpi=300)
            _fig.clear()
        
        


def main():

    _mode = sys.argv[1]
    
    if _mode == "print_best_hp":
        print_best_hp(_path=sys.argv[2])
    elif _mode in [
        "best_model_runs",
    ]:
        _dataset = sys.argv[2]
        _feature_selection_type = sys.argv[3]
        best_model_runs_report(_dataset, _feature_selection_type)
    else:
        raise Exception(f"Unsupported {_mode=}")
    
    

if __name__ == "__main__":
    
    main()
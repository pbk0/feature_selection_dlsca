import tensorflow as tf

tf.config.threading.set_intra_op_parallelism_threads(2)
tf.config.threading.set_inter_op_parallelism_threads(1)

import os
import sys
import time
import glob
import numpy as np

# sys.path.append('/project_root_folder')
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.parent.resolve().as_posix())

os.environ["OMP_NUM_THREADS"] = '2'  # export OMP_NUM_THREADS=4
os.environ["OPENBLAS_NUM_THREADS"] = '2'  # export OPENBLAS_NUM_THREADS=4
os.environ["MKL_NUM_THREADS"] = '2'  # export MKL_NUM_THREADS=6

import importlib

from src.datasets.ReadASCADr import ReadASCADr
from src.datasets.dataset_parameters import *
from src.sca_metrics.sca_metrics import sca_metrics
from src.callback import EarlyStopping
from experiments.paths import *


def dataset_name(fs_type, num_poi, resampling_window=20):
    dataset_name = {
        "RPOI": f"ascad-variable_{num_poi}poi.h5",
        "OPOI": "ascad-variable.h5",
        "NOPOI": f"ascad-variable_nopoi_window_{resampling_window}.h5",
        "NOPOI_DESYNC": f"ascad-variable_nopoi_window_{resampling_window}_desync.h5"
    }

    return dataset_name[fs_type]


if __name__ == "__main__":
    leakage_model = sys.argv[1]
    model_name = sys.argv[2]
    feature_selection_type = sys.argv[3]
    experiment_type = sys.argv[4]
    run_id = int(sys.argv[5])
    
    if feature_selection_type == "OPOI":
        npoi = 1400
        window = 0
    elif feature_selection_type == "NOPOI":
        npoi = 25000
        window = 20
    else:
        raise Exception(f"Unsupported feature selection type {feature_selection_type}")

    if feature_selection_type == "RPOI":
        dataset_folder = dataset_folder_ascadr_rpoi
        save_folder = results_folder_ascadr_rpoi
    elif feature_selection_type == "OPOI":
        dataset_folder = dataset_folder_ascadr_opoi
        save_folder = results_folder_ascadr_opoi
    elif feature_selection_type == "NOPOI":
        dataset_folder = dataset_folder_ascadr_nopoi
        save_folder = results_folder_ascadr_nopoi
    elif feature_selection_type == "NOPOI_DESYNC":
        dataset_folder = dataset_folder_ascadr_nopoi_desync
        save_folder = results_folder_ascadr_nopoi_desync
    else:
        dataset_folder = None
        save_folder = None
        print("ERROR: Feature selection type not found.")
        exit()
        
    _save_path = pathlib.Path(f"{save_folder}/{experiment_type}/best_model_runs/{model_name}_{leakage_model}_{run_id}.npz")
    _save_path.parent.mkdir(parents=True, exist_ok=True)

    filename = f"{dataset_folder}/{dataset_name(feature_selection_type, npoi, resampling_window=window)}"

    """ Parameters for the analysis """
    classes = 9 if leakage_model == "HW" else 256
    first_sample = 0
    target_byte = 2
    epochs = 100
    ascadr_parameters = ascadr
    n_profiling = ascadr_parameters["n_profiling"]
    n_attack = ascadr_parameters["n_attack"]
    n_validation = ascadr_parameters["n_validation"]
    n_attack_ge = ascadr_parameters["n_attack_ge"]
    n_validation_ge = ascadr_parameters["n_validation_ge"]

    """ Create dataset for ASCADf """
    ascad_dataset = ReadASCADr(
        n_profiling,
        n_attack,
        n_validation,
        file_path=f"{filename}",
        target_byte=target_byte,
        leakage_model=leakage_model,
        first_sample=first_sample,
        number_of_samples=npoi,
        reshape_to_cnn=False if model_name == "mlp" else True,
    )

    """ Create random model """
    module_name = importlib.import_module(f"experiments.ASCADr.{feature_selection_type}.best_models")
    model_class = getattr(module_name, f"best_{model_name}_{leakage_model.lower()}_{feature_selection_type.lower()}_{npoi}_ascadr")
    model, batch_size = model_class(classes, npoi)
    
    """ Add callback based on experiment type """
    if experiment_type == "orig":
        _callbacks = []
    elif experiment_type == "es":
        _es_callback = EarlyStopping(
            monitor='val_loss',
            min_delta=0.,
            start_from_epoch=0,
            patience=200,
            verbose=1,
            restore_best_weights=True,
        )
        _callbacks = [_es_callback]
    else:
        raise Exception(f"Unknown experiment type {experiment_type}")

    """ Train model """
    history = model.fit(
        x=ascad_dataset.x_profiling,
        y=ascad_dataset.y_profiling,
        batch_size=batch_size,
        verbose=2,
        epochs=100,
        shuffle=True,
        validation_data=(ascad_dataset.x_validation, ascad_dataset.y_validation),
        callbacks=_callbacks)

    """ Get DL metrics """
    accuracy = history.history["accuracy"]
    val_accuracy = history.history["val_accuracy"]
    loss = history.history["loss"]
    val_loss = history.history["val_loss"]

    """ Compute GE, SR and NT for validation set """
    ge_validation, sr_validation, nt_validation = sca_metrics(
        model, ascad_dataset.x_validation, n_validation_ge, ascad_dataset.labels_key_hypothesis_validation, ascad_dataset.correct_key)

    print(f"GE validation: {ge_validation[n_validation_ge - 1]}")
    print(f"SR validation: {sr_validation[n_validation_ge - 1]}")
    print(f"Number of traces to reach GE = 1: {nt_validation}")

    """ Compute GE, SR and NT for attack set """
    ge_attack, sr_attack, nt_attack = sca_metrics(
        model, ascad_dataset.x_attack, n_attack_ge, ascad_dataset.labels_key_hypothesis_attack, ascad_dataset.correct_key)

    print(f"GE attack: {ge_attack[n_attack_ge - 1]}")
    print(f"SR attack: {sr_attack[n_attack_ge - 1]}")
    print(f"Number of traces to reach GE = 1: {nt_attack}")

    """ Create dictionary with results """
    npz_dict = {"npoi": npoi, "target_byte": target_byte, "n_profiling": n_profiling, "n_attack": n_attack,
                "n_validation": n_validation, "n_attack_ge": n_attack_ge, "n_validation_ge": n_validation_ge,
                "ge_validation": ge_validation, "sr_validation": sr_validation, "nt_validation": nt_validation, "ge_attack": ge_attack,
                "sr_attack": sr_attack, "nt_attack": nt_attack, "accuracy": accuracy, "val_accuracy": val_accuracy, "loss": loss,
                "val_loss": val_loss, "params": model.count_params()}
    if experiment_type == "es":
        # noinspection PyUnboundLocalVariable
        npz_dict["best_epoch"] = _es_callback.best_epoch

    """ Save npz file with results """
    np.savez(_save_path, npz_dict=npz_dict)

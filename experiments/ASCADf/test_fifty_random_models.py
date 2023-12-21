import tensorflow as tf

tf.config.threading.set_intra_op_parallelism_threads(2)
tf.config.threading.set_inter_op_parallelism_threads(1)

import pathlib
import os
import sys
import time
import glob
import numpy as np

# put root project folder path here:
sys.path.append(pathlib.Path(__file__).parent.parent.parent.resolve().as_posix())

os.environ["OMP_NUM_THREADS"] = '2'  # export OMP_NUM_THREADS=4
os.environ["OPENBLAS_NUM_THREADS"] = '2'  # export OPENBLAS_NUM_THREADS=4
os.environ["MKL_NUM_THREADS"] = '2'  # export MKL_NUM_THREADS=6

import importlib

from src.random_models.random_mlp import *
from src.random_models.random_cnn import *
from src.datasets.ReadASCADf import ReadASCADf
from src.datasets.dataset_parameters import *
from src.sca_metrics.sca_metrics import sca_metrics
from experiments.paths import *


def dataset_name(fs_type, num_poi, resampling_window=10):
    dataset_name = {
        "RPOI": f"ASCAD_{num_poi}poi.h5",
        "OPOI": "ASCAD.h5",
        "NOPOI": f"ASCAD_nopoi_window_{resampling_window}.h5",
        "NOPOI_DESYNC": f"ASCAD_nopoi_window_{resampling_window}_desync.h5"
    }

    return dataset_name[fs_type]


if __name__ == "__main__":
    leakage_model = sys.argv[1]
    model_name = sys.argv[2]
    feature_selection_type = sys.argv[3]
    npoi = int(sys.argv[4])
    window = int(sys.argv[5])
    run_id = int(sys.argv[6])
    random_model_seed = int(sys.argv[7])

    if feature_selection_type == "RPOI":
        dataset_folder = dataset_folder_ascadf_rpoi
        save_folder = results_folder_ascadf_rpoi
    elif feature_selection_type == "OPOI":
        dataset_folder = dataset_folder_ascadf_opoi
        save_folder = results_folder_ascadf_opoi
    elif feature_selection_type == "NOPOI":
        dataset_folder = dataset_folder_ascadf_nopoi
        save_folder = results_folder_ascadf_nopoi
    elif feature_selection_type == "NOPOI_DESYNC":
        dataset_folder = dataset_folder_ascadf_nopoi_desync
        save_folder = results_folder_ascadf_nopoi_desync
    else:
        dataset_folder = None
        save_folder = None
        print("ERROR: Feature selection type not found.")
        exit()

    filename = f"{dataset_folder}/{dataset_name(feature_selection_type, npoi, resampling_window=window)}"

    """ Parameters for the analysis """
    classes = 9 if leakage_model == "HW" else 256
    first_sample = 0
    target_byte = 2
    epochs = 100
    ascadf_parameters = ascadf
    n_profiling = ascadf_parameters["n_profiling"]
    n_attack = ascadf_parameters["n_attack"]
    n_validation = ascadf_parameters["n_validation"]
    n_attack_ge = ascadf_parameters["n_attack_ge"]
    n_validation_ge = ascadf_parameters["n_validation_ge"]

    """ Create dataset for ASCADf """
    ascad_dataset = ReadASCADf(
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
    if model_name == "mlp":
        model, seed, hp = mlp_random(classes, npoi, regularization=False, search_id=random_model_seed)
    else:
        model, seed, hp = cnn_random(classes, npoi, regularization=False, search_id=random_model_seed)

    hp["epochs"] = epochs

    """ Train model """
    history = model.fit(
        x=ascad_dataset.x_profiling,
        y=ascad_dataset.y_profiling,
        batch_size=hp["batch_size"],
        verbose=2,
        epochs=hp["epochs"],
        shuffle=True,
        validation_data=(ascad_dataset.x_validation, ascad_dataset.y_validation),
        callbacks=[])

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

    """ Save npz file with results """
    np.savez(f"{save_folder}/orig/test_50_random_models/{model_name}_{leakage_model}_{npoi}_{run_id}_{random_model_seed}.npz", npz_dict=npz_dict)

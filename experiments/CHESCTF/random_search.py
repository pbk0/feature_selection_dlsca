import tensorflow as tf

tf.config.threading.set_intra_op_parallelism_threads(2)
tf.config.threading.set_inter_op_parallelism_threads(1)

import os

os.environ["OMP_NUM_THREADS"] = '2'  # export OMP_NUM_THREADS=4
os.environ["OPENBLAS_NUM_THREADS"] = '2'  # export OPENBLAS_NUM_THREADS=4
os.environ["MKL_NUM_THREADS"] = '2'  # export MKL_NUM_THREADS=6

import sys
import time
import glob
# sys.path.append('/project_root_folder')
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.parent.resolve().as_posix())

from src.random_models.random_mlp import mlp_random
from src.random_models.random_cnn import cnn_random
from src.datasets.ReadCHESCTF import ReadCHESCTF
from src.datasets.dataset_parameters import chesctf
from src.sca_metrics.sca_metrics import sca_metrics
import numpy as np
from experiments.paths import *


def dataset_name(fs_type, resampling_window):
    dataset_name = {
        "OPOI": "ches_ctf_opoi.h5",
        "NOPOI": f"ches_ctf_nopoi_window_{resampling_window}.h5",
        "NOPOI_DESYNC": f"ches_ctf_nopoi_window_{resampling_window}_desync.h5"

    }

    return dataset_name[fs_type]

if __name__ == "__main__":

    leakage_model = sys.argv[1]
    model_name = sys.argv[2]
    feature_selection_type = sys.argv[3]
    npoi = int(sys.argv[4])
    regularization = True if sys.argv[5] == "True" else False
    window = int(sys.argv[6])
    search_id = int(sys.argv[7])

    if feature_selection_type == "OPOI":
        dataset_folder = dataset_folder_chesctf_opoi
        save_folder = results_folder_chesctf_opoi
    elif feature_selection_type == "NOPOI":
        dataset_folder = dataset_folder_chesctf_nopoi
        save_folder = results_folder_chesctf_nopoi
    elif feature_selection_type == "NOPOI_DESYNC":
        dataset_folder = dataset_folder_chesctf_nopoi_desync
        save_folder = results_folder_chesctf_nopoi_desync
    else:
        dataset_folder = None
        save_folder = None
        print("ERROR: Feature selection type not found.")
        exit()

    filename = f"{dataset_folder}/{dataset_name(feature_selection_type, resampling_window=window)}"

    """ Parameters for the analysis """
    classes = 9 if leakage_model == "HW" else 256
    first_sample = 0
    target_byte = 2
    epochs = 100
    chesctf_parameters = chesctf
    n_profiling = chesctf_parameters["n_profiling"]
    n_attack = chesctf_parameters["n_attack"]
    n_validation = chesctf_parameters["n_validation"]
    n_attack_ge = chesctf_parameters["n_attack_ge"]
    n_validation_ge = chesctf_parameters["n_validation_ge"]

    """ Create dataset for CHES CTF """
    chesctf_dataset = ReadCHESCTF(
        n_profiling,
        n_attack,
        n_validation,
        file_path=filename,
        target_byte=target_byte,
        leakage_model=leakage_model,
        first_sample=first_sample,
        number_of_samples=npoi,
        reshape_to_cnn=False if model_name == "mlp" else True,
    )

    """ Start search """
    start_time = time.time()

    """ Create random model """
    if model_name == "mlp":
        model, seed, hp = mlp_random(classes, npoi, regularization=regularization, search_id=search_id)
    else:
        model, seed, hp = cnn_random(classes, npoi, regularization=regularization, search_id=search_id)

    hp["epochs"] = epochs

    """ Train model """
    history = model.fit(
        x=chesctf_dataset.x_profiling,
        y=chesctf_dataset.y_profiling,
        batch_size=hp["batch_size"],
        verbose=2,
        epochs=hp["epochs"],
        shuffle=True,
        validation_data=(chesctf_dataset.x_validation, chesctf_dataset.y_validation),
        callbacks=[])

    """ Get DL metrics """
    accuracy = history.history["accuracy"]
    val_accuracy = history.history["val_accuracy"]
    loss = history.history["loss"]
    val_loss = history.history["val_loss"]

    """ Compute GE, SR and NT for validation set """
    ge_validation, sr_validation, nt_validation = sca_metrics(
        model, chesctf_dataset.x_validation, n_validation_ge, chesctf_dataset.labels_key_hypothesis_validation,
        chesctf_dataset.correct_key)

    print(f"GE validation: {ge_validation[n_validation_ge - 1]}")
    print(f"SR validation: {sr_validation[n_validation_ge - 1]}")
    print(f"Number of traces to reach GE = 1: {nt_validation}")

    """ Compute GE, SR and NT for attack set """
    ge_attack, sr_attack, nt_attack = sca_metrics(
        model, chesctf_dataset.x_attack, n_attack_ge, chesctf_dataset.labels_key_hypothesis_attack, chesctf_dataset.correct_key)

    print(f"GE attack: {ge_attack[n_attack_ge - 1]}")
    print(f"SR attack: {sr_attack[n_attack_ge - 1]}")
    print(f"Number of traces to reach GE = 1: {nt_attack}")

    total_time = time.time() - start_time

    """ Create dictionary with results """
    npz_dict = {"npoi": npoi, "target_byte": target_byte, "n_profiling": n_profiling, "n_attack": n_attack,
                "n_validation": n_validation, "n_attack_ge": n_attack_ge, "n_validation_ge": n_validation_ge, "hp": hp,
                "ge_validation": ge_validation, "sr_validation": sr_validation, "nt_validation": nt_validation, "ge_attack": ge_attack,
                "sr_attack": sr_attack, "nt_attack": nt_attack, "accuracy": accuracy, "val_accuracy": val_accuracy, "loss": loss,
                "val_loss": val_loss, "elapsed_time": total_time, "seed": seed, "params": model.count_params()}

    """ Save npz file with results """
    np.savez(f"{save_folder}/orig/random_search/{model_name}_{leakage_model}_{npoi}_{search_id}.npz", npz_dict=npz_dict)

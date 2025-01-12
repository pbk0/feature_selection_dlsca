import tensorflow as tf
from tensorflow.keras.optimizers import *
from tensorflow.keras.layers import *
from tensorflow.keras.models import *
from tensorflow.keras.utils import *
from tensorflow.keras.callbacks import *
import numpy as np
import h5py
from scipy.stats import entropy
import sys
from scipy.stats import multivariate_normal
from sklearn.preprocessing import StandardScaler
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
import itertools
import os

# sys.path.append('/project_root_folder')
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.parent.resolve().as_posix())

AES_Sbox = np.array([
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
])


def template_training(X, Y, pool=False):
    num_clusters = max(Y) + 1
    classes = np.unique(Y)
    # assign traces to clusters based on lables
    HW_catagory_for_traces = [[] for _ in range(num_clusters)]
    for i in range(len(X)):
        HW = Y[i]
        HW_catagory_for_traces[HW].append(X[i])
    HW_catagory_for_traces = [np.array(HW_catagory_for_traces[HW]) for HW in range(num_clusters)]

    # calculate Covariance Matrices
    # step 1: calculate mean matrix of POIs
    meanMatrix = np.zeros((num_clusters, len(X[0])))
    for i in range(num_clusters):
        meanMatrix[i] = np.mean(HW_catagory_for_traces[i], axis=0)
    # step 2: calculate covariance matrix
    covMatrix = np.zeros((num_clusters, len(X[0]), len(X[0])))
    for HW in range(num_clusters):
        for i in range(len(X[0])):
            for j in range(len(X[0])):
                x = HW_catagory_for_traces[HW][:, i]
                y = HW_catagory_for_traces[HW][:, j]
                covMatrix[HW, i, j] = np.cov(x, y)[0][1]
    if pool:
        covMatrix[:] = np.mean(covMatrix, axis=0)
    return meanMatrix, covMatrix, classes


# Calculate index of the most possible cluster for each traces
def template_attacking(meanMatrix, covMatrix, X_attack, classes):
    # launch attacks
    number_traces = X_attack.shape[0]
    prediction = np.zeros((number_traces))
    for i in range(number_traces):
        if (i % 2000 == 0):
            print(str(i) + '/' + str(number_traces))
        proba = np.zeros(classes.shape[0])
        for j, cl in enumerate(classes):
            rv = multivariate_normal(meanMatrix[j], covMatrix[j])
            proba[j] = rv.pdf(X_attack[i])
        sorted_index = np.argsort(proba)
        # Store the index of the most possible cluster
        prediction[i] = classes[sorted_index[-1]]

    return prediction


# Calculate probability of the most possible cluster for each traces
def template_attacking_proba(meanMatrix, covMatrix, X_test, classes, labels):
    labels = np.array(labels, dtype=np.uint8)
    p_k = np.ones(num_classes, dtype=np.float64)
    for k in range(num_classes):
        p_k[k] = np.count_nonzero(labels == k)
    p_k /= len(labels)

    number_traces = X_test.shape[0]
    proba = np.zeros((number_traces, classes.shape[0]))
    rv_array = []
    m = 1e-6
    for idx in range(len(classes)):
        rv_array.append(multivariate_normal(meanMatrix[idx], covMatrix[idx], allow_singular=True))

    for i in range(number_traces):
        if (i % 2000 == 0):
            print(str(i) + '/' + str(number_traces))
        proba[i] = [o.pdf(X_test[i]) for o in rv_array]
        proba[i] = np.multiply(proba[i], p_k) / np.sum(np.multiply(proba[i], p_k))

    return proba


def guessing_entropy(model, labels_guess, good_key):
    nt = len(model)

    key_rank_executions = 100
    key_rank_attack_traces = 3000
    key_rank_report_interval = 1

    key_ranking_sum = np.zeros(key_rank_attack_traces)

    output_probabilities = np.log(model + 1e-40)

    probabilities_kg_all_traces = np.zeros((nt, 256))
    for index in range(nt):
        probabilities_kg_all_traces[index] = output_probabilities[index][
            np.asarray([int(leakage[index]) for leakage in labels_guess[:]])
        ]

    for run in range(key_rank_executions):
        r = np.random.choice(range(nt), key_rank_attack_traces, replace=False)
        probabilities_kg_all_traces_shuffled = probabilities_kg_all_traces[r]
        key_probabilities = np.zeros(256)

        kr_count = 0
        for index in range(key_rank_attack_traces):

            key_probabilities += probabilities_kg_all_traces_shuffled[index]
            key_probabilities_sorted = np.argsort(key_probabilities)[::-1]

            if (index + 1) % key_rank_report_interval == 0:
                key_ranking_good_key = list(key_probabilities_sorted).index(good_key) + 1
                key_ranking_sum[kr_count] += key_ranking_good_key
                kr_count += 1

    guessing_entropy = key_ranking_sum / key_rank_executions

    result_number_of_traces_val = key_rank_attack_traces
    if guessing_entropy[key_rank_attack_traces - 1] < 2:
        for index in range(key_rank_attack_traces - 1, -1, -1):
            if guessing_entropy[index] > 2:
                result_number_of_traces_val = (index + 1) * key_rank_report_interval
                break

    print("GE = {}".format(guessing_entropy[key_rank_attack_traces - 1]))
    print("Number of traces to reach GE = 1: {}".format(result_number_of_traces_val))

    return guessing_entropy, result_number_of_traces_val


def aes_labelize(plaintexts, keys, byte, lm):
    if np.array(keys).ndim == 1:
        """ repeat key if argument keys is a single key candidate (for GE and SR computations)"""
        keys = np.full([len(plaintexts), 16], keys)

    plaintext = [row[byte] for row in plaintexts]
    key = [row[byte] for row in keys]
    state = [int(p) ^ int(k) for p, k in zip(plaintext, key)]
    intermediates = AES_Sbox[state]

    return [bin(iv).count("1") for iv in intermediates] if lm == "HW" else intermediates


def aes_labelize_mask(plaintexts, keys, masks, byte, mask_byte, lm):
    if np.array(keys).ndim == 1:
        """ repeat key if argument keys is a single key candidate (for GE and SR computations)"""
        keys = np.full([len(plaintexts), 16], keys)

    plaintext = [row[byte] for row in plaintexts]
    key = [row[byte] for row in keys]
    mask = [row[mask_byte] for row in masks]
    state = [AES_Sbox[int(p) ^ int(k)] ^ int(m) for p, k, m in zip(plaintext, key, mask)]
    intermediates = state

    return [bin(iv).count("1") for iv in intermediates] if lm == "HW" else intermediates


def create_labels_key_guess(plaintexts, round_key, byte, lm):
    labels_key_hypothesis = np.zeros((256, len(plaintexts)), dtype='int64')
    for key_byte_hypothesis in range(256):
        key_h = bytearray.fromhex(round_key)
        key_h[byte] = key_byte_hypothesis
        labels_key_hypothesis[key_byte_hypothesis] = aes_labelize(plaintexts, key_h, byte, lm)
    return labels_key_hypothesis


def load_dataset(dataset_file, n_profiling, n_attack):
    in_file = h5py.File(dataset_file, "r")

    profiling_samples = np.array(in_file['Profiling_traces/traces'], dtype=np.float32)[:n_profiling]
    attack_samples = np.array(in_file['Attack_traces/traces'], dtype=np.float32)[:n_attack]
    profiling_key = in_file['Profiling_traces/metadata']['key'][:n_profiling]
    attack_key = in_file['Attack_traces/metadata']['key'][:n_attack]
    profiling_plaintext = in_file['Profiling_traces/metadata']['plaintext'][:n_profiling]
    attack_plaintext = in_file['Attack_traces/metadata']['plaintext'][:n_attack]
    profiling_masks = in_file['Profiling_traces/metadata']['masks'][:n_profiling]
    attack_masks = in_file['Attack_traces/metadata']['masks'][:n_attack]

    return (profiling_samples, attack_samples), (profiling_key, attack_key), (profiling_plaintext, attack_plaintext), (
        profiling_masks, attack_masks)


def perceived_information(model, labels, num_classes):
    labels = np.array(labels, dtype=np.uint8)
    p_k = np.ones(num_classes, dtype=np.float64)
    for k in range(num_classes):
        p_k[k] = np.count_nonzero(labels == k)
    p_k /= len(labels)

    pi = entropy(p_k, base=2)  # we initialize the value with H(K)

    y_pred = np.array(model + 1e-36)

    for k in range(num_classes):
        y_pred_k = []
        for i, y in enumerate(y_pred):
            if labels[i] == k:
                y_pred_k.append(y[k])

        y_pred_k = np.array(y_pred_k)
        if len(y_pred_k) > 0:
            p_k_l = np.sum(np.log2(y_pred_k)) / len(y_pred_k)
            pi += p_k[k] * p_k_l

    print(f"PI: {pi}")

    return pi


def mlp(classes, number_of_samples, neurons, layers, activation):
    input_layer = Input(shape=(number_of_samples,))
    x = Dense(neurons, activation=activation)(input_layer)
    for l_i in range(layers - 1):
        x = Dense(neurons, activation=activation)(x)
    output_layer = Dense(classes, activation="softmax")(x)
    model = Model(input_layer, output_layer, name="mlp_model")
    model.summary()
    optimizer = Adam(learning_rate=0.001)
    model.compile(loss="categorical_crossentropy", optimizer=optimizer, metrics=["accuracy"])
    return model


def cnn(classes, number_of_samples, neurons, layers, activation, filters, kernel_size):
    input_layer = Input(shape=(number_of_samples, 1))

    x = Conv1D(filters, kernel_size, kernel_initializer='he_uniform', activation=activation, padding='same', name='block1_conv1')(
        input_layer)
    x = BatchNormalization()(x)
    x = AveragePooling1D(2, strides=2, name='block1_pool')(x)
    x = Flatten(name='flatten')(x)
    for l_i in range(layers):
        x = Dense(neurons, activation=activation, kernel_initializer='he_uniform')(x)
    output_layer = Dense(classes, activation="softmax")(x)
    model = Model(input_layer, output_layer, name="cnn_model")
    model.summary()
    optimizer = Adam(learning_rate=0.001)
    model.compile(loss="categorical_crossentropy", optimizer=optimizer, metrics=["accuracy"])
    return model


if __name__ == "__main__":

    leakage_model = sys.argv[1]
    snr_level = sys.argv[2]
    npoi = int(sys.argv[3])
    dataset_name = sys.argv[4]
    model_type = sys.argv[5]

    if model_type == "mlp":
        hp = {
            "epochs": [50, 100],
            "batch_size": [200, 400],
            "neurons": [20, 50, 100],
            "activation": ["selu", "relu"],
            "layers": [1, 2, 3],
            "learning_rate": [0.001],
            "optimizer": ["Adam"]
        }
    else:
        hp = {
            "epochs": [50, 100],
            "batch_size": [200, 400],
            "neurons": [50, 100],
            "activation": ["selu", "relu"],
            "layers": [1, 2],
            "learning_rate": [0.001],
            "optimizer": ["Adam"],
            "filters": [5, 10],
            "kernel_size": [2, 4]
        }

    PI_ta = 0
    GE_ta = 0
    NT_ta = 0

    if snr_level == "low_snr":
        folder_name = "ASCAD_rpoi_low_snr"
    elif snr_level == "medium_snr":
        folder_name = "ASCAD_rpoi_medium_snr"
    else:
        folder_name = "ASCAD_rpoi"
    folder_dataset = "ASCADf"

    keys, value = zip(*hp.items())
    search_hp_combinations = [dict(zip(keys, v)) for v in itertools.product(*value)]

    trace_folder = "/"
    mask_byte = 0
    target_byte = 2
    if leakage_model == "ID":
        dataset = {
            "filename": f"{trace_folder}{folder_dataset}/{folder_name}/{dataset_name}_{npoi}poi.h5",
            "round_key": "4DFBE0F27221FE10A78D4ADC8E490469",
            "first_sample": 0,
            "number_of_samples": npoi,
            "number_of_profiling_traces": 50000,
            "number_of_attack_traces": 10000
        }
    else:
        dataset = {
            "filename": f"{trace_folder}{folder_dataset}/{folder_name}/{dataset_name}_{npoi}poi_hw.h5",
            "round_key": "4DFBE0F27221FE10A78D4ADC8E490469",
            "first_sample": 0,
            "number_of_samples": npoi,
            "number_of_profiling_traces": 50000,
            "number_of_attack_traces": 10000
        }

    correct_key = bytearray.fromhex(dataset["round_key"])[target_byte]
    num_classes = 256 if leakage_model == "ID" else 9

    (x_profiling, x_attack), (profiling_key, attack_key), (profiling_plaintext, attack_plaintext), (
        profiling_masks, attack_masks) = load_dataset(dataset["filename"], dataset["number_of_profiling_traces"],
                                                      dataset["number_of_attack_traces"])

    scaler = StandardScaler()
    x_profiling = scaler.fit_transform(x_profiling)
    x_attack = scaler.transform(x_attack)

    nt_attack = dataset["number_of_attack_traces"]
    nt_attack_ge = 3000

    profiling_labels = aes_labelize(profiling_plaintext, profiling_key, target_byte, leakage_model)
    attack_labels = aes_labelize(attack_plaintext, attack_key, target_byte, leakage_model)

    profiling_labels_masks = aes_labelize_mask(profiling_plaintext, profiling_key, profiling_masks, target_byte, mask_byte,
                                               leakage_model)
    masks = [bin(int(iv)).count("1") for iv in profiling_masks[:, mask_byte]] if leakage_model == "HW" else profiling_masks[:, mask_byte]

    lda = LDA(n_components=5)
    x_profiling_m1 = lda.fit_transform(x_profiling, profiling_labels_masks)
    x_attack_m1 = lda.transform(x_attack)

    lda = LDA(n_components=5)
    x_profiling_m2 = lda.fit_transform(x_profiling, masks)
    x_attack_m2 = lda.transform(x_attack)

    x_profiling_concat = np.concatenate((x_profiling_m1, x_profiling_m2), axis=1)
    x_attack_concat = np.concatenate((x_attack_m1, x_attack_m2), axis=1)
    y_profiling = to_categorical(profiling_labels, num_classes=num_classes)
    y_attack = to_categorical(attack_labels, num_classes=num_classes)

    mean_v, cov_v, classes = template_training(x_profiling_concat, profiling_labels, pool=False)
    TA_prediction = template_attacking_proba(mean_v, cov_v, x_attack_concat[:nt_attack], classes, attack_labels[:nt_attack])

    labels_key_guess = create_labels_key_guess(attack_plaintext[:nt_attack], dataset["round_key"], target_byte, leakage_model)
    ge, nt = guessing_entropy(TA_prediction[:nt_attack], labels_key_guess, correct_key)
    GE_ta = ge[nt_attack_ge - 1]
    NT_ta = nt
    PI_ta = perceived_information(TA_prediction[:nt_attack], attack_labels[:nt_attack], num_classes)

    save_folder = f"{trace_folder}{folder_dataset}/{folder_name}/pi_ta_dnn"
    np.savez(f"{save_folder}/{dataset_name}_rpoi_{snr_level}_pi_{leakage_model}_{npoi}_TA.npz", PI=PI_ta, GE=GE_ta, NT=NT_ta)

    if model_type == "cnn":
        x_profiling_concat = x_profiling_concat.reshape(x_profiling_concat.shape[0], x_profiling_concat.shape[1], 1)
        x_attack_concat = x_attack_concat.reshape(x_attack_concat.shape[0], x_attack_concat.shape[1], 1)

    # check how many files already exists to start from where it stopped
    file_count = 0
    for i in range(len(search_hp_combinations)):
        filename = f"{save_folder}/{dataset_name}_rpoi_{snr_level}_pi_{leakage_model}_{npoi}_{model_type}_{i}.npz"
        if os.path.exists(filename):
            file_count += 1

    for hp_index, hp_values in enumerate(search_hp_combinations):

        if hp_index >= file_count:

            if model_type == "mlp":
                model = mlp(num_classes, x_profiling_concat.shape[1], hp_values["neurons"], hp_values["layers"], hp_values["activation"])
            else:
                model = cnn(num_classes, x_profiling_concat.shape[1], hp_values["neurons"], hp_values["layers"], hp_values["activation"],
                            hp_values["filters"], hp_values["kernel_size"])
            history = model.fit(
                x=x_profiling_concat,
                y=y_profiling,
                batch_size=hp_values["batch_size"],
                verbose=2,
                epochs=hp_values["epochs"],
                shuffle=True,
                validation_data=[x_attack_concat, y_attack])

            mlp_prediction = model.predict(x_attack_concat)

            GE, NT = guessing_entropy(mlp_prediction[:nt_attack], labels_key_guess, correct_key)
            PI = perceived_information(mlp_prediction[:nt_attack], attack_labels[:nt_attack], num_classes)

            np.savez(f"{save_folder}/{dataset_name}_rpoi_{snr_level}_pi_{leakage_model}_{npoi}_{model_type}_{hp_index}.npz",
                     PI=PI,
                     GE=GE,
                     NT=NT,
                     LOSS=history.history["val_loss"][hp_values["epochs"] - 1],
                     hp=hp_values)

import numpy as np
import h5py
from scalib.metrics import SNR
from numba import njit
from tqdm import tqdm
import sys

# put root project folder path here:
# sys.path.append('/project_root_folder')
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.parent.resolve().as_posix())
from experiments.paths import *

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


@njit
def winres(trace, window=20, overlap=0.5):
    trace_winres = []
    step = int(window * overlap)
    max = len(trace)
    for i in range(0, max, step):
        trace_winres.append(np.mean(trace[i:i + window]))
    return np.array(trace_winres, dtype=np.float32)


def generate_rpoi(gaussian_noise=None, leakage_model="ID"):
    n_profiling = 50000
    n_attack = 10000
    ns = 100000
    r_out_byte = 0
    target_byte = 2

    in_file = h5py.File(f'{raw_trace_folder_ascadf}ATMega8515_raw_traces.h5', "r")
    traces = in_file["traces"]
    metadata = in_file["metadata"]

    profiling_samples = traces[:n_profiling, :]
    attack_samples = traces[n_profiling:n_profiling + n_attack, :]

    if gaussian_noise is not None:
        noise_profiling = np.random.normal(0, gaussian_noise, size=np.shape(profiling_samples))
        noise_attack = np.random.normal(0, gaussian_noise, size=np.shape(attack_samples))

        profiling_samples = np.add(np.array(profiling_samples), noise_profiling)
        attack_samples = np.add(np.array(attack_samples), noise_attack)

    profiling_ciphertext = np.zeros((n_profiling, 16))
    attack_ciphertext = np.zeros((n_attack, 16))

    raw_plaintexts = metadata['plaintext']
    raw_keys = metadata['key']
    raw_masks = metadata['masks']

    profiling_plaintext = raw_plaintexts[:n_profiling]
    profiling_key = raw_keys[:n_profiling]
    profiling_masks = raw_masks[:n_profiling]

    attack_plaintext = raw_plaintexts[n_profiling:n_profiling + n_attack]
    attack_key = raw_keys[n_profiling:n_profiling + n_attack]
    attack_masks = raw_masks[n_profiling:n_profiling + n_attack]

    if leakage_model == "ID":
        s_box_masked = [[AES_Sbox[int(p) ^ int(k)] ^ int(r), r] for p, k, r in
                        zip(
                            np.asarray(profiling_plaintext[:, target_byte]),
                            np.asarray(profiling_key[:, target_byte]),
                            np.asarray(profiling_masks[:, r_out_byte]))
                        ]
    else:
        s_box_masked = [[bin(AES_Sbox[int(p) ^ int(k)] ^ int(r)).count("1"), bin(r).count("1")] for p, k, r in
                        zip(
                            np.asarray(profiling_plaintext[:, target_byte]),
                            np.asarray(profiling_key[:, target_byte]),
                            np.asarray(profiling_masks[:, r_out_byte]))
                        ]

    snr = SNR(np=2, ns=ns, nc=256 if leakage_model == "ID" else 9)
    snr.fit_u(np.array(profiling_samples, dtype=np.int16), x=np.array(s_box_masked, dtype=np.uint16))
    snr_val = snr.get_snr()

    """ log scale """
    poi_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

    for n_poi in poi_list:
        """ sort POIs from masked sbox output """
        ind_snr_masks_poi_sm = np.argsort(snr_val[0])[::-1][:int(n_poi / 2)]
        ind_snr_masks_poi_sm_sorted = np.sort(ind_snr_masks_poi_sm)

        """ sort POIs from mask share """
        ind_snr_masks_poi_r2 = np.argsort(snr_val[1])[::-1][:int(n_poi / 2)]
        ind_snr_masks_poi_r2_sorted = np.sort(ind_snr_masks_poi_r2)

        snr_masks_poi = np.concatenate((ind_snr_masks_poi_sm_sorted, ind_snr_masks_poi_r2_sorted), axis=0)
        snr_masks_poi = np.sort(snr_masks_poi)

        attack_samples_poi = attack_samples[:, snr_masks_poi]
        profiling_samples_poi = profiling_samples[:, snr_masks_poi]

        profiling_index = [n for n in range(n_profiling)]
        attack_index = [n for n in range(n_attack)]

        if leakage_model == "ID":
            out_file = h5py.File(f'{dataset_folder_ascadf_rpoi}/ASCAD_{n_poi}poi.h5', 'w')
        else:
            out_file = h5py.File(f'{dataset_folder_ascadf_rpoi}/ASCAD_{n_poi}poi_hw.h5', 'w')

        profiling_traces_group = out_file.create_group("Profiling_traces")
        attack_traces_group = out_file.create_group("Attack_traces")

        profiling_traces_group.create_dataset(name="traces", data=profiling_samples_poi, dtype=profiling_samples_poi.dtype)
        attack_traces_group.create_dataset(name="traces", data=attack_samples_poi, dtype=attack_samples_poi.dtype)

        metadata_type_profiling = np.dtype([("plaintext", profiling_plaintext.dtype, (len(profiling_plaintext[0]),)),
                                            ("ciphertext", profiling_ciphertext.dtype, (len(profiling_ciphertext[0]),)),
                                            ("key", profiling_key.dtype, (len(profiling_key[0]),)),
                                            ("masks", profiling_masks.dtype, (len(profiling_masks[0]),))
                                            ])
        metadata_type_attack = np.dtype([("plaintext", attack_plaintext.dtype, (len(attack_plaintext[0]),)),
                                         ("ciphertext", attack_ciphertext.dtype, (len(attack_ciphertext[0]),)),
                                         ("key", attack_key.dtype, (len(attack_key[0]),)),
                                         ("masks", attack_masks.dtype, (len(attack_masks[0]),))
                                         ])

        profiling_metadata = np.array([(profiling_plaintext[n], profiling_ciphertext[n], profiling_key[n], profiling_masks[n]) for n in
                                       profiling_index], dtype=metadata_type_profiling)
        profiling_traces_group.create_dataset("metadata", data=profiling_metadata, dtype=metadata_type_profiling)

        attack_metadata = np.array([(attack_plaintext[n], attack_ciphertext[n], attack_key[n], attack_masks[n]) for n in
                                    attack_index], dtype=metadata_type_attack)
        attack_traces_group.create_dataset("metadata", data=attack_metadata, dtype=metadata_type_attack)

        out_file.flush()
        out_file.close()


def generate_nopoi(window):
    n_profiling = 50000
    n_attack = 10000

    in_file = h5py.File(f'{raw_trace_folder_ascadf}/ATMega8515_raw_traces.h5', "r")
    traces = in_file["traces"]
    metadata = in_file["metadata"]

    ns = int(len(traces[0]) / window) * 2
    profiling_samples = np.zeros((len(traces), ns), dtype=np.float32)
    for trace_index in tqdm(range(n_profiling + n_attack)):
        profiling_samples[trace_index] = winres(traces[trace_index], window=window)

    attack_samples = profiling_samples[n_profiling:n_profiling + n_attack]
    profiling_samples = profiling_samples[0:n_profiling]

    raw_plaintexts = metadata['plaintext']
    raw_keys = metadata['key']
    raw_masks = metadata['masks']

    profiling_plaintext = raw_plaintexts[0:n_profiling]
    profiling_key = raw_keys[0:n_profiling]
    profiling_masks = raw_masks[0:n_profiling]

    attack_plaintext = raw_plaintexts[n_profiling:n_profiling + n_attack]
    attack_key = raw_keys[n_profiling:n_profiling + n_attack]
    attack_masks = raw_masks[n_profiling:n_profiling + n_attack]

    out_file = h5py.File(f'{dataset_folder_ascadf_nopoi}/ASCAD_nopoi_window_{window}.h5', 'w')

    profiling_index = [n for n in range(n_profiling)]
    attack_index = [n for n in range(n_attack)]

    profiling_traces_group = out_file.create_group("Profiling_traces")
    attack_traces_group = out_file.create_group("Attack_traces")

    profiling_traces_group.create_dataset(name="traces", data=profiling_samples, dtype=profiling_samples.dtype)
    attack_traces_group.create_dataset(name="traces", data=attack_samples, dtype=attack_samples.dtype)

    metadata_type_profiling = np.dtype([("plaintext", profiling_plaintext.dtype, (len(profiling_plaintext[0]),)),
                                        ("key", profiling_key.dtype, (len(profiling_key[0]),)),
                                        ("masks", profiling_masks.dtype, (len(profiling_masks[0]),))
                                        ])
    metadata_type_attack = np.dtype([("plaintext", attack_plaintext.dtype, (len(attack_plaintext[0]),)),
                                     ("key", attack_key.dtype, (len(attack_key[0]),)),
                                     ("masks", attack_masks.dtype, (len(attack_masks[0]),))
                                     ])

    profiling_metadata = np.array([(profiling_plaintext[n], profiling_key[n], profiling_masks[n]) for n in
                                   profiling_index], dtype=metadata_type_profiling)
    profiling_traces_group.create_dataset("metadata", data=profiling_metadata, dtype=metadata_type_profiling)

    attack_metadata = np.array([(attack_plaintext[n], attack_key[n], attack_masks[n]) for n in
                                attack_index], dtype=metadata_type_attack)
    attack_traces_group.create_dataset("metadata", data=attack_metadata, dtype=metadata_type_attack)

    out_file.flush()
    out_file.close()


if __name__ == "__main__":
    # # high snr
    # generate_rpoi(leakage_model="HW")
    # # medium snr
    # generate_rpoi(gaussian_noise=3, leakage_model="HW")
    # # low snr
    # generate_rpoi(gaussian_noise=10, leakage_model="HW")
    # # high snr
    # generate_rpoi(leakage_model="ID")
    # # medium snr
    # generate_rpoi(gaussian_noise=3, leakage_model="ID")
    # # low snr
    # generate_rpoi(gaussian_noise=10, leakage_model="ID")

    # generate_nopoi(window=10)
    generate_nopoi(window=20)
    # generate_nopoi(window=40)
    generate_nopoi(window=80)

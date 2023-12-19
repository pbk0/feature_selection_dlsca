# Paths to raw trace sets:
# For ASCADf dataset: ATMega8515_raw_traces.h5 (source: https://github.com/ANSSI-FR/ASCAD/tree/master/ATMEGA_AES_v1/ATM_AES_v1_fixed_key)
# For ASCADr dataset: atmega8515-raw-traces.h5 (source: https://github.com/ANSSI-FR/ASCAD/tree/master/ATMEGA_AES_v1/ATM_AES_v1_variable_key)
# For DPAV42 dataset: ... (source: https://www.dpacontest.org/v4/42_traces.php)
# For CHESCTF dataset: ... (source: https://zenodo.org/record/3733418#.Yc2iq1ko9Pa)
raw_trace_folder_ascadf = "_traces"
raw_trace_folder_ascadr = "_traces"
raw_trace_folder_dpav42 = "_traces"
raw_trace_folder_ascadv2 = "_traces"
raw_trace_folder_chesctf = "_traces"

# Folder location for each dataset and feature selection scenario
dataset_folder_ascadf_rpoi = "_datasets/ASCADf/ASCAD_rpoi"
dataset_folder_ascadf_opoi = "_datasets/ASCADf/ASCAD_opoi"
dataset_folder_ascadf_nopoi = "_datasets/ASCADf/ASCAD_nopoi"
dataset_folder_ascadf_nopoi_desync = "_datasets/ASCADf/ASCAD_nopoi_desync"

dataset_folder_ascadr_rpoi = "_datasets/ASCADr/ascad-variable_rpoi"
dataset_folder_ascadr_opoi = "_datasets/ASCADr/ascad-variable_opoi"
dataset_folder_ascadr_nopoi = "_datasets/ASCADr/ascad-variable_nopoi"
dataset_folder_ascadr_nopoi_desync = "_datasets/ASCADr/ascad-variable_nopoi_desync"

dataset_folder_dpav42_rpoi = "_datasets/DPAV42/dpav42_rpoi"
dataset_folder_dpav42_opoi = "_datasets/DPAV42/dpav42_opoi"
dataset_folder_dpav42_nopoi = "_datasets/DPAV42/dpav42_nopoi"
dataset_folder_dpav42_nopoi_desync = "_datasets/DPAV42/dpav42_nopoi_desync"

dataset_folder_ascadv2_opoi = "_datasets/ASCADV2/ascadv2_opoi"

dataset_folder_chesctf_opoi = "_datasets/CHESCTF/ches_ctf_opoi"
dataset_folder_chesctf_nopoi = "_datasets/CHESCTF/ches_ctf_nopoi"
dataset_folder_chesctf_nopoi_desync = "_datasets/CHESCTF/ches_ctf_nopoi_desync"

# Folder location to save results from grid and random search
results_folder_ascadf_rpoi = "_results/ASCADf/ASCAD_rpoi/"
results_folder_ascadf_opoi = "_results/ASCADf/ASCAD_opoi/"
results_folder_ascadf_nopoi = "_results/ASCADf/ASCAD_nopoi/"
results_folder_ascadf_nopoi_desync = "_results/ASCADf/ASCAD_nopoi_desync/"

results_folder_ascadr_rpoi = "_results/ASCADr/ascad-variable_rpoi"
results_folder_ascadr_opoi = "_results/ASCADr/ascad-variable_opoi"
results_folder_ascadr_nopoi = "_results/ASCADr/ascad-variable_nppoi"
results_folder_ascadr_nopoi_desync = "_results/ASCADr/ascad-variable_nopoi_desync"

results_folder_dpav42_rpoi = "_results/DPAV42/dpav42_rpoi"
results_folder_dpav42_opoi = "_results/DPAV42/dpav42_opoi"
results_folder_dpav42_nopoi = "_results/DPAV42/dpav42_nopoi"
results_folder_dpav42_nopoi_desync = "_results/DPAV42/dpav42_nopoi_desync"

results_folder_ascadv2_opoi = "_results/ASCADV2/ascadv2_opoi"

results_folder_chesctf_opoi = "_results/CHESCTF/chesctf_opoi"
results_folder_chesctf_nopoi = "_results/CHESCTF/chesctf_nopoi"
results_folder_chesctf_nopoi_desync = "_results/CHESCTF/chesctf_nopoi_desync"

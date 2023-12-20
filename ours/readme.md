

# Clone the fork

```bash
# dnd
git clone https://github.com/pbk0/feature_selection_dlsca
cd feature_selection_dlsca/
```

# Generate dataset

We are only interested in OPOI

Note to install `pip install trsfile==0.3.2`

First lets make two dirs

```pwsh
cd feature_selection_dlsca
mkdir _traces
mkdir _datasets
mkdir _results
```

## ASCADf

```pwsh
curl https://www.data.gouv.fr/s/resources/ascad/20180530-163000/ASCAD_data.zip --output _traces\ASCAD_data.zip
copy D:\dnd\Download\sca.ascad_v1_full\DnFk\file _traces\ASCAD_data.zip
Expand-Archive -Path _traces\ASCAD_data.zip -DestinationPath _traces
mkdir _datasets\ASCADf\ASCAD_opoi
copy _traces\ASCAD_data\ASCAD_databases\ASCAD.h5 _datasets\ASCADf\ASCAD_opoi
rm -r -fo _traces\ASCAD_data
```


## ASCADr

```pwsh
curl https://static.data.gouv.fr/resources/ascad-atmega-8515-variable-key/20190903-083349/ascad-variable.h5 --output _traces\ascad-variable.h5
copy D:\dnd\Download\sca.ascad_v1\DnVk_000\file _traces\ascad-variable.h5
mkdir _datasets\ASCADr\ascad-variable_opoi
copy _traces\ascad-variable.h5 _datasets\ASCADr\ascad-variable_opoi
```


## CHESCTF

```pwsh
cd _traces
curl https://zenodo.org/record/3733418/files/PinataAcqTask2.1_10k_upload.trs --output _traces\PinataAcqTask2.1_10k_upload.trs
curl https://zenodo.org/record/3733418/files/PinataAcqTask2.2_10k_upload.trs --output _traces\PinataAcqTask2.2_10k_upload.trs
curl https://zenodo.org/record/3733418/files/PinataAcqTask2.3_10k_upload.trs --output _traces\PinataAcqTask2.3_10k_upload.trs
curl https://zenodo.org/record/3733418/files/PinataAcqTask2.4_10k_upload.trs --output _traces\PinataAcqTask2.4_10k_upload.trs

copy E:\scandal\dnd\Download\sca.reassure_masked_aes\DnA\file _traces\PinataAcqTask2.1_10k_upload.trs
copy E:\scandal\dnd\Download\sca.reassure_masked_aes\DnB\file _traces\PinataAcqTask2.2_10k_upload.trs
copy E:\scandal\dnd\Download\sca.reassure_masked_aes\DnC_vk\file _traces\PinataAcqTask2.3_10k_upload.trs
copy E:\scandal\dnd\Download\sca.reassure_masked_aes\DnC_fk\file _traces\PinataAcqTask2.4_10k_upload.trs

mkdir _datasets/CHESCTF/ches_ctf_nopoi
mkdir _datasets/CHESCTF/ches_ctf_opoi
python experiments\CHESCTF\generate_dataset.py

rm -r -fo _datasets/CHESCTF/ches_ctf_nopoi
```


## ASCADV2

We use the traces from [here](https://zenodo.org/record/7885814). 
Provided by authors of paper "A Comparison of Multi-task learning and Single-task learning Approaches"
https://eprint.iacr.org/2023/611

```pwsh
cd _traces

curl https://zenodo.org/record/7885814/files/Ascad_v2_dataset_extracted.h5 --output _traces\Ascad_v2_dataset_extracted.h5

copy D:\dnd\Download\sca.ascad_v2_mo\Dn\file _traces\Ascad_v2_dataset_extracted.h5

mkdir _datasets\ASCADV2\ascadv2_opoi
python experiments\ASCADV2\generate_dataset.py
```

## ~~DPAV42~~

We do not include this dataset for our experiments as the dataset is comparatively easy similar to full version datasets where all samples are used ...

```pwsh
cd _traces
# download all the files from here https://cloud.telecom-paris.fr/s/JM2iaRZfwrNKtSp
for ($i = 0; $i -lt 16; $i++)
{
    $ix = $i.ToString('D2')
    "D:\dnd\Download\sca.dpa_v42\Dn\k${ix}p1 _traces\DPA_contestv4_2_k${ix}_part1.zip"
    copy "D:\dnd\Download\sca.dpa_v42\Dn\k${ix}p1" "_traces\DPA_contestv4_2_k${ix}_part1.zip"
    "D:\dnd\Download\sca.dpa_v42\Dn\k${ix}p2 _traces\DPA_contestv4_2_k${ix}_part2.zip"
    copy "D:\dnd\Download\sca.dpa_v42\Dn\k${ix}p2" "_traces\DPA_contestv4_2_k${ix}_part2.zip"
}
copy "D:\dnd\Download\sca.dpa_v42\Dn\index" "_traces\dpav4_2_index"

mkdir _datasets/DPAV42/dpav42_nopoi
mkdir _datasets/DPAV42/dpav42_opoi
python experiments\DPAV42\generate_dataset.py
```


# Experiments

## Calling best models over 100 times

We call the best models 100 times to get statistic for number of traces needed for attack ...

### ASCADf

```bash
mkdir -p _results/ASCADf/opoi/orig/test_best_models/
mkdir -p _results/ASCADr/opoi/orig/test_best_models/
mkdir -p _results/CHESCTF/opoi/orig/test_best_models/
for n in {1..100}; 
do
  for lk in ID HW;
  do 
    for nn in mlp cnn;
    do
      bsub -oo "_results/ASCADf/opoi/orig/test_best_models/${nn}_${lk}_700_${n}.log" python experiments/ASCADf/test_best_models.py ${lk} ${nn} OPOI 700 0 ${n}
      bsub -oo "_results/ASCADr/opoi/orig/test_best_models/${nn}_${lk}_700_${n}.log" python experiments/ASCADr/test_best_models.py ${lk} ${nn} OPOI 1400 0 ${n}
      bsub -oo "_results/CHESCTF/opoi/orig/test_best_models/${nn}_${lk}_700_${n}.log" python experiments/CHESCTF/test_best_models.py ${lk} ${nn} OPOI 4000 0 ${n}
    done
  done
done
python ours/results_analyze.py "_results/ASCADf/opoi/orig/test_best_models" pbhp
python ours/results_analyze.py "_results/ASCADr/opoi/orig/test_best_models" pbhp
python ours/results_analyze.py "_results/CHESCTF/opoi/orig/test_best_models" pbhp
```



## Search best model for ASCADv2

This is just an experiment to check if standard classifiers work with ASCADv2

```bash
mkdir -p _results/ASCADV2/opoi/random_search
for n in {1..500}; 
do
  for lk in ID HW;
  do 
    for nn in mlp cnn;
    do
      bsub -oo "_results/ASCADV2/opoi/orig/random_search/${nn}_${lk}_7181_${n}.log" python experiments/ASCADV2/random_search.py ${lk} ${nn} OPOI 7181 True 0 ${n}
    done
  done
done
python ours/results_analyze.py "_results/ASCADV2/opoi/orig/random_search"
```
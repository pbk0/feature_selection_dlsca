

# Clone the fork

```bash
# dnd
git clone https://github.com/pbk0/feature_selection_dlsca
cd feature_selection_dlsca/
```

# Generate dataset

We are only interested in OPOI

Note to install `pip install trsfile==0.3.2`


## First lets make the datasets

First lets make two dirs

```pwsh
mkdir C:\traces
mkdir C:\datasets
```

### ASCADf

```pwsh
cd C:\traces
curl https://www.data.gouv.fr/s/resources/ascad/20180530-163000/ASCAD_data.zip --output ASCAD_data.zip
copy D:\dnd\Download\sca.ascad_v1_full\DnFk\file ASCAD_data.zip
Expand-Archive -Path ASCAD_data.zip -DestinationPath .
copy C:\traces\ASCAD_data\ASCAD_databases\ASCAD.h5 C:\datasets\ASCADf\ASCAD_opoi
rm -r -fo ASCAD_data
```


### ASCADr

```pwsh
cd C:\traces
curl https://static.data.gouv.fr/resources/ascad-atmega-8515-variable-key/20190903-083349/ascad-variable.h5 --output ascad-variable.h5
copy D:\dnd\Download\sca.ascad_v1\DnVk_000\file ascad-variable.h5
copy E:scandal\\dnd\Download\sca.ascad_v1\DnVk_000\file ascad-variable.h5
mkdir C:\datasets\ASCADr\ascad-variable_opoi
copy ascad-variable.h5 C:\datasets\ASCADr\ascad-variable_opoi
```


### CHESCTF

```pwsh
cd C:\traces
curl https://zenodo.org/record/3733418/files/PinataAcqTask2.1_10k_upload.trs --output PinataAcqTask2.1_10k_upload.trs
curl https://zenodo.org/record/3733418/files/PinataAcqTask2.2_10k_upload.trs --output PinataAcqTask2.2_10k_upload.trs
curl https://zenodo.org/record/3733418/files/PinataAcqTask2.3_10k_upload.trs --output PinataAcqTask2.3_10k_upload.trs
curl https://zenodo.org/record/3733418/files/PinataAcqTask2.4_10k_upload.trs --output PinataAcqTask2.4_10k_upload.trs

copy D:\dnd\Download\sca.reassure_masked_aes\DnA\file PinataAcqTask2.1_10k_upload.trs
copy D:\dnd\Download\sca.reassure_masked_aes\DnB\file PinataAcqTask2.2_10k_upload.trs
copy D:\dnd\Download\sca.reassure_masked_aes\DnC_vk\file PinataAcqTask2.3_10k_upload.trs
copy D:\dnd\Download\sca.reassure_masked_aes\DnC_fk\file PinataAcqTask2.4_10k_upload.trs

mkdir C:/datasets/CHESCTF/ches_ctf_nopoi
mkdir C:/datasets/CHESCTF/ches_ctf_opoi
python C:\Github\RU\feature_selection_dlsca\experiments\CHESCTF\generate_dataset.py

rm -r -fo C:/datasets/CHESCTF/ches_ctf_nopoi
```


### ASCADV2

We use the traces from [here](https://zenodo.org/record/7885814). 
Provided by authors of paper "A Comparison of Multi-task learning and Single-task learning Approaches"
https://eprint.iacr.org/2023/611

```pwsh
cd C:\traces

curl https://zenodo.org/record/7885814/files/Ascad_v2_dataset_extracted.h5 --output Ascad_v2_dataset_extracted.h5

copy D:\dnd\Download\sca.ascad_v2_mo\Dn\file Ascad_v2_dataset_extracted.h5

mkdir C:/datasets/ASCADV2/ascadv2_opoi
python C:\Github\RU\feature_selection_dlsca\experiments\ASCADV2\generate_dataset.py
```

### ~~DPAV42~~

We ignore this dataset as it is not clear how to generate it.

Also the attack dataset is created of last two sets which has different keys while first 14 groups are used to generate profiling traces. This makes the attack dataset to not be fixed ...

Apart from that the results on this dataset for OPOI are already close to 1 and make it difficult to compare models ...

Also we do not have acces to chunked *.h5 files taht are used by `merge_dataset()` method provided in script `experiments\DPAV42\generate_dataset.py`

```pwsh
cd C:\traces
# download all the files from here https://cloud.telecom-paris.fr/s/JM2iaRZfwrNKtSp
for ($i = 0; $i -lt 16; $i++)
{
    $ix = $i.ToString('D2')
    "D:\dnd\Download\sca.dpa_v42\Dn\k${ix}p1 DPA_contestv4_2_k${ix}_part1.zip"
    copy "D:\dnd\Download\sca.dpa_v42\Dn\k${ix}p1" "DPA_contestv4_2_k${ix}_part1.zip"
    "D:\dnd\Download\sca.dpa_v42\Dn\k${ix}p2 DPA_contestv4_2_k${ix}_part2.zip"
    copy "D:\dnd\Download\sca.dpa_v42\Dn\k${ix}p2" "DPA_contestv4_2_k${ix}_part2.zip"
}
copy "D:\dnd\Download\sca.dpa_v42\Dn\index" "dpav4_2_index"

mkdir C:/datasets/DPAV42/dpav42_nopoi
mkdir C:/datasets/DPAV42/dpav42_opoi
python C:\Github\RU\feature_selection_dlsca\experiments\DPAV42\generate_dataset.py
```



# Calling best models

## ASCADf

```bash
python experiments/ASCADf/test_best_models.py HW mlp OPOI 700 2 0
python experiments/ASCADf/test_best_models.py ID mlp OPOI 700 2 0
python experiments/ASCADf/test_best_models.py HW cnn OPOI 700 2 0
python experiments/ASCADf/test_best_models.py ID cnn OPOI 700 2 0
```

## ASCADr

```bash
python experiments/ASCADr/test_best_models.py HW mlp OPOI 1400 2 0
python experiments/ASCADr/test_best_models.py ID mlp OPOI 1400 2 0
python experiments/ASCADr/test_best_models.py HW cnn OPOI 1400 2 0
python experiments/ASCADr/test_best_models.py ID cnn OPOI 1400 2 0
```

## CHESCTF

```bash
python experiments/CHESCTF/test_best_models.py HW mlp OPOI 4000 2 0
python experiments/CHESCTF/test_best_models.py ID mlp OPOI 4000 2 0
python experiments/CHESCTF/test_best_models.py HW cnn OPOI 4000 2 0
python experiments/CHESCTF/test_best_models.py ID cnn OPOI 4000 2 0
```



# Search best model for ASCADv2

```bash
mkdir C:/results/ASCADV2/ascadv2_opoi
python experiments/ASCADV2/random_search.py HW mlp OPOI 7181 True 0 0
python experiments/ASCADV2/random_search.py ID mlp OPOI 7181 True 0 0
python experiments/ASCADV2/random_search.py HW cnn OPOI 7181 True 0 0
python experiments/ASCADV2/random_search.py ID cnn OPOI 7181 True 0 0
```
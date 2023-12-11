

# clone fork

```bash
# dnd
git clone https://github.com/pbk0/feature_selection_dlsca
cd feature_selection_dlsca/
```

# generate dataset

We are only interested in OPOI

+ ASCADf: no need 
+ ASCADr: no need
+ CHESCTF: 
  + `python experiments/CHESCTF/generate_dataset.py`


# Calling models

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
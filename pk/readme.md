

# clone fork

```bash
# dnd
git clone https://github.com/pbk0/feature_selection_dlsca
cd feature_selection_dlsca/
```

# generate dataset

+ we are only interested in OPOI


## ASCADf


```bash
python .\experiments\ASCADf\generate_dataset.py
python experiments/ASCADf/test_best_models.py HW mlp OPOI 700 2 20
python experiments/ASCADf/test_best_models.py ID mlp OPOI 700 2 20
python experiments/ASCADf/test_best_models.py HW cnn OPOI 700 2 20
python experiments/ASCADf/test_best_models.py ID cnn OPOI 700 2 20
```
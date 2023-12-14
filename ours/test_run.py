import pathlib
import os
import sys
import subprocess


subprocess.run(
    ["python", "experiments/ASCADf/test_best_models.py", "ID", "cnn", "OPOI", "700", "2", "20"],
    shell=True,
)


if __name__ == '__main__':
    ...
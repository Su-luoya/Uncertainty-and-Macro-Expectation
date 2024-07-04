import sys
from pathlib import Path

sys.path.append(str(object=Path.cwd()))
from src.utils.imports import *


def quantile_25(x) -> float:
    return np.quantile(x, 0.25)


def quantile_75(x) -> float:
    return np.quantile(x, 0.75)


if __name__ == "__main__":
    ...

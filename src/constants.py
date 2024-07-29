import sys
from pathlib import Path

sys.path.append(str(Path.cwd()))
from src.utils.imports import *

SEED: int = 0
random.seed(a=SEED)
np.random.seed(seed=SEED)

WINDOW_SIZE: int = 80

VARIABLE: dict[str, dict[str, str]] = {
    "Real GDP": {
        "abbreviation": "RGDP",
        "frequency": "Q",
        "type": "level",
    },
    "Nominal GDP": {
        "abbreviation": "NGDP",
        "frequency": "Q",
        "type": "level",
    },
    "Price Index GDP": {
        "abbreviation": "PGDP",
        "frequency": "Q",
        "type": "level",
    },
    "Real Consumption": {
        "abbreviation": "RConsumption",
        "frequency": "Q",
        "type": "level",
    },
    "Real Nonresidential Investment": {
        "abbreviation": "RNRESIN",
        "frequency": "Q",
        "type": "level",
    },
    "Real Residential Investment": {
        "abbreviation": "RRESIN",
        "frequency": "Q",
        "type": "level",
    },
    "Real Federal Government Consumption": {
        "abbreviation": "RFEDGOV",
        "frequency": "Q",
        "type": "level",
    },
    "Real State and Local Government Consumption": {
        "abbreviation": "RSLGOV",
        "frequency": "Q",
        "type": "level",
    },
    "Industry Production Index": {
        "abbreviation": "IPT",
        "frequency": "M",
        "type": "level",
    },
    "Housing Start": {
        "abbreviation": "Housing",
        "frequency": "M",
        "type": "level",
    },
    # "CPI": {
    #     "abbreviation": "CPI",
    #     "frequency": "QM",
    #     "type": "???",
    # },
    "Unemployment Rate": {
        "abbreviation": "Unemployment",
        "frequency": "QM",
        "type": "rate",
    },
    "Three-month Treasury Rate": {
        "abbreviation": "TB3M",
        "frequency": "MN",
        "type": "rate",
    },
    "Ten-year Treasury Rate": {
        "abbreviation": "TB10Y",
        "frequency": "MN",
        "type": "rate",
    },
    "AAA Corporate Bond Rate": {
        "abbreviation": "AAA",
        "frequency": "MN",
        "type": "rate",
    },
}


if __name__ == "__main__":

    ...

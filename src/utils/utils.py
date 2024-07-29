import sys
from pathlib import Path

sys.path.append(str(object=Path.cwd()))
from src.utils.imports import *


def quantile_25(x) -> float:
    """Calculate the 25th percentile of the data."""
    return np.quantile(x, 0.25)


def quantile_75(x) -> float:
    """Calculate the 75th percentile of the data."""
    return np.quantile(x, 0.75)


def revision_coefficient(df: DataFrame, summary: bool = False) -> float:
    """Calculate the revision coefficient."""
    model = sm.OLS(endog=df["error"], exog=sm.add_constant(df["revision"])).fit()
    if summary:
        pp(model.summary())
    return model.params["revision"]


if __name__ == "__main__":
    ...

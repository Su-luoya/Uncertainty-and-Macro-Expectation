import sys
from pathlib import Path

sys.path.append(str(Path.cwd()))

from src.constants import *
from src.settings import ProjectPath
from src.utils.imports import *
from src.utils.utils import *


@dataclass
class SCL(object):
    column: str = "SCL"
    window_size: int = 80

    def __post_init__(self):
        self.df: DataFrame = pd.read_csv(
            filepath_or_buffer=f"{ProjectPath.uncertainty}/{self.column}.csv"
        )
        self.df["date"] = pd.to_datetime(self.df["date"])
        self.df["year"] = self.df["date"].dt.year
        self.df["quarter"] = self.df["date"].dt.quarter
        self.df = (
            self.df.drop(columns="date")
            .groupby(by=["year", "quarter"])
            .mean()
            .reset_index()
        )
        self.df["period"] = self.df[["year", "quarter"]].apply(
            lambda row: pd.Period(year=row.iloc[0], quarter=row.iloc[1], freq="Q"),
            axis=1,
        )
        self.df = self.df.drop(columns=["year", "quarter"]).set_index("period")
        # self.df = self.df.rolling(window=self.window_size).mean().dropna()
        # pp(self.df)
        # self.df["real_uncertainty(1)"].plot()
        # plt.show()


@dataclass
class TIV(object):
    column: str = "TIV"

    def __post_init__(self):
        self.df: DataFrame = pd.read_csv(
            filepath_or_buffer=f"{ProjectPath.uncertainty}/{self.column}.csv"
        )
        self.df["date"] = pd.to_datetime(self.df[["year", "month"]].assign(day=1))
        self.df["period"] = self.df["date"].dt.to_period("Q")
        self.df = (
            self.df.drop(columns=["year", "month", "date"]).groupby("period").mean()
        )


@dataclass
class EPU(object):
    column: str = "EPU"

    def __post_init__(self):
        self.df: DataFrame = pd.read_csv(
            filepath_or_buffer=f"{ProjectPath.uncertainty}/{self.column}.csv"
        )
        self.df["date"] = pd.to_datetime(self.df["date"])
        self.df["year"] = self.df["date"].dt.year
        self.df["quarter"] = self.df["date"].dt.quarter
        self.df = (
            self.df.drop(columns="date")
            .groupby(by=["year", "quarter"])
            .mean()
            .reset_index()
        )
        self.df["period"] = self.df[["year", "quarter"]].apply(
            lambda row: pd.Period(year=row.iloc[0], quarter=row.iloc[1], freq="Q"),
            axis=1,
        )
        self.df = self.df.drop(columns=["year", "quarter"]).set_index("period")
        self.df = self.df / 100
        # pp(self.df)


class Uncertainty(object):
    def __init__(self):
        self.scl = SCL()
        # self.tiv = TIV()
        self.epu = EPU()
        self.df = pd.merge(
            left=self.scl.df,
            right=self.epu.df,
            left_index=True,
            right_index=True,
            how="outer",
        )


if __name__ == "__main__":
    ...
    # scl = SCL()
    # pp(scl.df)
    # tiv = TIV()
    # pp(tiv.df)
    # epu = EPU()
    # pp(epu.df)

    uncertainty = Uncertainty()
    pp(uncertainty.df)

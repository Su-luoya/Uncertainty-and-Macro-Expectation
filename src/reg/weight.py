import sys
from pathlib import Path

from pandas.core.frame import DataFrame

sys.path.append(str(Path.cwd()))

from src.constants import *
from src.data.individual import IndividualGrowth, IndividualLevel
from src.data.real import (
    RealMonthly,
    RealMonthlyNormal,
    RealQuarterly,
    RealQuarterlyMonthly,
)
from src.data.uncertainty import SCL, Uncertainty
from src.reg.fire import Fire
from src.settings import ProjectPath
from src.utils.imports import *
from src.utils.utils import *


@dataclass
class WindowGenerator(object):
    df: DataFrame
    window_size: int = 80

    def __post_init__(self) -> None:
        self.period_list = self.df["period"].unique()
        self.start_period = self.period_list[0]
        self._end_period = self.period_list[-1]

    def __iter__(self):
        self._period = self.start_period
        return self

    def __next__(self):
        if self._period > self._end_period - self.window_size:
            raise StopIteration
        self._period += 1
        return Window(
            df=self.df[
                self.df["period"].isin(
                    pd.period_range(
                        start=self._period - 1,
                        periods=self.window_size,
                        freq="Q-DEC",
                    )
                )
            ]
        )


@dataclass
class Window(object):
    df: DataFrame

    def __post_init__(self) -> None: ...

    def __repr__(self) -> str:
        return f"Window from {self.df['period'].min()} to {self.df['period'].max()}"

    def get_individual(self) -> DataFrame:
        return self.df[["period", "id", "error", "revision"]].set_index(
            keys=["period", "id"]
        )

    def get_idiosyncratic(self) -> DataFrame:
        return (
            self.df[["period", "id", "error_idio", "revision_idio"]]
            .rename(columns={"error_idio": "error", "revision_idio": "revision"})
            .set_index(["period", "id"])
        )

    def get_consensus(self) -> DataFrame:
        return (
            self.df[["period", "error_mean", "revision_mean"]]
            .drop_duplicates(subset=["period", "error_mean", "revision_mean"])
            .rename(columns={"error_mean": "error", "revision_mean": "revision"})
            .set_index(["period"])
        )

    @property
    def beta(self) -> dict[str, float]:
        return {
            "period": self.df["period"].max(),
            "consensus": revision_coefficient(self.get_consensus()),
            "individual": revision_coefficient(self.get_individual()),
            "idiosyncratic": revision_coefficient(self.get_idiosyncratic()),
        }


@dataclass
class Beta:
    fire: Fire
    window_size: int = 80

    def __post_init__(self) -> None:
        self.df_beta: DataFrame = pd.DataFrame(
            [
                window.beta
                for window in WindowGenerator(
                    df=self.fire.df, window_size=self.window_size
                )
            ]
        ).set_index("period")
        self.df_beta["weight"] = (
            self.df_beta["individual"] - self.df_beta["consensus"]
        ) / (self.df_beta["idiosyncratic"] - self.df_beta["consensus"])
        self.df_beta = pd.merge(
            left=self.df_beta,
            right=Uncertainty().df,
            how="left",
            left_index=True,
            right_index=True,
        )
        self.df_beta["weight_change"] = self.df_beta["weight"].diff()
        self.df_beta["weight_change_rate"] = (
            self.df_beta["weight_change"] / self.df_beta["weight"].shift(1)
        ) * 100

    def save(self) -> None:
        self.df_beta.to_csv(
            path_or_buf=f"{ProjectPath.beta_reg}/{self.fire.name}.csv",
            index=True,
        )
        pp(f"{self.fire.column} beta data saved successfully!")


if __name__ == "__main__":
    # fire = Fire(column="Real Consumption", forecast_horizon=3)
    # beta = Beta(fire=fire)
    # beta.save()
    ...
    for variable, info in VARIABLE.items():
        fire = Fire(column=variable)
        beta = Beta(fire=fire)
        beta.save()
    # break

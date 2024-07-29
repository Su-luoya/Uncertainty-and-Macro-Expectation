import sys
from pathlib import Path

sys.path.append(str(Path.cwd()))

from src.constants import *
from src.data.individual import IndividualGrowth, IndividualLevel
from src.data.real import (
    RealMonthly,
    RealMonthlyNormal,
    RealQuarterly,
    RealQuarterlyMonthly,
)
from src.data.uncertainty import Uncertainty
from src.settings import ProjectPath
from src.utils.imports import *
from src.utils.utils import *


@dataclass
class FireAbstract(ABC):
    column: str
    forecast_horizon: int = 4  # from quarter t − 1 to quarter t + 3

    def __post_init__(self) -> None:
        # pp(self.column)
        self.name: str = VARIABLE[self.column]["abbreviation"]
        # Initialize
        self.individual_init()
        self.real_init()
        # Construct FIRE data
        self.df: DataFrame = self.construct_fire_data()
        # pp(self.df)
        # Consensus, individual and idiosyncratic level
        self.df: DataFrame = pd.merge(
            left=self.df[["period", "id", "error", "revision"]],
            right=self.df.groupby(["period"])[["error", "revision"]]
            .mean()
            .rename(columns={"error": "error_mean", "revision": "revision_mean"}),
            how="inner",
            left_on="period",
            right_index=True,
        )
        self.df["error_idio"] = self.df["error"] - self.df["error_mean"]
        self.df["revision_idio"] = self.df["revision"] - self.df["revision_mean"]
        # pp(self.df)

    @abstractmethod
    def individual_init(self) -> None:
        """Initialize the `individual` object

        >>> self.individual = IndividualGrowth(column=self.column)
        >>> self.individual = IndividualLevel(column=self.column)
        """

    def real_init(self) -> None:
        """Initialize the `real` object"""
        if VARIABLE[self.column]["frequency"] == "Q":
            self.real = RealQuarterly(
                column=self.column, forecast_horizon=self.forecast_horizon
            )
        elif VARIABLE[self.column]["frequency"] == "M":
            self.real = RealMonthly(column=self.column)
        elif VARIABLE[self.column]["frequency"] == "QM":
            self.real = RealQuarterlyMonthly(column=self.column)
        elif VARIABLE[self.column]["frequency"] == "MN":
            self.real = RealMonthlyNormal(column=self.column)
        else:
            raise ValueError("Invalid frequency!")

    @abstractmethod
    def construct_fire_data(self) -> DataFrame:
        """Construct the FIRE data"""

    def filter_id(self, df: DataFrame, minimize_counts: int = 10) -> DataFrame:
        """Filter `id` based on the counts of `id`."""
        id_counts: Series[int] = df["id"].value_counts()
        return df[df["id"].isin(values=id_counts[id_counts >= minimize_counts].index)]

    def save(self):
        # Consensus level data saving
        pd.merge(
            left=self.df[["period", "error_mean", "revision_mean"]]
            .drop_duplicates()
            .rename(columns={"error_mean": "error", "revision_mean": "revision"}),
            right=Uncertainty().df,
            left_on="period",
            right_index=True,
        ).to_csv(
            path_or_buf=f"{ProjectPath.consensus_reg}/{self.name}.csv",
            index=False,
        )
        # Individual (and idiosyncratic) level data saving
        pd.merge(
            left=self.df[
                ["period", "id", "error", "revision", "error_idio", "revision_idio"]
            ],
            right=Uncertainty().df,
            left_on="period",
            right_index=True,
        ).to_csv(
            path_or_buf=f"{ProjectPath.individual_reg}/{self.name}.csv",
            index=False,
        )
        pp(f"{self.column} data saved successfully!")


class FireGrowth(FireAbstract):

    def individual_init(self) -> None:
        self.individual = IndividualGrowth(
            column=self.column, forecast_horizon=self.forecast_horizon
        )

    def construct_fire_data(self) -> DataFrame:
        """Construct the FIRE data.

        nowcast:
            ```
            (F_t x_{t+3} / x_{t-1}) - 1
            ```
        forecast:
            ```
            (F_{t-1} x_{t+3}) / (F_{t-1} x_{t-1}) - 1
            ```
        revision: nowcast - forecast
            ```
            (F_t x_{t+3} / x_{t-1}) - ( (F_{t-1} x_{t+3}) / (F_{t-1} x_{t-1}) )
            ```
        actual_growth:
            ```
            (x_{t+3} / x_{t-1}) - 1
            ```
        """
        df_nowcast: DataFrame = pd.merge(
            left=self.individual.df_nowcast,  # F_t x_{t+3}
            right=self.real.get_last_level(),  # x_{t-1}
            left_on="period",
            right_index=True,
            how="inner",
        )
        # (F_t x_{t+3} / x_{t-1}) - 1
        df_nowcast["nowcast"] = (df_nowcast["nowcast"] / df_nowcast["last_level"]) - 1
        # FIRE
        df: DataFrame = pd.merge(
            left=pd.merge(
                left=df_nowcast,
                right=self.individual.df_forecast,  # (F_{t-1} x_{t+3}) / (F_{t-1} x_{t-1}) - 1 (index: t)
                on=["period", "id"],
                how="inner",
            ),
            right=self.real.get_actual_growth(),  # (x_{t+3}/x_{t-1} - 1)
            left_on="period",
            right_index=True,
            how="inner",
        )
        # (F_t x_{t+3} / x_{t-1}) - ( (F_{t-1} x_{t+3}) / (F_{t-1} x_{t-1}) )
        df["revision"] = df["nowcast"] - df["forecast"]
        # (x_{t+3} / x_{t-1}) - (F_t x_{t+3} / x_{t-1})
        df["error"] = df["actual_growth"] - df["nowcast"]
        # df["actual_growth_1"] = df.groupby(["id"])["actual_growth"].shift(1)
        # df["change"] = df["actual_growth"] - df["actual_growth_1"]
        # pp(df[df["id"] == 1])
        return self.filter_id(df=df)


class FireLevel(FireAbstract):

    def individual_init(self) -> None:
        self.individual = IndividualLevel(column=self.column)

    def construct_fire_data(self) -> DataFrame:
        df: DataFrame = pd.merge(
            left=self.individual.df_revision,
            right=self.real.get_actual_level(),
            left_on="period",
            right_index=True,
            how="inner",
        )
        df["error"] = df["actual_level"] - df["nowcast"]
        return self.filter_id(df=df)


@dataclass
class Fire:
    column: str
    forecast_horizon: int = 4

    def __post_init__(self) -> None:
        info: dict[str, str] = VARIABLE[self.column]
        self.name: str = info["abbreviation"]
        if info["type"] == "rate":
            self.fire: FireAbstract = FireLevel(self.column)
        elif info["type"] == "level":
            self.fire: FireAbstract = FireGrowth(
                column=self.column, forecast_horizon=self.forecast_horizon
            )
        else:
            raise ValueError("Invalid type!")
        self.df: DataFrame = self.fire.df
        self.save: Callable[[], None] = self.fire.save


if __name__ == "__main__":
    # fire = Fire(column="Real GDP", forecast_horizon=1)
    # pp(fire.df)
    # fire.save()
    for variable, info in VARIABLE.items():
        fire = Fire(column=variable)
        fire.save()
    # break

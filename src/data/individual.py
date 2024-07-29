import sys
from pathlib import Path

from pandas.core.frame import DataFrame

sys.path.append(str(Path.cwd()))

from src.constants import *
from src.settings import ProjectPath
from src.utils.imports import *
from src.utils.utils import *


@dataclass
class IndividualGrowth:
    column: str
    forecast_horizon: int = 4  # from quarter t − 1 to quarter t + 3

    def __post_init__(self) -> None:
        # Initialize the attributes
        self.column_name: str = VARIABLE[self.column]["abbreviation"]
        # Read the data
        self.df: DataFrame = pd.read_csv(
            filepath_or_buffer=f"{ProjectPath.survey}/{self.column}.csv"
        )
        # columns required
        if self.forecast_horizon > 1:
            self.columns: list[str] = [
                f"{self.column_name}(0)",
                f"{self.column_name}({self.forecast_horizon-1})",
                f"{self.column_name}({self.forecast_horizon})",
            ]
        elif self.forecast_horizon == 1:
            self.columns = [
                f"{self.column_name}(0)",
                f"{self.column_name}(1)",
            ]
        else:
            raise ValueError("forecast horizon must be in range 1~4")
        self.df = self.df[["period", "id"] + self.columns]
        # Convert the `period` to `Period` object
        self.df["period"] = self.df["period"].map(arg=pd.Period)
        # F_t x_{t+3} (index: t)
        self.df_nowcast: DataFrame = (
            self.df[["period", "id", f"{self.column_name}({self.forecast_horizon-1})"]]
            .rename(
                columns={f"{self.column_name}({self.forecast_horizon-1})": "nowcast"}
            )
            .dropna(subset="nowcast")
        )
        # (F_{t-1} x_{t+3}) / (F_{t-1} x_{t-1}) - 1 (index: t)
        self.df_forecast: DataFrame = (
            (
                self.df.set_index("period")
                .groupby("id")[
                    [
                        f"{self.column_name}(0)",
                        f"{self.column_name}({self.forecast_horizon})",
                    ]
                ]
                .apply(func=lambda df: self.__shift_func(df=df))
                .reset_index()
            )[["forecast_period", "id", "forecast"]]
            .rename(columns={"forecast_period": "period"})
            .dropna(subset="forecast")
        )

    def __shift_func(self, df: DataFrame) -> DataFrame:
        """Calculate the forecast for each individual series."""
        df["forecast_period"] = df.index + 1
        # pp(df)
        df["forecast"] = (
            df[f"{self.column_name}({self.forecast_horizon})"]
            / df[f"{self.column_name}(0)"]
            - 1
        )
        return df


@dataclass
class IndividualLevel:
    column: str

    def __post_init__(self) -> None:
        # Initialize the attributes
        self.column_name: str = VARIABLE[self.column]["abbreviation"]
        # Read the data
        self.df: DataFrame = pd.read_csv(
            filepath_or_buffer=f"{ProjectPath.survey}/{self.column}.csv"
        )
        # columns required
        self.columns: list[str] = [
            f"{self.column_name}(3)",
            f"{self.column_name}(4)",
        ]
        self.df = self.df[["period", "id"] + self.columns]
        self.df.columns = ["period", "id", "nowcast", "forecast"]
        # Convert the `period` to `Period` object
        self.df["period"] = self.df["period"].map(pd.Period)
        # Revision: F_t x_{t+3} - F_{t-1} x_{t+3} (index: t)
        self.df["forecast"] = self.df.groupby("id")["forecast"].shift(1)
        self.df["revision"] = self.df["nowcast"] - self.df["forecast"]
        self.df_revision: DataFrame = self.df[
            ["period", "id", "nowcast", "forecast", "revision"]
        ].dropna(subset=["nowcast", "forecast", "revision"])
        # pp(self.df[self.df["id"] == 1])
        # pp(self.df_revision[self.df_revision["id"] == 1])


@dataclass
class IndividualCPI:
    column: str

    def __post_init__(self):
        # Initialize the attributes
        self.column_name: str = VARIABLE[self.column]["abbreviation"]
        # Read the data
        self.df: DataFrame = pd.read_csv(
            filepath_or_buffer=f"{ProjectPath.survey}/{self.column}.csv"
        )
        pp(self.df)
        # todo: not implemented yet


if __name__ == "__main__":
    ...
    individual = IndividualGrowth("Real GDP", 1)
    # individual = IndividualLevel("AAA Corporate Bond Rate")
    pp(individual.df_forecast)
    pp(individual.df_nowcast)
    # individual = IndividualCPI("CPI")

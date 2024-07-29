import sys
from pathlib import Path

from pandas.core.frame import DataFrame

sys.path.append(str(Path.cwd()))


from src.constants import *
from src.settings import ProjectPath
from src.utils.imports import *
from src.utils.utils import *


@dataclass
class AbstractReal(ABC):
    column: str
    forecast_horizon: int = 4  # from quarter t − 1 to quarter t + 3

    def __post_init__(self) -> None:
        self.column_name: str = VARIABLE[self.column]["abbreviation"]
        self.df: DataFrame = (
            pd.read_csv(filepath_or_buffer=f"{ProjectPath.real}/{self.column}.csv")
            .set_index(keys="period")
            .fillna(value=np.nan)
            .astype(dtype=float)
        )
        self.df.index = self.df.index.map(mapper=pd.Period)
        self.df.columns = self.df.columns.map(mapper=pd.Period)
        self.other_init()

    def other_init(self) -> None:
        """Other initialization steps."""

    @abstractmethod
    def query(
        self,
        data_period: Period | str,
        kind: str = "level",
    ) -> float:
        """Query the data."""

    @abstractmethod
    def get_last_level(self) -> DataFrame:
        """
        x_{t-1}
        index: t
        release time: t
        """

    @abstractmethod
    def get_actual_growth(self) -> DataFrame:
        """
        (x_{t+3}/x_{t-1} - 1)
        index: t
        published time: t+4
        """

    @abstractmethod
    def get_actual_level(self) -> DataFrame:
        """
        x_{t+3}
        index: t
        published time: t+4
        """


class RealQuarterly(AbstractReal):

    def other_init(self) -> None:
        self.df_growth: DataFrame = (
            self.df / self.df.shift(periods=self.forecast_horizon)  # 4
        ) - 1
        # pp(self.df_growth)

    def query(
        self,
        data_period: Period | str,
        kind: str = "level",
    ) -> float:
        if kind == "level":
            return self.df.loc[data_period].loc[data_period + 1]  # type: ignore
        elif kind == "growth":
            return self.df_growth.loc[data_period].loc[data_period + 1]  # type: ignore
        else:
            raise ValueError("kind must be 'level' or 'growth'")

    def get_last_level(self) -> DataFrame:
        df = pd.DataFrame(index=sorted(list(set(self.df.index) & set(self.df.columns))))
        df["last_level"] = df.index.map(
            lambda x: self.query(
                data_period=x,
                kind="level",
            )
        )
        return df.shift(1).dropna()

    def get_actual_growth(self) -> DataFrame:
        df = pd.DataFrame(
            index=[pd.Period(i) - self.forecast_horizon for i in self.df_growth.columns]
        )
        df["actual_growth"] = df.index.map(
            mapper=lambda x: self.query(
                data_period=x + self.forecast_horizon - 1, kind="growth"
            )
        )
        return df.dropna()

    def get_actual_level(self) -> DataFrame:
        df = pd.DataFrame(
            index=[pd.Period(i) - self.forecast_horizon for i in self.df_growth.columns]
        )  # 4
        df["actual_level"] = df.index.map(
            mapper=lambda x: self.query(
                data_period=x + self.forecast_horizon - 1, kind="level"
            )  # 3
        )
        return df.dropna()


class RealMonthly(AbstractReal):

    def query(
        self,
        data_period: Period | str,
        kind: str = "level",
    ) -> float:
        last_month: Period["M"] = data_period.asfreq("M")  # type: ignore
        period_list: list[Period] = [last_month - i for i in range(3)]
        if kind == "level":
            return self.df.loc[period_list][last_month + 1].mean()  # type: ignore
        elif kind == "growth":
            return (self.df.loc[period_list][last_month + 1].mean()) / (  # type: ignore
                self.df.loc[[i - 12 for i in period_list]][last_month + 1].mean()  # type: ignore
            ) - 1
        elif kind == "next_level":
            return self.df.loc[period_list][last_month + 1].mean()  # type: ignore
        else:
            raise ValueError("kind must be 'level' or 'growth'")

    def get_last_level(self) -> DataFrame:
        df = pd.DataFrame(
            index=pd.period_range(
                start=self.df.columns[0].asfreq("Q"),  # type: ignore
                end=self.df.columns[-1].asfreq("Q") - 1,  # type: ignore
                freq="Q",
            ),
        )
        df["last_level"] = df.index.map(
            mapper=lambda x: self.query(
                data_period=x,
                kind="level",
            )
        )
        return df.shift(periods=1).dropna()

    def get_actual_growth(self) -> DataFrame:
        df = pd.DataFrame(
            index=pd.period_range(
                start=self.df.columns[0].asfreq("Q"),  # type: ignore
                end=self.df.columns[-1].asfreq("Q") - 4,  # type: ignore
                freq="Q",
            ),
        )
        df["actual_growth"] = df.index.map(
            mapper=lambda x: self.query(
                data_period=x + 3,
                kind="growth",
            )
        )
        return df.dropna()

    def get_actual_level(self) -> DataFrame:
        df = pd.DataFrame(
            index=pd.period_range(
                start=self.df.columns[0].asfreq("Q"),  # type: ignore
                end=self.df.columns[-1].asfreq("Q") - 4,  # type: ignore
                freq="Q",
            ),
        )
        df["actual_level"] = df.index.map(
            mapper=lambda x: self.query(
                data_period=x + 3,
                kind="level",
            )
        )
        return df.dropna()


class RealQuarterlyMonthly(AbstractReal):

    def other_init(self) -> None:
        self.start_quarter: Period = self.df.columns[0]  # type:ignore

    def query(self, data_period: Period, kind: str = "level"):
        last_month: Period["M"] = data_period.asfreq("M")  # type: ignore
        period_list: list[Period] = [last_month - i for i in range(3)]
        current_period: Period = (
            data_period + 1
            if data_period + 1 >= self.start_quarter
            else self.start_quarter
        )
        if kind == "level":
            return self.df.loc[period_list][current_period].mean()  # type: ignore
        elif kind == "growth":
            return (self.df.loc[period_list][current_period].mean()) / (  # type: ignore
                self.df.loc[[i - 12 for i in period_list]][current_period].mean()  # type: ignore
            ) - 1
        else:
            raise ValueError("kind must be 'level' or 'growth'")

    def get_last_level(self) -> DataFrame:
        df = pd.DataFrame(
            index=pd.period_range(
                start=self.df.index[0].asfreq("Q"),  # type: ignore
                end=self.df.index[-1].asfreq("Q") - 1,  # type: ignore
                freq="Q",
            ),
        )
        df["last_level"] = df.index.map(
            mapper=lambda x: self.query(
                data_period=x,
                kind="level",
            )
        )
        return df.shift(periods=1).dropna()

    def get_actual_growth(self) -> DataFrame:
        df = pd.DataFrame(
            index=pd.period_range(
                start=self.df.index[0].asfreq("Q") + 1,  # type: ignore
                end=self.df.index[-1].asfreq("Q") - 4,  # type: ignore
                freq="Q",
            ),
        )
        df["actual_growth"] = df.index.map(
            mapper=lambda x: self.query(
                data_period=x + 3,
                kind="growth",
            )
        )
        return df.dropna()

    def get_actual_level(self) -> DataFrame:
        df = pd.DataFrame(
            index=pd.period_range(
                start=self.df.index[0].asfreq("Q") + 1,  # type: ignore
                end=self.df.index[-1].asfreq("Q") - 4,  # type: ignore
                freq="Q",
            ),
        )
        df["actual_level"] = df.index.map(
            mapper=lambda x: self.query(
                data_period=x + 3,
                kind="level",
            )
        )
        return df.dropna()


@dataclass
class RealMonthlyNormal:
    column: str

    def __post_init__(self) -> None:
        self.column_name: str = VARIABLE[self.column]["abbreviation"]
        self.df = pd.read_csv(
            filepath_or_buffer=f"{ProjectPath.real}/{self.column}.csv"
        )  # .set_index(keys="period")
        self.df["date"] = pd.to_datetime(self.df["date"])
        self.df["year"] = self.df["date"].dt.year
        self.df["quarter"] = self.df["date"].dt.quarter

    def get_actual_level(self) -> DataFrame:
        """
        x_{t+3}
        index: t
        published time: t+4
        """
        df: DataFrame = (
            self.df.groupby(["year", "quarter"])[[self.column_name]]
            .mean()
            .rename(columns={self.column_name: "actual_level"})
            .reset_index()
        )
        return (
            df.set_index(
                df.apply(
                    lambda x: pd.Period(year=x["year"], quarter=x["quarter"], freq="Q"),
                    axis=1,
                )
            )
            .drop(columns=["year", "quarter"])
            .shift(periods=-3)
        ).dropna()

    def get_last_level(self) -> DataFrame:
        """
        x_{t-1}
        index: t
        release time: t
        """
        raise NotImplementedError

    def get_actual_growth(self) -> DataFrame:
        """
        (x_{t+3}/x_{t-1} - 1)
        index: t
        published time: t+4
        """
        raise NotImplementedError


if __name__ == "__main__":
    ...
    real = RealQuarterly("Real GDP", 1)
    # real = RealMonthly("Industry Production Index", "IPT")
    # real = RealMonthly("Housing Start")
    # real = RealQuarterlyMonthly("CPI")
    # real = RealQuarterlyMonthly("Unemployment Rate")
    # # pp(real)
    pp(real.get_last_level())
    pp(real.get_actual_growth())
    pp(real.get_actual_level())
    # real = RealMonthlyNormal("AAA Corporate Bond Rate")

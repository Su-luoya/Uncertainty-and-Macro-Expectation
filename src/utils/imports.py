import copy
import json
import os
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

# from itertools import combinations, combinations_with_replacement, permutations, product
from typing import (
    Any,
    Generic,
    Iterable,
    Literal,
    Optional,
    Sequence,
    TypedDict,
    TypeVar,
    Union,
)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

# from flatdict import FlatDict
# from numpy import float32, float64
# from numpy.typing import NDArray
from pandas import (
    DataFrame,
    DatetimeIndex,
    Index,
    Period,
    PeriodIndex,
    Series,
    Timestamp,
)
from pandas.arrays import PeriodArray
from rich import print as ic
from rich.panel import Panel
from rich.pretty import Pretty, pprint
from rich.progress import (
    BarColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

# from scipy import stats
# from scipy.linalg import toeplitz
# from scipy.optimize import minimize
# from scipy.stats import chi2, norm, t
# from sympy import Eq, Symbol, solve, symbols
from typing_extensions import NotRequired, Required, Self

# D = TypeVar("D")
# T = TypeVar("T", str, Timestamp)
StrOrTimestamp = Union[str, Timestamp]
Info = dict[str, Any]
Parameters = dict[str, float]


def pp(_object: Any) -> None:
    """Pretty print an object in a panel using the rich library"""
    ic(Panel(Pretty(_object, expand_all=True), expand=False, subtitle_align="center"))


def progress(iterable, description="Working"):
    """A generator that yields items from an iterable and updates a progress bar."""
    # Get the total number of items in the iterable
    total: int = len(iterable)
    # Create a progress bar
    with Progress(
        TextColumn(
            "[bold red][progress.description]{task.description}[/bold red]",
        ),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        BarColumn(bar_width=200),
        TextColumn("{task.completed}/{task.total}"),
        TextColumn("[time elapsed:"),
        TimeElapsedColumn(),
        TextColumn(", time remaining:"),
        TimeRemainingColumn(),
        TextColumn(","),
        TextColumn("{task.speed} it/s"),
        TextColumn("]"),
        transient=True,
        expand=True,
    ) as progress:
        # Add a task to the progress bar
        task_id: TaskID = progress.add_task(description, total=total)
        # Iterate over the items in the iterable
        for item in iterable:
            # Yield the item
            yield item
            # Update the progress bar
            progress.update(task_id, advance=1)
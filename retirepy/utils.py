import pandas as pd
import numpy as np
import datetime as dt
from .models import Frequency, FrequencyMeta


def compute_compound_interest(
    annual_interest_rate: float,
    compounding_frequency: Frequency,
) -> float:
    # annual_interest_rate / unit_t_per_year
    r = annual_interest_rate / compounding_frequency.meta.per_year
    # Number of times that interest is compounded per unit t
    # n = compounding_frequency.meta.per_month
    n = 1
    return (1 + r / n) ** (n * 1)


def compute_future_value_series(
    start_month: dt.date,
    end_month: dt.date,
    principal_investment: float,
    annual_interest_rate: float,
    compounding_frequency: Frequency,
    contribution_amount: float,
    contribution_frequency: Frequency,
    contribution_at_start_of_compound_period: bool = True,
) -> pd.Series:
    """Return Future Value for entire date range

    https://www.vertex42.com/Calculators/compound-interest-calculator.html#calculator
    """
    return_series = pd.Series(
        data=np.nan,
        index=pd.date_range(
            start=start_month,
            end=end_month,
            freq="MS",  # Month Start Frequency
        ),
    )
    return_series.iloc[0] = principal_investment

    compound_interest = compute_compound_interest(
        annual_interest_rate=annual_interest_rate,
        compounding_frequency=compounding_frequency,
    )

    current_value = np.nan
    for iloc, month in enumerate(return_series.index.month):
        if iloc == 0:
            current_value = principal_investment
            continue
        contribute = month in contribution_frequency.meta.trigger_months

        if contribute and contribution_at_start_of_compound_period:
            # Time to add a contribution
            current_value += contribution_amount

        # Compound Interest if needed
        if month in compounding_frequency.meta.trigger_months:
            # Time to compound
            current_value *= compound_interest

        if contribute and not contribution_at_start_of_compound_period:
            # Time to add a contribution
            current_value += contribution_amount

        return_series.iloc[iloc] = current_value

    return return_series

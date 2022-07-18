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
    num_months: int,
    principal_investment: float,
    annual_interest_rate: float,
    compounding_frequency: Frequency,
    contribution_amount: float,
    contribution_frequency: Frequency,
    contribution_at_start_of_compound_period: bool = True,
) -> np.ndarray:
    """Return Future Value for entire date range

    https://www.vertex42.com/Calculators/compound-interest-calculator.html#calculator
    """
    # Initialize Months
    month_range = np.arange(0, num_months)
    month_arr = (month_range % 12) + 1

    # Initialize FV array
    future_value_arr = np.zeros(num_months)
    future_value_arr[0] = principal_investment

    # Initialize Input Array
    deposits_arr = np.zeros(num_months)
    add_deposit_arr = np.isin(month_arr, contribution_frequency.meta.trigger_months)
    deposits_arr[add_deposit_arr] = contribution_amount

    compound_interest = compute_compound_interest(
        annual_interest_rate=annual_interest_rate,
        compounding_frequency=compounding_frequency,
    )

    current_value = principal_investment
    iter_arr = np.vstack((month_arr, deposits_arr)).T[1:]
    for iloc, (month, deposit) in enumerate(iter_arr):
        if contribution_at_start_of_compound_period:
            # Time to add a contribution
            current_value += deposit

        # Compound Interest if needed
        if month in compounding_frequency.meta.trigger_months:
            # Time to compound
            current_value *= compound_interest

        if not contribution_at_start_of_compound_period:
            # Time to add a contribution
            current_value += deposit

        future_value_arr[iloc + 1] = current_value

    return future_value_arr

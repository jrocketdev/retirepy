import pandas as pd
import numpy as np
import logging
from .models import CompoundingFrequency, ContributionFrequency

logger = logging.getLogger(__file__)


def compute_compound_interest(
    annual_interest_rate: float,
) -> float:
    """
    r = the interest rate (decimal)
    n = the number of times that interest is compounded per period (per month)
    t = the number of periods the money is invested for (months)

    :param annual_interest_rate:
    :param compounding_frequency:
    :return:
    """

    # annual_interest_rate / unit_t_per_year
    r = annual_interest_rate / 12
    # Number of times that interest is compounded per unit t
    n = 1
    return r / n


def compute_future_value_series(
    num_months: int,
    principal_investment: float,
    annual_interest_rate: float,
    compounding_frequency: CompoundingFrequency | str,
    contribution_amount: float,
    contribution_frequency: ContributionFrequency | str,
    contribution_at_start_of_compound_period: bool = True,
) -> np.ndarray:
    """Return Future Value for entire date range

    https://www.vertex42.com/Calculators/compound-interest-calculator.html#calculator
    """
    if isinstance(compounding_frequency, str):
        compounding_frequency = CompoundingFrequency(compounding_frequency)
    if isinstance(contribution_frequency, str):
        contribution_frequency = ContributionFrequency(contribution_frequency)

    num_months -= 1
    # Initialize Months
    month_range = np.arange(num_months + 1) - 1
    month_arr = (month_range % 12) + 1
    month_arr[0] = 0

    # Initialize FV array
    future_value_arr = np.zeros(num_months + 1)
    future_value_arr[0] = principal_investment

    # Initialize Input Array
    deposits_arr = np.zeros(num_months + 1)
    add_deposit_arr = np.isin(month_arr, contribution_frequency.meta.trigger_months)
    deposits_arr[add_deposit_arr] = contribution_amount

    # Initialize Interest Arr (for debugging purposes at this time)
    interest_arr = np.zeros(num_months + 1)
    accrued_interest_arr = np.zeros(num_months + 1)
    undeposited_interest = 0

    compound_interest = compute_compound_interest(
        annual_interest_rate=annual_interest_rate,
    )
    logger.debug(f"{compound_interest=}")

    current_value = principal_investment
    iter_arr = np.vstack((month_arr, deposits_arr)).T[1:]
    for i, (month, deposit) in enumerate(iter_arr):
        if contribution_at_start_of_compound_period:
            # Time to add a contribution
            current_value += deposit

        # Compound the interest
        current_interest = current_value * compound_interest
        interest_arr[i + 1] = current_interest
        undeposited_interest += current_interest
        accrued_interest_arr[i + 1] = accrued_interest_arr[i] + current_interest
        if month in compounding_frequency.meta.trigger_months:
            # Time to compound
            current_value += undeposited_interest
            undeposited_interest = 0

        if not contribution_at_start_of_compound_period:
            # Time to add a contribution
            current_value += deposit

        future_value_arr[i + 1] = current_value

    return future_value_arr

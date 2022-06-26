from enum import Enum
from typing import Optional
import datetime as dt
import pandas as pd
import numpy as np
from pydantic import BaseModel, validator, PrivateAttr


class FlowType(str, Enum):
    INCOME: str = "Income"
    EXPENSE: str = "Expense"


class FrequencyMeta(BaseModel):
    name: str
    per_year: int
    _trigger_months: list[int] = PrivateAttr()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._trigger_months = {
            12: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            4: [1, 4, 7, 10],
            2: [1, 7],
            1: [1]
        }[self.per_year]

    @validator('per_year')
    def ensure_per_year_in_allowed(cls, v):
        if v not in [1, 2, 4, 12]:
            raise ValueError('per_year can only be 1 (yearly), 2 (semi-annually), 4 (quarterly), 12 (monthly)')
        return v

    @property
    def per_month(self) -> float:
        return self.per_year / 12

    @property
    def months_between(self) -> int:
        return 12 // self.per_year

    @property
    def trigger_months(self) -> list[int]:
        return self._trigger_months


MONTHLY_META = FrequencyMeta(
    name='Monthly',
    per_year=12
)

YEARLY_META = FrequencyMeta(
    name='Yearly',
    per_year=1
)


class Frequency(str, Enum):
    MONTHLY: str = "Monthly"
    YEARLY: str = "Yearly"

    @property
    def meta(self) -> FrequencyMeta:
        return {"Monthly": MONTHLY_META, "Yearly": YEARLY_META}[self.value]


class AmountType(str, Enum):
    FLAT: str = "Flat"
    PERCENT_OF_INCOME: str = "Percent Of Income"


class MoneyFlow(BaseModel):
    name: str
    active: bool = True
    type: FlowType

    amount: float
    frequency: Frequency

    growth_rate: float = 0
    growth_frequency: Frequency = Frequency.YEARLY

    # TODO: Add validators to ensure these are starts of the month
    start_month: dt.date
    end_month: dt.date

    @validator("growth_frequency")
    def ensure_growth_frequency_isnt_more_frequent_than_flow_frequency(cls, v, values):
        # Make sure growth frequency isn't monthly if flow frequency is yearly. Makes no sense.
        if v.meta.per_year > values["frequency"].meta.per_year:
            raise ValueError(
                f"Cannot have a growth frequency ({v}) that is more frequent than the money flow frequency ({values['frequency']})"
            )
        return v

    def future_value(self) -> pd.Series:
        """Return Future Value for entire date range

        A = P(1 + r/n)(nt)
        https://www.thecalculatorsite.com/articles/finance/compound-interest-formula.php

        a = the future value of the investment/loan, including interest
        p = the principal investment amount (the initial deposit or loan amount)
        r = the annual interest rate (decimal)
        n = the number of times that interest is compounded per unit t
        t = the time (months, years, etc) the money is invested or borrowed for

        Args:
            num_months (int): _description_
        """

        return_series = pd.Series(
            data=np.nan,
            index=pd.date_range(
                start=self.start_month,
                end=self.end_month,
                freq="MS",  # Month Start Frequency
            ),
        )

        if self.growth_frequency == Frequency.YEARLY:
            # Find the new amount for each year - then distribute among the months
            date_range = pd.date_range(
                start=self.start_month,
                end=self.end_month,
                freq="YS",  # Year Start Frequency
            )
            p = self.amount * self.frequency.meta.per_year
            r = self.growth_rate
            t = np.arange(0, len(date_range))
            n = 1
            a = p * (1 + r / n) ** (n * t)

            a_df = pd.Series(data=a, index=date_range)

            if self.frequency == Frequency.YEARLY:
                return_series.loc[a_df.index] = a_df.values
                return_series = return_series.fillna(value=0.0)
            elif self.frequency == Frequency.MONTHLY:
                # Fill in the start of each year with the yearly values / 12
                return_series.loc[a_df.index] = a_df.values / 12.0
                # Fill in the rest of each year with the monthly values
                return_series = return_series.fillna(method="ffill")
            else:
                raise NotImplementedError(
                    f'Calculation for Flow Frequency "{self.frequency}" has not been implemented yet '
                )
        elif self.growth_frequency == Frequency.MONTHLY:
            # Find the new amount for each year - then distribute among the months
            date_range = pd.date_range(
                start=self.start_month,
                end=self.end_month,
                freq="MS",  # Year Start Frequency
            )
            p = self.amount * self.frequency.meta.per_month
            r = self.growth_rate
            t = np.arange(0, len(date_range))
            n = 1
            a = p * (1 + r / n) ** (n * t)

            a_df = pd.Series(data=a, index=date_range)
            return_series.loc[a_df.index] = a_df.values
        else:
            raise NotImplementedError(
                f'Calculation for Growth Frequency "{self.growth_frequency}" has not been implemented yet '
            )

        return return_series


class InvestmentType(str, Enum):
    ROTH_401K: str = 'Roth 401k'
    TRADITIONAL_401K: str = '401k'
    ROTH_IRA: str = 'Roth IRA'
    TRADITIONAL_IRA: str = 'IRA'
    BROKERAGE_ACCOUNT: str = 'Brokerage Account'

    @property
    def tax_advantaged(self) -> bool:
        if self.value == 'Brokerage Account':
            return False
        return True


# TODO: How to handle company 401k contribution
class Investment(BaseModel):
    name: str
    active: bool = True
    tax_advantaged: bool = False
    withdrawal_min_age: Optional[int]

    principal_investment: float = 0.0

    contribution_amount: float
    contribution_frequency: Frequency
    contribution_at_start_of_compound_period: bool = True

    annual_interest_rate: float
    compounding_frequency: Frequency

    # TODO: Add validators to ensure these are starts of the month
    start_month: dt.date
    end_month: dt.date

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def compound_interest(self):
        # annual_interest_rate / unit_t_per_year
        r = self.annual_interest_rate / 12.0
        # Number of times that interest is compounded per unit t
        n = self.compounding_frequency.meta.per_month
        return (1 + r / n) ** (n * 1)

    def future_value(self) -> pd.Series:
        """Return Future Value for entire date range

        https://www.vertex42.com/Calculators/compound-interest-calculator.html#calculator
        """
        return_series = pd.Series(
            data=np.nan,
            index=pd.date_range(
                start=self.start_month,
                end=self.end_month,
                freq="MS",  # Month Start Frequency
            ),
        )
        return_series.iloc[0] = self.principal_investment

        current_value = np.nan
        for iloc, month in enumerate(return_series.index.month):
            if iloc == 0:
                current_value = self.principal_investment
                continue
            contribute = month in self.contribution_frequency.meta.trigger_months

            if contribute and self.contribution_at_start_of_compound_period:
                # Time to add a contribution
                current_value += self.contribution_amount

            # Compound Interest if needed
            if month in self.compounding_frequency.meta.trigger_months:
                # Time to compound
                current_value *= self.compound_interest

            if contribute and not self.contribution_at_start_of_compound_period:
                # Time to add a contribution
                current_value += self.contribution_amount

            return_series.iloc[iloc] = current_value

        return return_series

    def future_value_old(self) -> pd.Series:
        """Return Future Value for entire date range

        https://www.vertex42.com/Calculators/compound-interest-calculator.html#calculator
        """
        return_series = pd.Series(
            data=np.nan,
            index=pd.date_range(
                start=self.start_month,
                end=self.end_month,
                freq="MS",  # Month Start Frequency
            ),
        )
        return_series.iloc[0] = self.principal_investment

        current_value = np.nan
        for iloc, month in enumerate(return_series.index.month):
            if iloc == 0:
                current_value = self.principal_investment
                continue
            contribute = month in self.contribution_frequency.meta.trigger_months

            if contribute and self.contribution_at_start_of_compound_period:
                # Time to add a contribution
                current_value += self.contribution_amount

            # Compound Interest if needed
            if month in self.compounding_frequency.meta.trigger_months:
                # Time to compound
                current_value *= (1.0 + self.annual_interest_rate / self.compounding_frequency.meta.per_year)

            if contribute and not self.contribution_at_start_of_compound_period:
                # Time to add a contribution
                current_value += self.contribution_amount

            return_series.iloc[iloc] = current_value

        return return_series


class IncomeTax:
    pass

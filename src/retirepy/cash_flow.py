import numpy as np
from pydantic import BaseModel
from retirepy.models import (
    CompoundingFrequency,
    ContributionFrequency,
    OccurrenceFrequency,
)
from retirepy.future_value import compute_future_value_series


class CashFlow(BaseModel):
    name: str

    def future_value(self, num_months: int):
        raise NotImplementedError()


class Investment(CashFlow):
    principal_investment: float
    annual_interest_rate: float
    compounding_frequency: CompoundingFrequency = ContributionFrequency.YEARLY
    contribution_amount: float = 0.0
    contribution_frequency: ContributionFrequency = ContributionFrequency.MONTHLY
    contribution_at_start_of_compound_period: bool = True

    def future_value(self, num_months: int):
        return compute_future_value_series(
            num_months=num_months,
            principal_investment=self.principal_investment,
            annual_interest_rate=self.annual_interest_rate,
            compounding_frequency=self.compounding_frequency,
            contribution_amount=self.contribution_amount,
            contribution_frequency=self.contribution_frequency,
            contribution_at_start_of_compound_period=self.contribution_at_start_of_compound_period,
        )


class EarnedIncome(CashFlow):
    starting_salary: float
    annual_percentage_increase: float

    def future_value(self, num_months: int):
        return compute_future_value_series(
            num_months=num_months,
            principal_investment=self.starting_salary,
            annual_interest_rate=self.annual_percentage_increase,
            compounding_frequency=CompoundingFrequency.YEARLY,
        )


class OneTimeIncome(CashFlow):
    amount: float
    month: int

    def future_value(self, num_months: int):
        fv = np.zeros(num_months)
        fv[self.month] = self.amount
        return fv


class OneTimeExpense(CashFlow):
    amount: float
    month: int

    def future_value(self, num_months: int):
        fv = np.zeros(num_months)
        fv[self.month] = self.amount
        return fv


class RecurringExpense(CashFlow):
    amount: float
    frequency: OccurrenceFrequency

    def future_value(self, num_months: int):
        months = np.arange(0, num_months) % 12 + 1
        fv = np.zeros(num_months)
        fv[np.isin(months, self.frequency.meta.trigger_months)] = self.amount
        return fv

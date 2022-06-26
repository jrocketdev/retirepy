import pytest
import pandas as pd
from retirepy.models import Frequency
from retirepy.utils import compute_future_value_series


class TestComputeFutureValueSeries:
    """
    Use https://www.thecalculatorsite.com/finance/calculators/compoundinterestcalculator.php
    for validation
    """

    @pytest.mark.parametrize(
        argnames=["input_dict", "expected_output"],
        argvalues=[
            [
                # https://www.thecalculatorsite.com/compound?a=12000&p=7&pp=yearly&y=1&m=0&rd=0&rp=monthly&rt=deposit&rw=0&rwp=1m&rm=beginning&ci=monthly&ip=&c=1&di=
                dict(
                    start_month=pd.Timestamp(year=2022, month=1, day=1),
                    end_month=pd.Timestamp(year=2022 + 1, month=1, day=1),
                    principal_investment=12000.0,
                    annual_interest_rate=0.07,
                    compounding_frequency=Frequency.MONTHLY,
                    contribution_amount=0.0,
                    contribution_frequency=Frequency.MONTHLY,
                    contribution_at_start_of_compound_period=True,
                ),
                12_867.48,
            ],
            [
                # https://www.thecalculatorsite.com/compound?a=12000&p=7&pp=yearly&y=1&m=0&rd=100&rp=monthly&rt=deposit&rw=0&rwp=1m&rm=beginning&ci=monthly&ip=&c=1&di=
                dict(
                    start_month=pd.Timestamp(year=2022, month=1, day=1),
                    end_month=pd.Timestamp(year=2022 + 1, month=1, day=1),
                    principal_investment=12000.0,
                    annual_interest_rate=0.07,
                    compounding_frequency=Frequency.MONTHLY,
                    contribution_amount=100.0,
                    contribution_frequency=Frequency.MONTHLY,
                    contribution_at_start_of_compound_period=True,
                ),
                14_113.97,
            ],
            [
                # https://www.thecalculatorsite.com/compound?a=12000&p=7&pp=yearly&y=1&m=0&rd=100&rp=monthly&rt=deposit&rw=0&rwp=1m&rm=end&ci=monthly&ip=&c=1&di=
                dict(
                    start_month=pd.Timestamp(year=2022, month=1, day=1),
                    end_month=pd.Timestamp(year=2022 + 1, month=1, day=1),
                    principal_investment=12000.0,
                    annual_interest_rate=0.07,
                    compounding_frequency=Frequency.MONTHLY,
                    contribution_amount=100.0,
                    contribution_frequency=Frequency.MONTHLY,
                    contribution_at_start_of_compound_period=False,
                ),
                14_106.74,
            ],
            [
                # https://www.thecalculatorsite.com/compound?a=12000&p=7&pp=yearly&y=10&m=0&rd=0&rp=monthly&rt=deposit&rw=0&rwp=1m&rm=beginning&ci=yearly&ip=&c=1&di=
                dict(
                    start_month=pd.Timestamp(year=2022, month=1, day=1),
                    end_month=pd.Timestamp(year=2022 + 10, month=1, day=1),
                    principal_investment=12000.0,
                    annual_interest_rate=0.07,
                    compounding_frequency=Frequency.YEARLY,
                    contribution_amount=0.0,
                    contribution_frequency=Frequency.YEARLY,
                    contribution_at_start_of_compound_period=True,
                ),
                23_605.82,
            ],
            [
                # https://www.thecalculatorsite.com/compound?a=12000&p=7&pp=yearly&y=10&m=0&rd=100&rp=yearly&rt=deposit&rw=0&rwp=1m&rm=beginning&ci=yearly&ip=&c=1&di=
                dict(
                    start_month=pd.Timestamp(year=2022, month=1, day=1),
                    end_month=pd.Timestamp(year=2022 + 10, month=1, day=1),
                    principal_investment=12000.0,
                    annual_interest_rate=0.07,
                    compounding_frequency=Frequency.YEARLY,
                    contribution_amount=100.0,
                    contribution_frequency=Frequency.YEARLY,
                    contribution_at_start_of_compound_period=True,
                ),
                25_084.18,
            ],
            [
                # https://www.thecalculatorsite.com/compound?a=12000&p=7&pp=yearly&y=10&m=0&rd=100&rp=monthly&rt=deposit&rw=0&rwp=1m&rm=beginning&ci=yearly&ip=&c=1&di=
                dict(
                    start_month=pd.Timestamp(year=2022, month=1, day=1),
                    end_month=pd.Timestamp(year=2022 + 10, month=1, day=1),
                    principal_investment=12000.0,
                    annual_interest_rate=0.07,
                    compounding_frequency=Frequency.YEARLY,
                    contribution_amount=100.0,
                    contribution_frequency=Frequency.MONTHLY,
                    contribution_at_start_of_compound_period=True,
                ),
                40_814.20,
            ],
        ],
        ids=[
            "monthly compounding interest with no contribution",
            "monthly compounding interest with monthly contribution at start of period",
            "monthly compounding interest with monthly contribution at end of period",
            "yearly compounding interest with no contribution",
            "yearly compounding interest with yearly contribution at start of period",
            "yearly compounding interest with monthly contribution at start of period",
        ],
    )
    def test_future_values_final_value(self, request, input_dict, expected_output):
        fv_series = compute_future_value_series(**input_dict)
        print(fv_series)
        assert (fv_series[-1]).round(2) == expected_output

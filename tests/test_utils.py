import pytest
import pandas as pd
from pathlib import Path
from retirepy.future_value import compute_future_value_series


class TestComputeFutureValueSeries:
    """
    Use https://www.thecalculatorsite.com/finance/calculators/compoundinterestcalculator.php
    for validation
    """

    TESTS = [
        {
            "name": "monthly compounding interest with no contribution",
            "link": "https://www.thecalculatorsite.com/compound?a=12000&p=7&pp=yearly&y=1&m=0&rd=0&rp=monthly&rt=deposit&rw=0&rwp=1m&rm=beginning&ci=monthly&ip=&c=1&di=",
            "input": dict(
                num_months=12 + 1,
                principal_investment=12000.0,
                annual_interest_rate=0.07,
                compounding_frequency="Monthly",
                contribution_amount=0.0,
                contribution_frequency="Monthly",
                contribution_at_start_of_compound_period=True,
            ),
            "expected": 12_867.48,
        },
        {
            "name": "monthly compounding interest with monthly contribution at start of period",
            "link": "https://www.thecalculatorsite.com/compound?a=12000&p=7&pp=yearly&y=1&m=0&rd=100&rp=monthly&rt=deposit&rw=0&rwp=1m&rm=beginning&ci=monthly&ip=&c=1&di=",
            "input": dict(
                num_months=12 + 1,
                principal_investment=12000.0,
                annual_interest_rate=0.07,
                compounding_frequency="Monthly",
                contribution_amount=100.0,
                contribution_frequency="Monthly",
                contribution_at_start_of_compound_period=True,
            ),
            "expected": 14_113.97,
        },
        {
            "name": "monthly compounding interest with monthly contribution at end of period",
            "link": "https://www.thecalculatorsite.com/compound?a=12000&p=7&pp=yearly&y=1&m=0&rd=100&rp=monthly&rt=deposit&rw=0&rwp=1m&rm=end&ci=monthly&ip=&c=1&di=",
            "input": dict(
                num_months=12 + 1,
                principal_investment=12000.0,
                annual_interest_rate=0.07,
                compounding_frequency="Monthly",
                contribution_amount=100.0,
                contribution_frequency="Monthly",
                contribution_at_start_of_compound_period=False,
            ),
            "expected": 14_106.74,
        },
        {
            "name": "yearly compounding interest with no contribution",
            "link": "https://www.thecalculatorsite.com/compound?a=12000&p=7&pp=yearly&y=10&m=0&rd=0&rp=monthly&rt=deposit&rw=0&rwp=1m&rm=beginning&ci=yearly&ip=&c=1&di=",
            "input": dict(
                num_months=12 * 10 + 1,
                principal_investment=12000.0,
                annual_interest_rate=0.07,
                compounding_frequency="Yearly",
                contribution_amount=0.0,
                contribution_frequency="Yearly",
                contribution_at_start_of_compound_period=True,
            ),
            "expected": 23_605.82,
        },
        {
            "name": "yearly compounding interest with yearly contribution at start of period",
            "link": "https://www.thecalculatorsite.com/compound?a=12000&p=7&pp=yearly&y=10&m=0&rd=100&rp=yearly&rt=deposit&rw=0&rwp=1m&rm=beginning&ci=yearly&ip=&c=1&di=",
            "input": dict(
                num_months=12 * 10 + 1,
                principal_investment=12000.0,
                annual_interest_rate=0.07,
                compounding_frequency="Yearly",
                contribution_amount=100.0,
                contribution_frequency="Yearly",
                contribution_at_start_of_compound_period=True,
            ),
            "expected": 25_084.18,
        },
        {
            "name": "yearly compounding interest with monthly contribution at start of period",
            "link": "https://www.thecalculatorsite.com/compound?a=12000&p=7&pp=yearly&y=10&m=0&rd=100&rp=monthly&rt=deposit&rw=0&rwp=1m&rm=beginning&ci=yearly&ip=&c=1&di=",
            "input": dict(
                num_months=12 * 10 + 1,
                principal_investment=12000.0,
                annual_interest_rate=0.07,
                compounding_frequency="Yearly",
                contribution_amount=100.0,
                contribution_frequency="Monthly",
                contribution_at_start_of_compound_period=True,
            ),
            "expected": 40_814.20,
        },
    ]

    @pytest.mark.parametrize(
        argnames=["input_dict", "expected_output", "check_link"],
        argvalues=[(_["input"], _["expected"], _["link"]) for _ in TESTS],
        ids=[_["name"] for _ in TESTS],
    )
    def test_future_values_final_value(
        self, request, input_dict: dict, expected_output: float, check_link: str
    ):
        fv_series = compute_future_value_series(**input_dict)
        fail_msg = f"Failed, check link: {check_link}"
        try:
            assert (fv_series[-1]).round(2) == expected_output, fail_msg
        except:
            data_dir = Path(__file__).parent / "data"
            data_fname = "_".join(request.node.callspec.id.split()) + ".csv"
            data_fpath = data_dir / data_fname
            if data_fpath.exists():
                df = pd.read_csv(data_fpath)

                print(fv_series)
                print(df["Balance"].values)

                comparison_df = pd.DataFrame(
                    data={
                        "actual_balance": fv_series,
                        "expected_balance": df["Balance"].values,
                    },
                    index=df.index,
                )
                print(comparison_df)

                # TODO: Compare expected to actual
            else:
                print("Unable to find csv file with expected data")
            raise

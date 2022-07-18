from enum import Enum
from pydantic import BaseModel, validator, PrivateAttr

COMPOUNDING_TRIGGER_MONTHS = {
    12: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    4: [3, 6, 9, 12],
    2: [6, 12],
    1: [12],
}

CONTRIBUTION_TRIGGER_MONTHS = {
    12: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    4: [1, 4, 7, 10],
    2: [1, 7],
    1: [1],
}

TRIGGER_MONTH_DICT = {
    "Compounding": COMPOUNDING_TRIGGER_MONTHS,
    "Contribution": CONTRIBUTION_TRIGGER_MONTHS,
}


class FrequencyType(str, Enum):
    COMPOUNDING: str = "Compounding"
    CONTRIBUTION: str = "Contribution"


class FrequencyMeta(BaseModel):
    name: str
    per_year: int
    frequency_type: FrequencyType
    _trigger_months: list[int] = PrivateAttr()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._trigger_months = TRIGGER_MONTH_DICT[self.frequency_type.value][
            self.per_year
        ]

    @validator("per_year")
    def ensure_per_year_in_allowed(cls, v):
        if v not in [1, 2, 4, 12]:
            raise ValueError(
                "per_year can only be 1 (yearly), 2 (semi-annually), 4 (quarterly), 12 (monthly)"
            )
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


MONTHLY_CONTRIBUTION_META = FrequencyMeta(
    name="Monthly", per_year=12, frequency_type="Contribution"
)
YEARLY_CONTRIBUTION_META = FrequencyMeta(
    name="Yearly", per_year=1, frequency_type="Contribution"
)
MONTHLY_COMPOUNDING_META = FrequencyMeta(
    name="Monthly", per_year=12, frequency_type="Compounding"
)
YEARLY_COMPOUNDING_META = FrequencyMeta(
    name="Yearly", per_year=1, frequency_type="Compounding"
)


class ContributionFrequency(str, Enum):
    MONTHLY: str = "Monthly"
    YEARLY: str = "Yearly"

    @property
    def meta(self) -> FrequencyMeta:
        return {
            "Monthly": MONTHLY_CONTRIBUTION_META,
            "Yearly": YEARLY_CONTRIBUTION_META,
        }[self.value]


class CompoundingFrequency(str, Enum):
    MONTHLY: str = "Monthly"
    YEARLY: str = "Yearly"

    @property
    def meta(self) -> FrequencyMeta:
        return {
            "Monthly": MONTHLY_COMPOUNDING_META,
            "Yearly": YEARLY_COMPOUNDING_META,
        }[self.value]

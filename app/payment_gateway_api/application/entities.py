
from dataclasses import dataclass
from typing import Literal

STATUS_TYPE = Literal["Authorized", "Declined"]

@dataclass(frozen=True)
class BaseEntity:
    id: str

@dataclass(frozen=True)
class Payment(BaseEntity):
    card_number: str
    expiry_month: int
    expiry_year: int
    currency: str
    amount: int
    cvv: str
    status: STATUS_TYPE | None = None


from typing import Annotated

from pydantic import AfterValidator


def is_valid_card_number(card_number: str) -> str:
    """
    Validates the card number format.
    """
    if not card_number.isdigit():
        raise ValueError("Card number must contain only digits.")
    if not (14 <= len(card_number) <= 19):
        raise ValueError("Card number must be between 14 and 19 characters long.")
    return card_number

def is_valid_expiry_month(month: int) -> int:
    """
    Validates the expiry month.
    """
    if month < 1 or month > 12:
        raise ValueError("Expiry month must be between 1 and 12.")
    return month

def is_valid_cvv(cvv: str) -> str:
    """
    Validates the CVV.
    """
    if not cvv.isdigit() or len(cvv) not in [3, 4]:
        raise ValueError("CVV must be 3 or 4 digits.")
    return cvv

def is_valid_currency(currency: str) -> str:
    """
    Validates the currency.
    """
    if len(currency) != 3 or not currency.isalpha():
        raise ValueError("Currency must be a 3-letter ISO code.")
    if currency.upper() not in ["USD", "EUR", "GBP"]:
        raise ValueError("Currency must be one of: USD, EUR, GBP.")
    return currency.upper()

CurrencyField = Annotated[str, AfterValidator(is_valid_currency)]
CvvField = Annotated[str, AfterValidator(is_valid_cvv)]
ExpiryMonthField = Annotated[int, AfterValidator(is_valid_expiry_month)]
CardNumberField = Annotated[str, AfterValidator(is_valid_card_number)]
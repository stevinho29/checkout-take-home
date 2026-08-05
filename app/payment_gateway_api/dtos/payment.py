
from payment_gateway_api.application.entities import Payment
from payment_gateway_api.dtos.fields import CardNumberField, CurrencyField, CvvField, ExpiryMonthField, ExpiryYearField
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from uuid import uuid4


class GetPaymentDTO(BaseModel):
    """
    DTO for getting a payment.
    """

    id: str = Field(..., description="The id of the payment.")
    status: str = Field(..., description="The status of the payment.")
    last_four_card_digits: str = Field(..., description="The last four digits of the card number.")
    expiry_month: int = Field(..., description="The expiry month of the card.")
    expiry_year: int = Field(..., description="The expiry year of the card.")
    currency: str = Field(..., description="The currency of the payment.")
    amount: int = Field(..., description="The amount of the payment.")

    @staticmethod
    def from_entity(payment: Payment) -> "GetPaymentDTO":
        """
        Converts a Payment entity to a GetPaymentDTO.
        """
        return GetPaymentDTO(
            id=payment.id,
            status=payment.status,
            last_four_card_digits=payment.card_number[-4:],
            expiry_month=payment.expiry_month,
            expiry_year=payment.expiry_year,
            currency=payment.currency,
            amount=payment.amount,
        )

class PostPaymentDTO(BaseModel):
    """
    DTO for creating a payment.
    """

    card_number: CardNumberField
    expiry_month: ExpiryMonthField
    expiry_year: ExpiryYearField
    cvv: CvvField
    currency: CurrencyField
    amount: int = Field(..., gt=0, description="The amount of the payment.")

    @model_validator(mode="after")
    def validate_expiry_in_future(self):
        """
        Validates that the combination of expiry month and year is in the future.
        """
        now = datetime.now()
        if (self.expiry_year, self.expiry_month) < (now.year, now.month):
            raise ValueError("The card has expired.")
        return self

    def to_entity(self) -> Payment:
        """
        Converts the DTO to a Payment entity.
        """
        return Payment(
            id=str(uuid4()),
            card_number=self.card_number,
            expiry_month=self.expiry_month,
            expiry_year=self.expiry_year,
            currency=self.currency,
            amount=self.amount,
            cvv=self.cvv,
        )
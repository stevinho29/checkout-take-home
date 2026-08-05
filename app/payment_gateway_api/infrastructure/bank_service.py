
import logging
from httpx import AsyncClient
from dataclasses import dataclass

from payment_gateway_api.application.entities import Payment
from payment_gateway_api.application.exceptions import BankUnavailable
from payment_gateway_api.settings import BANK_SERVICE_HOST

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PaymentResponse:
    authorized: bool
    authorization_code: str

@dataclass(frozen=True)
class PaymentRequest:
    card_number: str
    expiry_date: str
    currency: str
    amount: float
    cvv: str

class BankService:

    def __init__(self):
        self.client = AsyncClient()
        self.log_header = "[BankService]"

    def _build_request(self, payment: Payment) -> dict:
        return {
            "card_number": payment.card_number,
            "expiry_date": f"{payment.expiry_month}/{payment.expiry_year}",
            "currency": payment.currency,
            "amount": payment.amount,
            "cvv": payment.cvv
        }
    
    async def pay(self, payment: Payment):
        log_header = f"{self.log_header}[pay]"
        logger.info(
            f"{log_header} About to call bank service to process payment with ID: {payment.id}"
        )
        response = await self.client.post(
            url=f"{BANK_SERVICE_HOST}/payments",
            timeout=10, # timeout arbitraire à uniformiser si besoin
            json=self._build_request(payment)
        )
        if response.status_code != 200:
            logger.error(f"{log_header} request to bank service failed with status code {response.status_code}")
            logger.error(f"{log_header} response content: {response.text}")
            raise BankUnavailable(f"Payment failed with status code {response.status_code}")
        
        logger.info(
            f"{log_header} Payment with ID: {payment.id} processed successfully with status code {response.status_code}"
        )
        return PaymentResponse(**response.json())
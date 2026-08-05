

from payment_gateway_api.application.entities import Payment
from payment_gateway_api.application.ports import IRepository


class PaymentRepository(IRepository):

    REPO: dict[str, Payment] = {}
    
    @classmethod
    async def get_by_id(cls, id: str) -> Payment:
        return PaymentRepository.REPO.get(id)

    @classmethod
    async def insert(cls, payment: Payment) -> Payment:
        cls.REPO[payment.id] = payment
        return payment
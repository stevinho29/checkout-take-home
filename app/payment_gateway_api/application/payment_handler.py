import logging
from dataclasses import replace
from payment_gateway_api.const import PAYMENT_STATUS_AUTHORIZED, PAYMENT_STATUS_DECLINED
from payment_gateway_api.application.exceptions import NotFound
from payment_gateway_api.application.ports import IRepository, IBankService
from payment_gateway_api.dtos.payment import GetPaymentDTO, PostPaymentDTO

logger = logging.getLogger(__name__)


class PaymentHandler:
    def __init__(self, payment_repository: IRepository, bank_service: IBankService):
        self.payment_repository = payment_repository
        self.bank_service = bank_service
        self.log_header = "[PaymentHandler]"

    async def create_payment(self, payment_dto: PostPaymentDTO) -> GetPaymentDTO:
        log_header = f"{self.log_header}[create_payment]"
        payment = payment_dto.to_entity()

        response = await self.bank_service.pay(payment)
        status = PAYMENT_STATUS_AUTHORIZED if response.authorized else PAYMENT_STATUS_DECLINED
        payment = replace(payment, status=status)
        new_payment = await self.payment_repository.insert(payment)
        logger.info(
            f"{log_header} Payment with ID: {payment.id} inserted into repository with status {status}."
        )
        return GetPaymentDTO.from_entity(new_payment)

    async def get_payment(self, payment_id: str) -> GetPaymentDTO:
        log_header = f"{self.log_header}[get_payment]"
        payment = await self.payment_repository.get_by_id(id=payment_id)
        if not payment:
            logger.warning(f"{log_header} Payment with ID {payment_id} not found.")
            raise NotFound(f"Payment with ID {payment_id} not found.")
        logger.info(
            f"{log_header} Payment with ID: {payment.id} retrieved with success."
        )
        return GetPaymentDTO.from_entity(payment)

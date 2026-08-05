
import logging
from typing import Generator

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from payment_gateway_api.application.exceptions import BankUnavailable, NotFound
from payment_gateway_api.application.payment_handler import PaymentHandler
from payment_gateway_api.dtos.payment import GetPaymentDTO, PostPaymentDTO
from payment_gateway_api.infrastructure.bank_service import BankService
from payment_gateway_api.infrastructure.payment_repository import PaymentRepository

logger = logging.getLogger(__name__)

app = FastAPI()

def get_payment_repository() -> Generator[PaymentRepository]:
    yield PaymentRepository()

def get_bank_service() -> Generator[BankService]:
    yield BankService()

def get_payment_handler(
        payment_repository: PaymentRepository = Depends(get_payment_repository), 
        bank_service: BankService = Depends(get_bank_service)
) -> Generator[PaymentHandler]:
    yield PaymentHandler(payment_repository, bank_service)

@app.exception_handler(NotFound)
async def not_found_handler(request: Request, exc: NotFound) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc) or "Not found"})

@app.exception_handler(BankUnavailable)
async def bank_unavailable_handler(request: Request, exc: BankUnavailable) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc) or "Bank service unavailable"})


@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.post("/payments")
async def create_payment(
    payment: PostPaymentDTO, 
    payment_handler: PaymentHandler = Depends(get_payment_handler)
) -> GetPaymentDTO:
    return await payment_handler.create_payment(payment)


@app.get("/payments/{payment_id}")
async def get_payment(
    payment_id: str, 
    payment_handler: PaymentHandler = Depends(get_payment_handler)
) -> GetPaymentDTO:
    return await payment_handler.get_payment(payment_id)
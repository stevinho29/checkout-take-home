
from payment_gateway_api.const import PAYMENT_STATUS_AUTHORIZED, PAYMENT_STATUS_DECLINED
from datetime import datetime
from fastapi.testclient import TestClient
from payment_gateway_api.app import app, get_bank_service
from payment_gateway_api.application.entities import Payment
from payment_gateway_api.application.exceptions import BankUnavailable
from payment_gateway_api.application.ports import IBankService
from payment_gateway_api.infrastructure.bank_service import PaymentResponse
from payment_gateway_api.infrastructure.payment_repository import PaymentRepository
from pytest import fixture
import json

@fixture(autouse=True)
def clear_repository():
    PaymentRepository.REPO.clear()
    yield

@fixture
def client():
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@fixture
def client_unavailable_bank_service():
    client = TestClient(app)
    app.dependency_overrides[get_bank_service] = lambda: BankServiceMock()
    yield client
    app.dependency_overrides.clear()


class BankServiceMock(IBankService):
    async def pay(self, payment: Payment) -> PaymentResponse:
        raise BankUnavailable("Bank service is unavailable.")

def test_generate_doc():
    with open("openapi.json", "w") as f:
        json.dump(app.openapi(), f, indent=2)

class TestAPIPostPayment:


    def _get_valid_payload(self):
        year = datetime.now().year + 1
        return {
            "amount": 100.0,
            "currency": "USD",
            "card_number": "4111111111111111",
            "expiry_month": 12,
            "expiry_year": year,
            "cvv": "123"
        }
    
    def test_post_payment_bad_request(self, client: TestClient):
        # missing required field
        payload = self._get_valid_payload()
        del payload["cvv"]
        response = client.post("/payments", json=payload)
        assert response.status_code == 422

        # card number too short (below the 14-19 character range)
        payload = self._get_valid_payload()
        payload["card_number"] = "411111111111"
        response = client.post("/payments", json=payload)
        assert response.status_code == 422

        # card number contains non-numeric characters
        payload = self._get_valid_payload()
        payload["card_number"] = "411111111111111a"
        response = client.post("/payments", json=payload)
        assert response.status_code == 422

        # invalid card expiry month
        payload = self._get_valid_payload()
        payload["expiry_month"] = 13
        response = client.post("/payments", json=payload)
        assert response.status_code == 422

        # expiry date in the past
        payload = self._get_valid_payload()
        payload["expiry_month"] = 1
        payload["expiry_year"] = 2020
        response = client.post("/payments", json=payload)
        assert response.status_code == 422

        # unsupported currency
        payload = self._get_valid_payload()
        payload["currency"] = "XAF"
        response = client.post("/payments", json=payload)
        assert response.status_code == 422

        # invalid amount
        payload = self._get_valid_payload()
        payload["amount"] = -100.0
        response = client.post("/payments", json=payload)
        assert response.status_code == 422


    def test_post_payment_success(self, client: TestClient):
        payload = self._get_valid_payload()

        # authorized true, card ends with odd number
        payload["card_number"] = "4111111111111111"
        response = client.post("/payments", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == PAYMENT_STATUS_AUTHORIZED
        assert body["id"]
        assert body["last_four_card_digits"] == "1111"
        assert "card_number" not in body
        assert "cvv" not in body

        # authorized false, card ends with even number
        payload["card_number"] = "4111111111111112"
        response = client.post("/payments", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == PAYMENT_STATUS_DECLINED
        assert body["id"]

    def test_post_payment_unavailable_bank_service(self, client_unavailable_bank_service: TestClient):
        payload = self._get_valid_payload()

        response = client_unavailable_bank_service.post("/payments", json=payload)
        assert response.status_code == 503

class TestAPIGetPayment:

    def _get_valid_payload(self):
        year = datetime.now().year + 1
        return {
            "amount": 100.0,
            "currency": "USD",
            "card_number": "4111111111111111",
            "expiry_month": 12,
            "expiry_year": year,
            "cvv": "123"
        }
    
    def test_get_payment_not_found(self, client: TestClient):
        response = client.get("/payments/nonexistent-id")
        assert response.status_code == 404
        assert response.json() == {"detail": "Payment with ID nonexistent-id not found."}

    def test_get_payment_success(self, client: TestClient):
        # First, create a payment to ensure it exists
        payload = self._get_valid_payload()

        post_response = client.post("/payments", json=payload)
        assert post_response.status_code == 200
        post_response_data = post_response.json()
        payment_id = post_response_data["id"]

        # Now, retrieve the payment
        get_response = client.get(f"/payments/{payment_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == payment_id
        assert get_response.json() == post_response_data

    def test_get_declined_payment_success(self, client: TestClient):
        # Declined payments must also be retrievable afterwards
        payload = self._get_valid_payload()
        payload["card_number"] = "4111111111111112"  # ends even -> Declined

        post_response = client.post("/payments", json=payload)
        assert post_response.status_code == 200
        post_response_data = post_response.json()
        assert post_response_data["status"] == PAYMENT_STATUS_DECLINED
        payment_id = post_response_data["id"]

        get_response = client.get(f"/payments/{payment_id}")
        assert get_response.status_code == 200
        assert get_response.json() == post_response_data
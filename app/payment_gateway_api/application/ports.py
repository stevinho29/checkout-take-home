
from abc import ABC, abstractmethod

from payment_gateway_api.application.entities import BaseEntity

class IRepository(ABC):

    @abstractmethod
    def get_by_id(self, id: str) -> BaseEntity:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def insert(self, entity: BaseEntity) -> BaseEntity:
        raise NotImplementedError("Subclasses must implement this method.")


class IBankService(ABC):

    @abstractmethod
    def pay(self, payment: BaseEntity) -> dict:
        raise NotImplementedError("Subclasses must implement this method.")
from abc import *
from decimal import Decimal
from typing import *
import datetime

class Payment(ABC):

    @abstractmethod
    def get_payment_amount(self) -> Decimal:
        pass

    @abstractmethod
    def get_payment_date(self) -> str:
        pass

class Customer(ABC):

    @abstractmethod
    def get_customer_id(self) -> int:
        pass

    @abstractmethod
    def get_customer_balance(self) -> Decimal:
        pass

    @abstractmethod
    def get_customer_name(self) -> str:
        pass

    @abstractmethod
    def get_payment_list(self) -> List[Payment]:
        pass

    @abstractmethod
    def set_customer_balance(self, value: Decimal) -> None:
        pass
    
    @abstractmethod
    def set_customer_name(self, name: str) -> None:
        pass

    @abstractmethod
    def add_customer_entity(self, balance: Decimal) -> None:
        pass

    @abstractmethod
    def add_payment(self, amount: Decimal) -> None:
        pass


class Product(ABC):

    @abstractmethod
    def get_product_id(self) -> int:
        pass

    @abstractmethod
    def get_product_name(self) -> str:
        pass

    @abstractmethod
    def get_product_price(self) -> Decimal:
        pass

    @abstractmethod
    def set_product_name(self, value: str) -> None:
        pass
    
    @abstractmethod
    def set_product_price(self, name: Decimal) -> None:
        pass

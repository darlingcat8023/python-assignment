from abc import *
from decimal import Decimal
from typing import *

class OrderItem(ABC):
    
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
    def get_product_num(self) -> int:
        pass

    @abstractmethod
    def get_product_sub_total(self) -> Decimal:
        pass


class Order(ABC):

    @abstractmethod    
    def get_order_id(self) -> int:
        pass
    
    @abstractmethod
    def get_order_date(self) -> str:
        pass
    
    @abstractmethod
    def get_order_items(self) -> List[OrderItem]:
        pass

    @abstractmethod
    def get_order_total(self) -> Decimal:
        pass


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
    def get_customer_order(self) -> List[Order]:
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
    def add_customer_order(self, order_total: Decimal, order_items: List[OrderItem]) -> None:
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

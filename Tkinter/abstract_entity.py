import abc
from decimal import Decimal
from typing import *

C = TypeVar('C', bound = 'Customer')

class Customer(abc.ABC):

    @abc.abstractmethod
    def get_customer_id(self) -> int:
        pass

    @abc.abstractmethod
    def get_customer_balance(self) -> Decimal:
        pass

    @abc.abstractmethod
    def get_customer_name(self) -> str:
        pass

    @abc.abstractmethod
    def set_customer_balance(self, value: Decimal) -> C:
        pass
    
    @abc.abstractmethod
    def set_customer_name(self, name: str) -> C:
        pass

P = TypeVar('P', bound = 'Product')

class Product(abc.ABC):

    @abc.abstractmethod
    def get_product_id(self) -> int:
        pass

    @abc.abstractmethod
    def get_product_name(self) -> str:
        pass

    @abc.abstractmethod
    def get_product_price(self) -> Decimal:
        pass

    @abc.abstractmethod
    def set_product_name(self, value: str) -> C:
        pass
    
    @abc.abstractmethod
    def set_product_price(self, name: Decimal) -> C:
        pass
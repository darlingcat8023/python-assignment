from decimal import Decimal
from typing import TypeVar, List, Callable, Generic, Tuple

T = TypeVar("T")

class FieldWrapper(Generic[T]):

    __field: T
    __error_handler: Callable[[T], None]

    def __init__(self, field: T, error_handler: Callable[[T], None]) -> None:
        super().__init__()
        self.__field = field
        self.__error_handler = error_handler

    def get_value(self) -> T:
        return self.__field
    
    def get_error_handler(self) -> Callable[[T], None]:
        return self.__error_handler
    
    def set_value(self, T) -> None:
        self.__field = T


class CustomerAddEntity:

    __customer_name: FieldWrapper[str]
    __customer_balance: FieldWrapper[Decimal]

    def __init__(self, name_wrapper: FieldWrapper[str], balance_wrapper: FieldWrapper[Decimal]) -> None:
        self.__customer_name = name_wrapper
        self.__customer_balance = balance_wrapper
    
    def set_customer_name(self, customer_name: str) -> None:
        self.__customer_name.set_value(customer_name)

    def set_customer_balance(self, customer_balance: Decimal) -> None:
        self.__customer_balance.set_value(customer_balance)

    def get_customer_name(self) -> str:
        return self.__customer_name.get_value()
    
    def get_customer_balance(self) -> Decimal:
        return self.__customer_balance.get_value()

    def is_ready_for_submit(self) -> bool:
        name = self.get_customer_name()
        if name is None or len(name) == 0:
            handler = self.__customer_name.get_error_handler()
            if handler is not None : handler(name)
            return False
        if self.get_customer_balance() is None:
            handler = self.__customer_balance.get_error_handler()
            if handler is not None : handler(self.get_customer_balance())
            return False
        return True
    

class CustomerEditEntity(CustomerAddEntity):

    __customer_id: FieldWrapper[int]

    def __init__(self, id_wrapper: FieldWrapper[int], name_wrapper: FieldWrapper[str], balance_wrapper: FieldWrapper[Decimal]) -> None:
        super().__init__(name_wrapper, balance_wrapper)
        self.__customer_id = id_wrapper

    def get_customer_id(self) -> int:
        return self.__customer_id.get_value()
    

class ProductAddEntity:

    __product_name: FieldWrapper[str]
    __product_price: FieldWrapper[Decimal]

    def __init__(self, name_wrapper: FieldWrapper[str], price_wrapper: FieldWrapper[Decimal]) -> None:
        self.__product_name = name_wrapper
        self.__product_price = price_wrapper

    def set_product_name(self, product_name: str) -> None:
        self.__product_name.set_value(product_name)

    def set_product_price(self, product_price: Decimal) -> None:
        self.__product_price.set_value(product_price)

    def get_product_name(self) -> str:
        return self.__product_name.get_value()

    def get_product_price(self) -> Decimal:
        return self.__product_price.get_value()

    def is_ready_for_submit(self) -> bool:
        name = self.get_product_name()
        if name is None or len(name) == 0:
            handler = self.__product_name.get_error_handler()
            if handler is not None : handler(name)
            return False
        if self.get_product_price() is None:
            handler = self.__product_price.get_error_handler()
            if handler is not None : handler(self.get_customer_balance()).set_tip("Invalid Product Price input")
            return False
        return True
    

class ProductEditEntity(ProductAddEntity):

    __product_id: FieldWrapper[int]

    def __init__(self, id_wrapper: FieldWrapper[int], name_wrapper: FieldWrapper[str], price_wrapper: FieldWrapper[Decimal]) -> None:
        super().__init__(name_wrapper, price_wrapper)
        self.__product_id = id_wrapper

    def get_customer_id(self) -> int:
        return self.__product_id.get_value()


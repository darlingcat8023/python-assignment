from decimal import Decimal
from typing import TypeVar, List, Callable, Generic
from abc import *

T = TypeVar("T")

class FieldWrapper(Generic[T]):

    def __init__(self, field: T, error_handler: Callable[[T], None]) -> None:
        super().__init__()
        self.__field: T = field
        self.__error_handler: Callable[[T], None] = error_handler

    def get_value(self) -> T:
        return self.__field
    
    def get_error_handler(self) -> Callable[[T], None]:
        return self.__error_handler
    
    def set_value(self, T) -> None:
        self.__field = T

    def set_error_handler(self, handler: Callable[[T], None]) -> None:
        self.__error_handler = handler


class SelectableEntity(ABC):

    @abstractmethod
    def get_selection_key(self) -> str:
        pass


class CustomerAddEntity:

    def __init__(self, name_wrapper: FieldWrapper[str], balance_wrapper: FieldWrapper[Decimal]) -> None:
        self.__customer_name: FieldWrapper[str] = name_wrapper
        self.__customer_balance: FieldWrapper[Decimal] = balance_wrapper
    
    def set_customer_name(self, customer_name: str) -> None:
        self.__customer_name.set_value(customer_name)

    def set_name_error_hanlder(self, handler: Callable[[str], None]) -> None:
        self.__customer_name.set_error_handler(handler)

    def set_customer_balance(self, customer_balance: Decimal) -> None:
        self.__customer_balance.set_value(customer_balance)

    def set_balance_error_hanlder(self, handler: Callable[[Decimal], None]) -> None:
        self.__customer_balance.set_error_handler(handler)

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

    def __init__(self, id_wrapper: FieldWrapper[int], name_wrapper: FieldWrapper[str], balance_wrapper: FieldWrapper[Decimal]) -> None:
        super().__init__(name_wrapper, balance_wrapper)
        self.__customer_id: FieldWrapper[int] = id_wrapper

    def get_customer_id(self) -> int:
        return self.__customer_id.get_value()
    

class CustomerViewEntity(CustomerEditEntity, SelectableEntity):

    def __init__(self, id: int, name: str, balance: Decimal) -> None:
        super().__init__(FieldWrapper[int](id, None), FieldWrapper[str](name, None), FieldWrapper[Decimal](balance, None))

    def get_selection_key(self) -> str:
        return "{0} [ID:{1}]".format(self.get_customer_name(), self.get_customer_id())
    
    def text_print_on_text_box(self) -> None:
            return f"Customer Id:\t\t{self.get_customer_id()}\nCustomer Name:\t\t{self.get_customer_name()}\nCustomer Balance:\t\t{self.get_customer_balance()}"
    

class CustomerListFilterEntity:

    def __init__(self) -> None:
        self.__customer_name: str = None

    def set_customer_name(self, name: str) -> None:
        self.__customer_name = name

    def get_customer_name(self) -> str:
        return self.__customer_name
    

class ProductAddEntity:

    def __init__(self, name_wrapper: FieldWrapper[str], price_wrapper: FieldWrapper[Decimal]) -> None:
        self.__product_name: FieldWrapper[str] = name_wrapper
        self.__product_price: FieldWrapper[Decimal] = price_wrapper

    def set_product_name(self, product_name: str) -> None:
        self.__product_name.set_value(product_name)

    def set_name_error_hanlder(self, handler: Callable[[str], None]) -> None:
        self.__product_name.set_error_handler(handler)

    def set_product_price(self, product_price: Decimal) -> None:
        self.__product_price.set_value(product_price)

    def set_price_error_hanlder(self, handler: Callable[[Decimal], None]) -> None:
        self.__product_price.set_error_handler(handler)

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
            if handler is not None : handler(self.get_product_price())
            return False
        return True
    

class ProductEditEntity(ProductAddEntity):

    def __init__(self, id_wrapper: FieldWrapper[int], name_wrapper: FieldWrapper[str], price_wrapper: FieldWrapper[Decimal]) -> None:
        super().__init__(name_wrapper, price_wrapper)
        self.__product_id: FieldWrapper[int] = id_wrapper

    def get_product_id(self) -> int:
        return self.__product_id.get_value()


class ProductViewEntity(ProductEditEntity, SelectableEntity):

    def __init__(self, id: int, name: str, price: Decimal) -> None:
        super().__init__(FieldWrapper[int](id, None), FieldWrapper[str](name, None), FieldWrapper[Decimal](price, None))

    def get_selection_key(self) -> str:
        return "{0} [ID:{1}]".format(self.get_product_name(), self.get_product_id())
    

class ProductListFilterEntity:

    def __init__(self) -> None:
        self.__product_name: str = None

    def set_product_name(self, name: str) -> None:
        self.__product_name = name

    def get_product_name(self) -> str:
        return self.__product_name
    

class OrderCreateEntity:

    class OrderCustomerEntity:

        def __init__(self, id: int, name: str, balance: Decimal) -> None:
            self.__customer_id: int = id
            self.__customer_name: str = name
            self.__customer_balance: Decimal = balance

        def get_customer_id(self) -> int:
            return self.__customer_id
        
        def get_customer_name(self) -> str:
            return self.__customer_name
        
        def get_customer_balance(self) -> Decimal:
            return self.__customer_balance
        
    class OrderProductEntity:

        def __init__(self, id: int, name: str, price: Decimal, num: int = 0, sub_total: Decimal = Decimal(0.00)) -> None:
            self.__product_id: int = id
            self.__product_name: str = name
            self.__product_price: Decimal = price
            self.__product_num: int = num
            self.__product_sub_total: Decimal = sub_total

        def get_product_id(self) -> int:
            return self.__product_id
        
        def get_product_name(self) -> str:
            return self.__product_name
        
        def get_product_price(self) -> Decimal:
            return self.__product_price
        
        def get_product_num(self) -> int:
            return self.__product_num

        def get_product_sub_total(self) -> Decimal:
            return self.__product_sub_total
        
        def set_product_id(self, id: int) -> None:
            self.__product_id = id

        def set_product_name(self, name: str) -> None:
            self.__product_name = name

        def set_product_price(self, price: Decimal) -> None:
            self.__product_price = price
            self.recalculate_total()

        def set_product_num(self, num: int) -> None:
            self.__product_num = num
            self.recalculate_total()

        def set_product_sub_total(self, sub_total: Decimal) -> None:
            self.__product_sub_total = sub_total

        def recalculate_total(self) -> None:
            if self.get_product_num() is None:
                return
            if self.get_product_price() is None:
                return
            self.set_product_sub_total(self.get_product_num() * self.get_product_price())
 
        def text_print_on_text_box(self) -> None:
            return f"Product Id:\t{self.get_product_id()}\tProduct Name:\t{self.get_product_name()}\nProduct Num:\t{self.get_product_num()}\tProduct Price:\t{self.get_product_price()}\nSub Total:\t{self.get_product_sub_total()}"
        
        def text_print_on_cell(self) -> None:
            return f"Product Name: {self.get_product_name()}, Product Num: {self.get_product_num()}, Product Price: {self.get_product_price()}, Sub Total: {self.get_product_sub_total()}"
    
    def __init__(self) -> None:
        self.__customer: OrderCreateEntity.OrderCustomerEntity = None
        self.__temp_entity: OrderCreateEntity.OrderProductEntity = OrderCreateEntity.OrderProductEntity(None, None, None)
        self.__items: List[OrderCreateEntity.OrderProductEntity] = []
        self.__order_price: Decimal = Decimal(0.00)

    def get_customer(self) -> OrderCustomerEntity:
        return self.__customer
    
    def get_order_items(self) -> List[OrderProductEntity]:
        return self.__items

    def set_customer(self, id: int, name: str, balance: Decimal) -> None:
        self.__customer = OrderCreateEntity.OrderCustomerEntity(id, name, balance)

    def set_temp_entity(self, id: int, name: str, price: Decimal) -> None:
        self.__temp_entity.set_product_id(id)
        self.__temp_entity.set_product_name(name)
        self.__temp_entity.set_product_price(price)

    def set_temp_num(self, num: int) -> None:
        self.__temp_entity.set_product_num(num)

    def confirm_product(self) -> None:
        ent = self.__temp_entity
        items = self.get_order_items()
        item = next((p for p in items if p.get_product_id() == ent.get_product_id()), None)
        if item is None:
            item = OrderCreateEntity.OrderProductEntity(ent.get_product_id(), ent.get_product_name(), ent.get_product_price(), ent.get_product_num(), ent.get_product_sub_total())
            items.append(item)
            self.__order_price += item.get_product_sub_total()
        else:
            item.set_product_num(item.get_product_num() + ent.get_product_num())
            self.__order_price +=  ent.get_product_num() * ent.get_product_price()

    def get_order_price(self) -> Decimal:
        return self.__order_price
    
    def text_print_on_product_box(self) -> None:
        return "\n\n".join(list(map(lambda item: item.text_print_on_text_box(), self.get_order_items()))) + f"\n\nOrder Total:\t{self.get_order_price()}"
    
    def is_reay_for_submit(self) -> None:
        if self.get_customer() is None:
            return False
        if len(self.get_order_items()) < 1:
            return False
        return True
    
class PaymentCreateEntity:

    def __init__(self) -> None:
        self.__customer_id: FieldWrapper[int] = FieldWrapper[int](None, None)
        self.__payment_amount: FieldWrapper[Decimal] = FieldWrapper[Decimal](Decimal(0.00), None)

    def get_customer_id(self) -> int:
        return self.__customer_id.get_value()

    def get_payment_amount(self) -> Decimal:
        return self.__payment_amount.get_value()
    
    def set_payment_amount_error_hanlder(self, handler: Callable[[Decimal], None]) -> None:
        self.__payment_amount.set_error_handler(handler)

    def set_customer_id(self, id: int) -> None:
        self.__customer_id.set_value(id)

    def set_payment_amount(self, amount: Decimal) -> None:
        self.__payment_amount.set_value(amount)

    def is_ready_for_submit(self) -> bool:
        if self.get_payment_amount() <= 0:
            handler = self.__payment_amount.get_error_handler()
            if handler is not None : handler(self.get_payment_amount())
            return False
        return True
    
class PaymentViewEneity:

    def __init__(self, id: int, name: str, amount: Decimal, date: str) -> None:
        self.__customer_id: int = id
        self.__customer_name: str = name
        self.__payment_amount: Decimal = amount
        self.__payment_date: str = date

    def get_customer_id(self) -> int:
        return self.__customer_id
    
    def get_customer_name(self) -> str:
        return self.__customer_name
    
    def get_payment_amount(self) -> Decimal:
        return self.__payment_amount
    
    def get_payment_date(self) -> str:
        return self.__payment_date
    

class OrderViewEntity:

    def __init__(self, customer_id: int, customer_name: str, order_id: int, order_date: str, order_items: List[OrderCreateEntity.OrderProductEntity], order_total: Decimal) -> None:
        self.__customer_id: int = customer_id
        self.__customer_name: str = customer_name
        self.__order_id: int = order_id
        self.__order_date: str = order_date
        self.__order_items: List[OrderCreateEntity.OrderProductEntity] = order_items
        self.__order_total: Decimal = order_total

    def get_customer_id(self) -> int:
        return self.__customer_id
    
    def get_customer_name(self) -> str:
        return self.__customer_name
    
    def get_order_id(self) -> int:
        return self.__order_id
    
    def get_order_date(self) -> str:
        return self.__order_date
    
    def get_formated_items(self) -> str:
        return "\n".join(list(map(lambda item: item.text_print_on_cell(), self.__order_items)))

    def get_order_total(self) -> Decimal:
        return self.__order_total
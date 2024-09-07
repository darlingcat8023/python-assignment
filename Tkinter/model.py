from decimal import Decimal
from typing import List
from abstract_model import *
from datetime import datetime

date_formate = "%d/%m/%Y %H:%M:%S" 
        
class ProductEntity(Product):
    
    __product_list: List[Product]

    @staticmethod
    def init_data_set() -> None:
        ProductEntity.__product_list = []
        for i in range(1, 200):
            ProductEntity.get_product_list().append(ProductEntity(i, "product-" + str(i), Decimal(i * 10)))

    @staticmethod
    def get_product_list() -> List[Product]:
        return ProductEntity.__product_list
    
    @staticmethod
    def append_product(name: str, price: Decimal) -> None:
        ProductEntity.get_product_list().append(ProductEntity(ProductEntity.__get_next_product_id(), name, price))

    @staticmethod
    def edit_product(id: str, name: str, price: Decimal) -> None:
        product = next(filter(lambda item: item.get_product_id() == id, ProductEntity.get_product_list()), None)
        if product:
            product.set_product_name(name)
            product.set_product_price(price)

    @staticmethod
    def __get_next_product_id() -> int:
        if len(ProductEntity.get_product_list()) == 0:
            return 1
        return max(map(lambda ent: ent.get_product_id(), ProductEntity.get_product_list())) + 1

    def __init__(self, product_id: int, product_name: str, product_price: Decimal = Decimal(0.00)) -> None:
        self.__product_id: int = product_id
        self.__product_price: str = product_price
        self.__product_name: Decimal = product_name

    def get_product_id(self) -> int:
        return self.__product_id

    def get_product_price(self) -> Decimal:
        return self.__product_price

    def get_product_name(self) -> str:
        return self.__product_name

    def set_product_price(self, value: Decimal) -> Product:
        self.__product_price = value
        return self
    
    def set_product_name(self, name: str) -> Product:
        assert name is not None and len(name) > 0
        self.__product_name = name
        return self


class PaymentEntity(Payment):

    def __init__(self, payment_amount: Decimal) -> None:
        self.__payment_amount = payment_amount
        self.__payment_date = datetime.strftime(datetime.now(), date_formate)

    def get_payment_amount(self) -> Decimal:
        return  self.__payment_amount
    
    def get_payment_date(self) -> str:
        return self.__payment_date


class OrderItemEntity(OrderItem):

    __product_id: int
    __product_name: str
    __product_price: Decimal
    __product_num: int
    __product_sub_total: Decimal

    def __init__(self, id: int, name: str, price: Decimal, num: int = 0, sub_total: Decimal = Decimal(0.00)) -> None:
        self.__product_id = id
        self.__product_name = name
        self.__product_price = price
        self.__product_num = num
        self.__product_sub_total = sub_total

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


class OrderEntity(Order):

    __next_order_id: int = 1000

    @staticmethod
    def get_next_order_id() -> int:
        id = OrderEntity.__next_order_id
        OrderEntity.__next_order_id += 1
        return id
    
    def __init__(self,order_total: Decimal, order_items: List[OrderItem]) -> None:
        self.__order_id = OrderEntity.get_next_order_id()
        self.__order_date = datetime.strftime(datetime.now(), date_formate)
        self.__order_items = order_items
        self.__order_total = order_total

    def get_order_id(self) -> int:
        return self.__order_id
    
    def get_order_date(self) -> str:
        return self.__order_date
    
    def get_order_items(self) -> List[OrderItem]:
        return self.__order_items

    def get_order_total(self) -> Decimal:
        return self.__order_total
    

class CustomerEntity(Customer):

    __customer_list: List[Customer]

    @staticmethod
    def init_data_set() -> None:
        CustomerEntity.__customer_list = []
        for i in range(1, 200):
            CustomerEntity.get_customer_list().append(CustomerEntity(i, "customer-" + str(i), Decimal(i * 100)))

    @staticmethod
    def get_customer_list() -> List[Customer]:
        return CustomerEntity.__customer_list
    
    @staticmethod
    def append_customer(name: str, balance: Decimal) -> None:
        CustomerEntity.get_customer_list().append(CustomerEntity(CustomerEntity.__get_next_customer_id(), name, balance))

    @staticmethod
    def edit_customer(id: str, name: str, balance: Decimal) -> None:
        customer = next(filter(lambda item: item.get_customer_id() == id, CustomerEntity.get_customer_list()), None)
        if customer:
            customer.set_customer_name(name)
            customer.set_customer_balance(balance)

    @staticmethod
    def __get_next_customer_id() -> int:
        if len(CustomerEntity.get_customer_list()) == 0:
            return 1
        return max(map(lambda ent: ent.get_customer_id(), CustomerEntity.get_customer_list())) + 1

    def __init__(self, customer_id: int, customer_name: str, customer_balance: Decimal = Decimal(0.00)) -> None:
        self.__customer_id: int = customer_id
        self.__customer_balance: str = customer_balance
        self.__customer_name: Decimal = customer_name
        self.__customer_payment: List[Payment] = []
        self.__customer_order: List[Order] = []

    def get_customer_id(self) -> int:
        return self.__customer_id

    def get_customer_balance(self) -> Decimal:
        return self.__customer_balance

    def get_customer_name(self) -> str:
        return self.__customer_name
    
    def get_customer_order(self) -> List[Order]:
        return self.__customer_order
    
    def get_payment_list(self) -> List[Payment]:
        return self.__customer_payment

    def set_customer_balance(self, value: Decimal) -> None:
        self.__customer_balance = value
    
    def set_customer_name(self, name: str) -> None:
        self.__customer_name = name

    def add_customer_order(self, order_total: Decimal, order_items: List[OrderItem]) -> None:
        self.get_customer_order().append(OrderEntity(order_total, order_items))
        self.set_customer_balance(self.get_customer_balance() + order_total)
        

    def add_payment(self, amount: Decimal) -> None:
        self.set_customer_balance(self.get_customer_balance() - amount)
        self.get_payment_list().append(PaymentEntity(amount))
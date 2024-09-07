from decimal import Decimal
from typing import List
from abstract_entity import *
import datetime

date_formate = "%d/%m/%Y %H:%M:%S" 

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

    def get_customer_id(self) -> int:
        return self.__customer_id

    def get_customer_balance(self) -> Decimal:
        return self.__customer_balance

    def get_customer_name(self) -> str:
        return self.__customer_name
    
    def get_payment_list(self) -> List[Payment]:
        return self.__customer_payment

    def set_customer_balance(self, value: Decimal) -> None:
        self.__customer_balance = value
    
    def set_customer_name(self, name: str) -> None:
        self.__customer_name = name
    
    def add_customer_entity(self, balance: Decimal) -> None:
        self.set_customer_balance(self.get_customer_balance() + balance)

    def add_payment(self, amount: Decimal) -> None:
        self.set_customer_balance(self.get_customer_balance() - amount)
        self.get_payment_list().append(PaymentEntity(amount))
        

class PaymentEntity(Payment):

    def __init__(self, payment_amount: Decimal) -> None:
        self.__payment_amount = payment_amount
        self.__payment_date = datetime.strftime(datetime.now(), date_formate)

    def get_payment_amount(self) -> Decimal:
        return  self.__payment_amount
    
    def get_payment_date(self) -> str:
        return self.__payment_date
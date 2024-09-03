from customer import CustomerEntity
from product import ProductEntity
from page import Page
from typing import List
from decimal import Decimal
from reactivex import operators, Observable
import reactivex
from abstract_interface import *

CustomerEntity.init_data_set()
ProductEntity.init_data_set()

def list_all_customers() -> Observable[List[Customer]]:
    return reactivex.of(CustomerEntity.get_customer_list())

def page_all_customers(page_num: int, page_size: int) -> Observable[Page[Customer]]:
    list = CustomerEntity.get_customer_list()
    return reactivex.from_iterable(list).pipe(
        operators.skip(page_size * page_num),
        operators.take(page_size),
        operators.to_iterable(),
        operators.map(lambda set: Page(len(list), set))
    )

def add_customer(name: str, balance: Decimal) -> Observable[str]:
    CustomerEntity.append_customer(name, balance)
    return reactivex.create(lambda obj, _: obj.on_next("success"))

def edit_customer(id: int, name: str, balance: Decimal) -> Observable[str]:
    CustomerEntity.edit_customer(id, name, balance)
    return reactivex.create(lambda obj, _: obj.on_next("success"))

def list_all_products(page_num: int, page_size: int) -> Observable[Page[Product]]:
    list = ProductEntity.get_product_list()
    return reactivex.from_iterable(list).pipe(
        operators.skip(page_size * page_num),
        operators.take(page_size),
        operators.to_iterable(),
        operators.map(lambda set: Page(len(list), set))
    )

def add_product(name: str, balance: Decimal) -> Observable[str]:
    ProductEntity.append_product(name, balance)
    return reactivex.create(lambda obj, _: obj.on_next("success"))

def edit_product(id: int, name: str, price: Decimal) -> Observable[str]:
    ProductEntity.edit_product(id, name, price)
    return reactivex.create(lambda obj, _: obj.on_next("success"))
from customer import CustomerEntity
from product import ProductEntity
from page import Page
from typing import List
from decimal import Decimal
from reactivex import operators, Observable
import reactivex
from abstract_entity import *
from view_model import *

CustomerEntity.init_data_set()
ProductEntity.init_data_set()

def all_customers() -> Observable[List[CustomerViewEntity]]:
    return reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
        operators.map(lambda item: CustomerViewEntity(item.get_customer_id(), item.get_customer_name(), item.get_customer_balance())),
        operators.to_iterable()
    )

def page_customers(page_num: int, page_size: int) -> Observable[Page[CustomerViewEntity]]:
    list = CustomerEntity.get_customer_list()
    return reactivex.from_iterable(list).pipe(
        operators.skip(page_size * page_num),
        operators.take(page_size),
        operators.map(lambda item: CustomerViewEntity(item.get_customer_id(), item.get_customer_name(), item.get_customer_balance())),
        operators.to_iterable(),
        operators.map(lambda set: Page(len(list), set))
    )

def add_customer(entity: CustomerAddEntity) -> Observable[str]:
    CustomerEntity.append_customer(entity.get_customer_name(), entity.get_customer_balance())
    return reactivex.create(lambda obj, _: obj.on_next("success"))

def edit_customer(entity: CustomerEditEntity) -> Observable[str]:
    CustomerEntity.edit_customer(entity.get_customer_id(), entity.get_customer_name(), entity.get_customer_balance())
    return reactivex.create(lambda obj, _: obj.on_next("success"))

def all_products() -> Observable[List[ProductViewEntity]]:
    return reactivex.from_iterable(ProductEntity.get_product_list()).pipe(
        operators.map(lambda item: ProductViewEntity(item.get_product_id(), item.get_product_name(), item.get_product_price())),
        operators.to_iterable()
    )

def page_products(page_num: int, page_size: int) -> Observable[Page[ProductViewEntity]]:
    list = ProductEntity.get_product_list()
    return reactivex.from_iterable(list).pipe(
        operators.skip(page_size * page_num),
        operators.take(page_size),
        operators.map(lambda item: ProductViewEntity(item.get_product_id(), item.get_product_name(), item.get_product_price())),
        operators.to_iterable(),
        operators.map(lambda set: Page(len(list), set))
    )

def add_product(entity: ProductAddEntity) -> Observable[str]:
    ProductEntity.append_product(entity.get_product_name(), entity.get_product_price())
    return reactivex.create(lambda obj, _: obj.on_next("success"))

def edit_product(entity: ProductViewEntity) -> Observable[str]:
    ProductEntity.edit_product(entity.get_product_id(), entity.get_product_name(), entity.get_product_price())
    return reactivex.create(lambda obj, _: obj.on_next("success"))
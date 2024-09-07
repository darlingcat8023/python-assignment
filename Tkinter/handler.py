from model import *
from page import Page
from typing import List
from reactivex import operators, Observable
import reactivex
from Tkinter.abstract_model import *
from view_model import *

CustomerEntity.init_data_set()
ProductEntity.init_data_set()

def all_customers() -> Observable[List[CustomerViewEntity]]:
    return reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
        operators.map(lambda item: CustomerViewEntity(item.get_customer_id(), item.get_customer_name(), item.get_customer_balance())),
        operators.to_iterable()
    )

def page_customers(pattern: CustomerListFilterEntity, page_num: int, page_size: int) -> Observable[Page[CustomerViewEntity]]:
    return reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
        operators.filter(lambda item: item.get_customer_name().lower().startswith(pattern.get_customer_name()) if pattern.get_customer_name() is not None and len(pattern.get_customer_name()) > 0 else True),
        operators.count(),
        operators.flat_map(lambda count: reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
            operators.filter(lambda item: item.get_customer_name().lower().startswith(pattern.get_customer_name()) if pattern.get_customer_name() is not None and len(pattern.get_customer_name()) > 0 else True),
            operators.skip(page_size * page_num),
            operators.take(page_size),
            operators.map(lambda item: CustomerViewEntity(item.get_customer_id(), item.get_customer_name(), item.get_customer_balance())),
            operators.to_iterable(),
            operators.map(lambda set: Page(count, set))
        ))
    )

def customer_detail(customer_id: int) -> Observable[CustomerViewEntity]:
    return reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
        operators.filter(lambda item: item.get_customer_id() == customer_id),
        operators.map(lambda item: CustomerViewEntity(item.get_customer_id(), item.get_customer_name(), item.get_customer_balance()))
    )

def add_customer(entity: CustomerAddEntity) -> Observable[str]:
    CustomerEntity.append_customer(entity.get_customer_name(), entity.get_customer_balance())
    return reactivex.of("success")

def edit_customer(entity: CustomerEditEntity) -> Observable[str]:
    CustomerEntity.edit_customer(entity.get_customer_id(), entity.get_customer_name(), entity.get_customer_balance())
    return reactivex.of("success")

def all_products() -> Observable[List[ProductViewEntity]]:
    return reactivex.from_iterable(ProductEntity.get_product_list()).pipe(
        operators.map(lambda item: ProductViewEntity(item.get_product_id(), item.get_product_name(), item.get_product_price())),
        operators.to_iterable()
    )

def page_products(pattern: ProductListFilterEntity, page_num: int, page_size: int) -> Observable[Page[ProductViewEntity]]:
    return reactivex.from_iterable(ProductEntity.get_product_list()).pipe(
        operators.filter(lambda item: item.get_product_name().lower().startswith(pattern.get_product_name()) if pattern.get_product_name() is not None and len(pattern.get_product_name()) > 0 else True),
        operators.count(),
        operators.flat_map(lambda count: reactivex.from_iterable(ProductEntity.get_product_list()).pipe(
            operators.filter(lambda item: item.get_product_name().lower().startswith(pattern.get_product_name()) if pattern.get_product_name() is not None and len(pattern.get_product_name()) > 0 else True),
            operators.skip(page_size * page_num),
            operators.take(page_size),
            operators.map(lambda item: ProductViewEntity(item.get_product_id(), item.get_product_name(), item.get_product_price())),
            operators.to_iterable(),
            operators.map(lambda set: Page(count, set))
        ))
    )

def add_product(entity: ProductAddEntity) -> Observable[str]:
    ProductEntity.append_product(entity.get_product_name(), entity.get_product_price())
    return reactivex.of("success")

def edit_product(entity: ProductViewEntity) -> Observable[str]:
    ProductEntity.edit_product(entity.get_product_id(), entity.get_product_name(), entity.get_product_price())
    return reactivex.of("success")

def create_new_order(entity: OrderCreateEntity) -> Observable[str]:
    return reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
        operators.filter(lambda customer: customer.get_customer_id() == entity.get_customer().get_customer_id()),
        operators.do_action(lambda customer: customer.add_customer_entity(entity.get_order_price())),
        operators.map(lambda _: "success")
    )

def create_new_payment(entity: PaymentCreateEntity) -> Observable[str]:
    return reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
        operators.filter(lambda customer: customer.get_customer_id() == entity.get_customer_id()),
        operators.do_action(lambda customer: customer.add_payment(entity.get_payment_amount())),
        operators.map(lambda _: "success")
    )
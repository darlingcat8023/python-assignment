from model import *
from page import Page
from typing import List
from reactivex import operators, Observable
import reactivex
from abstract_model import *
from view_model import *
from typing import *

class CompanyHanlder:

    def __init__(self) -> None:
        CustomerEntity.init_data_set()
        ProductEntity.init_data_set()

    def all_customers(self) -> Observable[List[CustomerViewEntity]]:
        return reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
            operators.map(lambda item: CustomerViewEntity(item.get_customer_id(), item.get_customer_name(), item.get_customer_balance())),
            operators.to_iterable()
        )

    def page_customers(self, pattern: CustomerListFilterEntity, page_num: int, page_size: int) -> Observable[Page[CustomerViewEntity]]:
        return reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
            operators.filter(lambda item: item.get_customer_name().lower().startswith(pattern.get_customer_name().lower()) if pattern.get_customer_name() is not None and len(pattern.get_customer_name()) > 0 else True),
            operators.count(),
            operators.flat_map(lambda count: reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
                operators.filter(lambda item: item.get_customer_name().lower().startswith(pattern.get_customer_name().lower()) if pattern.get_customer_name() is not None and len(pattern.get_customer_name()) > 0 else True),
                operators.skip(page_size * page_num),
                operators.take(page_size),
                operators.map(lambda item: CustomerViewEntity(item.get_customer_id(), item.get_customer_name(), item.get_customer_balance())),
                operators.to_iterable(),
                operators.map(lambda set: Page(count, set))
            ))
        )

    def customer_detail(self, customer_id: int) -> Observable[CustomerViewEntity]:
        return reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
            operators.filter(lambda item: item.get_customer_id() == customer_id),
            operators.map(lambda item: CustomerViewEntity(item.get_customer_id(), item.get_customer_name(), item.get_customer_balance()))
        )

    def add_customer(self, entity: CustomerAddEntity) -> Observable[str]:
        CustomerEntity.append_customer(entity.get_customer_name(), entity.get_customer_balance())
        return reactivex.of("success")

    def edit_customer(self, entity: CustomerEditEntity) -> Observable[str]:
        CustomerEntity.edit_customer(entity.get_customer_id(), entity.get_customer_name(), entity.get_customer_balance())
        return reactivex.of("success")

    def all_products(self) -> Observable[List[ProductViewEntity]]:
        return reactivex.from_iterable(ProductEntity.get_product_list()).pipe(
            operators.map(lambda item: ProductViewEntity(item.get_product_id(), item.get_product_name(), item.get_product_price())),
            operators.to_iterable()
        )

    def page_products(self, pattern: ProductListFilterEntity, page_num: int, page_size: int) -> Observable[Page[ProductViewEntity]]:
        return reactivex.from_iterable(ProductEntity.get_product_list()).pipe(
            operators.filter(lambda item: item.get_product_name().lower().startswith(pattern.get_product_name().lower()) if pattern.get_product_name() is not None and len(pattern.get_product_name()) > 0 else True),
            operators.count(),
            operators.flat_map(lambda count: reactivex.from_iterable(ProductEntity.get_product_list()).pipe(
                operators.filter(lambda item: item.get_product_name().lower().startswith(pattern.get_product_name().lower()) if pattern.get_product_name() is not None and len(pattern.get_product_name()) > 0 else True),
                operators.skip(page_size * page_num),
                operators.take(page_size),
                operators.map(lambda item: ProductViewEntity(item.get_product_id(), item.get_product_name(), item.get_product_price())),
                operators.to_iterable(),
                operators.map(lambda set: Page(count, set))
            ))
        )

    def add_product(self, entity: ProductAddEntity) -> Observable[str]:
        ProductEntity.append_product(entity.get_product_name(), entity.get_product_price())
        return reactivex.of("success")

    def edit_product(self, entity: ProductViewEntity) -> Observable[str]:
        ProductEntity.edit_product(entity.get_product_id(), entity.get_product_name(), entity.get_product_price())
        return reactivex.of("success")

    def create_new_order(self, entity: OrderCreateEntity) -> Observable[str]:
        return reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
            operators.filter(lambda customer: customer.get_customer_id() == entity.get_customer().get_customer_id()),
            operators.do_action(lambda customer: customer.add_customer_order(entity.get_order_price(), list(map(lambda item: OrderItemEntity(item.get_product_id(), item.get_product_name(), item.get_product_price(), item.get_product_num(), item.get_product_sub_total()), entity.get_order_items())))),
            operators.map(lambda _: "success")
        )

    def create_new_payment(self, entity: PaymentCreateEntity) -> Observable[str]:
        return reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
            operators.filter(lambda customer: customer.get_customer_id() == entity.get_customer_id()),
            operators.do_action(lambda customer: customer.add_payment(entity.get_payment_amount())),
            operators.map(lambda _: "success")
        )

    def page_payments(self, pattern: CustomerListFilterEntity, page_num: int, page_size: int) -> Observable[Page[PaymentViewEneity]]:
        return reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
            operators.filter(lambda item: item.get_customer_name().lower().startswith(pattern.get_customer_name().lower()) if pattern.get_customer_name() is not None and len(pattern.get_customer_name()) > 0 else True),
            operators.reduce(lambda count, item: count + len(item.get_payment_list()), 0),
            operators.flat_map(lambda count: reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
                operators.filter(lambda item: item.get_customer_name().lower().startswith(pattern.get_customer_name().lower()) if pattern.get_customer_name() is not None and len(pattern.get_customer_name()) > 0 else True),
                operators.flat_map(lambda item: reactivex.from_iterable(item.get_payment_list()).pipe(
                    operators.map(lambda pay: PaymentViewEneity(item.get_customer_id(), item.get_customer_name(), pay.get_payment_amount(), pay.get_payment_date()))
                )),
                operators.skip(page_size * page_num),
                operators.take(page_size),
                operators.to_iterable(),
                operators.map(lambda set: Page(count, set))
            ))
        )

    def page_orders(self, pattern: CustomerListFilterEntity, page_num: int, page_size: int) -> Observable[Page[OrderViewEntity]]:
        return reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
            operators.filter(lambda item: item.get_customer_name().lower().startswith(pattern.get_customer_name().lower()) if pattern.get_customer_name() is not None and len(pattern.get_customer_name()) > 0 else True),
            operators.reduce(lambda count, item: count + len(item.get_customer_order()), 0),
            operators.flat_map(lambda count: reactivex.from_iterable(CustomerEntity.get_customer_list()).pipe(
                operators.filter(lambda item: item.get_customer_name().lower().startswith(pattern.get_customer_name().lower()) if pattern.get_customer_name() is not None and len(pattern.get_customer_name()) > 0 else True),
                operators.flat_map(lambda item: reactivex.from_iterable(item.get_customer_order()).pipe(
                    operators.map(lambda order: OrderViewEntity(item.get_customer_id(), item.get_customer_name(), order.get_order_id(), order.get_order_date(), list(map(lambda o: OrderCreateEntity.OrderProductEntity(o.get_product_id(), o.get_product_name(), o.get_product_price(), o.get_product_num(), o.get_product_sub_total()) ,order.get_order_items())), order.get_order_total()))
                )),
                operators.skip(page_size * page_num),
                operators.take(page_size),
                operators.to_iterable(),
                operators.map(lambda set: Page(count, set))
            ))
        )
    
class HandlerRegstation:

    __company_handler: CompanyHanlder = CompanyHanlder()

    @staticmethod
    def get_company_hanlder() -> CompanyHanlder:
        return HandlerRegstation.__company_handler
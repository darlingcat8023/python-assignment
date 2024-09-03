from decimal import Decimal
from typing import List
from abstract_interface import Product

class ProductEntity(Product):
    
    __product_list: List[Product]

    @staticmethod
    def init_data_set() -> None:
        ProductEntity.__product_list = []

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
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Page(Generic[T]):

    __total: int
    __data: List[T]

    def __init__(self, total: int, data: List[T]) -> None:
        super().__init__()
        self.__total = total
        self.__data = data

    def get_total(self) -> int:
        return self.__total
    
    def get_data(self) -> List[T]:
        return self.__data
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Page(Generic[T]):

    def __init__(self, total: int, data: List[T]) -> None:
        super().__init__()
        self.__total: int = total
        self.__data: List[T] = data

    def get_total(self) -> int:
        return self.__total
    
    def get_data(self) -> List[T]:
        return self.__data
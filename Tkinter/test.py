from tkinter import *
from tkinter import Event, Frame, ttk, font
from typing import TypeVar, List, Callable, Generic, Tuple, Dict
from reactivex import operators, Observable
from reactivex.subject import *
import abc, handler, page, math, reactivex
from decimal import Decimal
from view_model import *
from datetime import datetime, timedelta  


class BaseSpinBox(Spinbox):

    __selected_subject: Subject

    def __init__(self, parent_frame: Frame) -> None:
        super().__init__(parent_frame, from_ = 1, to = 100)
        self.__selected_subject = Subject()
        int_var = IntVar()
        int_var.trace_add("write", lambda x, y, z: self.__selected_subject.on_next(int_var.get()))
        self.config(textvariable = int_var)
        self.pack(side = RIGHT, padx = 10, pady = 10, anchor = NW)

    def get_selected_subject(self) -> Subject:
        return self.__selected_subject


# root = Tk()
# root.title("Spinbox with IntVar Example")
# spin = BaseSpinBox(root)
# spin.get_selected_subject().subscribe(lambda i: print(i))
# root.mainloop()


print(datetime.strftime(datetime.now(), "%d/%m/%Y %H:%M:%S" ))
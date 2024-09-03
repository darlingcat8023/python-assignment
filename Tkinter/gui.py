from tkinter import *
from tkinter import Event, Frame, ttk
from typing import TypeVar, List, Callable, Generic, Tuple
from reactivex import operators, Observable
from reactivex.subject import *
import abc, handler, page, customer, math, reactivex, abstract_interface
from decimal import Decimal
from base_gui_compnent import *

class MethodInvoker:

    T = TypeVar('T')

    @staticmethod
    def execute(function: Callable[[None], T]) -> T:
        try:
            return function()
        except Exception:
            return None

## Main GUI, entrance
class GUI(Frame):

    def __init__(self, root: Tk, pixel: str, title: str) -> None:
        super().__init__(root)
        root.geometry(pixel)
        root.title(title)
        menu_frame = BaseFrame(root, width = root.winfo_width() / 4)
        menu_frame.set_frame_style(LEFT, Y, False)
        menu_frame.display_frame()
        compnent_frame = BaseFrame(root, width = root.winfo_width() * 3 / 4)
        compnent_frame.set_frame_style(RIGHT, BOTH, True)
        compnent_frame.display_frame()
        frame_holder = FrameHolder(compnent_frame)
        self.__render_menu(menu_frame, frame_holder)

    def __render_menu(self, menu_frame: BaseFrame, frame_holder: FrameHolder) -> None:
        ReactiveMainButton(menu_frame, "Main", frame_holder, Subject())
        ReactiveListCustomerButton(menu_frame, "List All Customers", frame_holder, Subject())
        ReactiveListProductButton(menu_frame, "List All Products", frame_holder, Subject())
        ReactiveCreateNewOrderButton(menu_frame, "Create New Order", frame_holder, Subject())
        

class ReactiveMainButton(AbstractMenuButton):

    def __init__(self, menu_frame: BaseFrame, name: str, frame_holder: FrameHolder, subject: Subject) -> None:      
        super().__init__(menu_frame, name, frame_holder, subject)

    def display_button(self) -> None:
        self.pack(side = TOP, fill = X, padx = 10, pady = 10)

    def render_compnent(self, frame: BaseFrame) -> None:
        welcome_label = Label(frame, text = "Welcome to Lincoln Office Supplies!")
        welcome_label.pack(expand = True)

    
class ReactiveListCustomerButton(AbstractMenuButton):

    def __init__(self, menu_frame: BaseFrame, name: str, frame_holder: FrameHolder, subject: Subject) -> None:
        super().__init__(menu_frame, name, frame_holder, subject)

    def display_button(self) -> None:
        self.pack(side = TOP, fill = X, padx = 10, pady = 10)

    def render_compnent(self, frame: BaseFrame) -> None:
        table = PageableTreeTable[abstract_interface.Customer](frame,
            lambda page, page_size: handler.page_all_customers(page, page_size),
            lambda table, data: table.insert("", "end", values = (data.get_customer_id(), data.get_customer_name(), data.get_customer_balance()))
        )
        table.set_column_title(['Customer Id', 'Customer Name', 'Customer Balance'])
        ReactiveAddCustomerButton(frame, "Add Customer", self.get_frame_holder(), Subject(), table.get_load_subject())
        self.get_button_subject().subscribe(table.get_load_subject())
        edit_button = ReactiveEditCustomerButton(frame, "Edit Customer", self.get_frame_holder(), Subject(), table.get_load_subject())
        self.get_button_subject().subscribe(lambda _: edit_button.hide_button())
        table.get_load_subject().subscribe(lambda _: edit_button.hide_button())
        table.get_selected_subject().pipe(
            operators.do_action(lambda item: edit_button.set_data_to_edit(item))
        ).subscribe(lambda _: edit_button.display_button())


class ReactiveListProductButton(AbstractMenuButton):
    
    def __init__(self, menu_frame: BaseFrame, name: str, frame_holder: FrameHolder, subject: Subject) -> None:
        super().__init__(menu_frame, name, frame_holder, subject)

    def display_button(self) -> None:
        self.pack(side = TOP, fill = X, padx = 10, pady = 10)

    def render_compnent(self, frame: BaseFrame) -> None:
        table = PageableTreeTable[abstract_interface.Product](frame,
            lambda page, page_size: handler.list_all_products(page, page_size),
            lambda table, data: table.insert("", "end", values = (data.get_product_id(), data.get_product_name(), data.get_product_price()))
        )
        table.set_column_title(['Product Id', 'Product Name', 'Product Price'])
        ReactiveAddProductButton(frame, "Add Product", self.get_frame_holder(), Subject(), table.get_load_subject())
        self.get_button_subject().subscribe(table.get_load_subject())
        edit_button = ReactiveEditProductButton(frame, "Edit Product", self.get_frame_holder(), Subject(), table.get_load_subject())
        self.get_button_subject().subscribe(lambda _: edit_button.hide_button())
        table.get_load_subject().subscribe(lambda _: edit_button.hide_button())
        table.get_selected_subject().pipe(
            operators.do_action(lambda item: edit_button.set_data_to_edit(item))
        ).subscribe(lambda _: edit_button.display_button())


class CreateOrderFrame(BaseFrame):

    class OrderCreateEntity:

        class CustomerEntity:

            __customer_id: int
            __customer_name: str
            __customer_balance: Decimal

            def __init__(self, id: int, name: str, balance: Decimal) -> None:
                self.__customer_id = id
                self.__customer_name = name
                self.__customer_balance = balance

            def get_customer_id(self) -> int:
                return self.__customer_id
            
            def get_customer_name(self) -> str:
                return self.__customer_name
            
            def get_customer_balance(self) -> Decimal:
                return self.__customer_balance
            
            def print_on_text_box(self, text_box: BaseTextBox) -> None:
                text_box.replace_text(f"Customer Id:\t\t{self.get_customer_id()}\nCustomer Name:\t\t{self.get_customer_name()}\nCustomer Balance:\t\t{self.get_customer_balance()}")

        __customer: CustomerEntity
        
        def __init__(self) -> None:
            self.__customer = None

        def get_customer(self) -> CustomerEntity:
            return self.__customer

        def set_customer(self, id: int, name: str, balance: Decimal) -> None:
            self.__customer = CreateOrderFrame.OrderCreateEntity.CustomerEntity(id, name, balance)

    def __init__(self, frame_holder: FrameHolder) -> None:
        super().__init__(frame_holder.get_base_frame())
        self.__frame_subject = Subject()
        self.draw_compnent(frame_holder)

    def get_frame_subject(self) -> Subject:
        return self.__frame_subject

    def draw_compnent(self, frame_holder: FrameHolder) -> None:
        entity = CreateOrderFrame.OrderCreateEntity()
        self.render_customer_select_area(entity)
        self.render_product_select_area(entity)
        

    def render_customer_select_area(self, entity: OrderCreateEntity) -> None:
        customer_frame = BaseFrame(self)
        customer_frame.set_frame_style(TOP, BOTH, True)
        customer_select_frame = BaseFrame(customer_frame)
        customer_select_frame.set_frame_style(LEFT, BOTH, True)
        customer_show_frame = BaseFrame(customer_frame)
        customer_show_frame.set_frame_style(LEFT, BOTH, True)
        customer_frame.display_frame()
        customer_select_frame.display_frame()
        customer_show_frame.display_frame()

        label = Label(customer_select_frame, text = "Please select a customer :")
        label.pack(side = TOP, padx = 10, pady = 10, anchor = W)
        customer_select_box = PrefixSearchCombobox[abstract_interface.Customer](customer_select_frame, lambda: handler.list_all_customers(), lambda c: "{0}({1})".format(c.get_customer_name(), c.get_customer_id()))
        customer_select_box.get_load_subject().on_next(None)
        customer_text_box = BaseTextBox(customer_show_frame)
        customer_select_box.get_selected_subject().pipe(
            operators.do_action(lambda item: entity.set_customer(item.get_customer_id(), item.get_customer_name(), item.get_customer_balance())),
            operators.map(lambda item: entity.get_customer())
        ).subscribe(lambda item: item.print_on_text_box(customer_text_box))

    def render_product_select_area(self, entity: OrderCreateEntity) -> None:
        product_frame = BaseFrame(self)
        product_frame.set_frame_style(TOP, BOTH, True)
        product_select_frame = BaseFrame(product_frame)
        product_select_frame.set_frame_style(LEFT, BOTH, True)
        product_show_frame = BaseFrame(product_frame)
        product_show_frame.set_frame_style(LEFT, BOTH, True)
        product_frame.display_frame()
        product_select_frame.display_frame()
        product_show_frame.display_frame()

        label = Label(product_select_frame, text = "Please select a product :")
        label.pack(side = TOP, padx = 10, pady = 10, anchor = W)
        product_select_box = PrefixSearchCombobox[abstract_interface.Product](product_select_frame, lambda: handler.list_all_customers(), lambda c: "{0}({1})".format(c.get_customer_name(), c.get_customer_id()))
        product_select_box.get_load_subject().on_next(None)
        product_text_box = BaseTextBox(product_show_frame)

class ReactiveCreateNewOrderButton(AbstractMenuButton):
    
    def __init__(self, menu_frame: BaseFrame, name: str, frame_holder: FrameHolder, subject: Subject) -> None:
        super().__init__(menu_frame, name, frame_holder, subject)

    def display_button(self) -> None:
        self.pack(side = TOP, fill = X, padx = 10, pady = 10)

    def get_compnent_frame(self) -> BaseFrame:
        new_frame = CreateOrderFrame(self.get_frame_holder())
        new_frame.set_frame_style(RIGHT, BOTH, True)
        return new_frame

    def render_compnent(self, frame: BaseFrame) -> None:
        pass
        

class AddCustomerFrame(BaseFrame):

    class CustomerAddEntity:

        __customer_name: str
        __customer_balance: Decimal

        def __init__(self) -> None:
            self.__customer_name = None
            self.__customer_balance = None
    
        def set_customer_name(self, customer_name: str) -> None:
            self.__customer_name = customer_name

        def set_customer_balance(self, customer_balance: Decimal) -> None:
            self.__customer_balance = customer_balance

        def get_customer_name(self) -> str:
            return self.__customer_name
    
        def get_customer_balance(self) -> Decimal:
            return self.__customer_balance

        def is_ready_for_submit(self, customer_name_entry: LabelEntryPair, customer_balance_entry: LabelEntryPair) -> bool:
            if self.get_customer_name() is None or len(self.get_customer_name()) == 0:
                customer_name_entry.set_tip("Invalid Customer Name input")
                return False
            if self.get_customer_balance() is None:
                customer_balance_entry.set_tip("Invalid Customer Balance input")
                return False
            return True

    def __init__(self, frame_holder: FrameHolder, callback: Subject, width: int = -1) -> None:
        super().__init__(frame_holder.get_base_frame(), width)
        self.draw_compnent(frame_holder, callback)

    def draw_compnent(self, frame_holder: FrameHolder, callback: Subject) -> None:
        entity = AddCustomerFrame.CustomerAddEntity()
        customer_name_entry = LabelEntryPair(self, "Customer Name:")
        customer_name_entry.get_input_subject().pipe(
            operators.do_action(lambda _: customer_name_entry.set_tip(""))
        ).subscribe(lambda ipt: entity.set_customer_name(ipt))
        customer_balance_entry = LabelEntryPair(self, "Customer Balance:")
        customer_balance_entry.get_input_subject().pipe(
            operators.do_action(lambda _: customer_balance_entry.set_tip(""))
        ).subscribe(
            on_next = lambda ipt: entity.set_customer_balance(Decimal(ipt)),
            on_error = lambda error: print(f"{error}")
        )
        submit_button = OptionButton(self, "Add Submit", Subject())
        cancel_button = OptionButton(self, "Add Cancel", Subject())
        submit_button.get_button_subject().pipe(
            operators.map(lambda _: entity),
            operators.filter(lambda entity: entity.is_ready_for_submit(customer_name_entry, customer_balance_entry)),
            operators.flat_map(lambda entity: handler.add_customer(entity.get_customer_name(), entity.get_customer_balance())),
        ).subscribe(cancel_button.get_button_subject())
        cancel_button.get_button_subject().pipe(
            operators.do_action(lambda _: frame_holder.revert_frame(destory = True))
        ).subscribe(callback)


class ReactiveAddCustomerButton(AbstractMenuButton):

    __callback_subject: Subject

    def __init__(self, frame: BaseFrame, name: str, frame_holder: FrameHolder, subject: Subject, callback: Subject) -> None:
        super().__init__(frame, name, frame_holder, subject)
        self.__callback_subject = callback

    def display_button(self) -> None:
        self.pack(side = RIGHT, padx = 10, pady = 10)
    
    def get_compnent_frame(self) -> BaseFrame:
        new_frame = AddCustomerFrame(self.get_frame_holder(),  self.__callback_subject)
        new_frame.set_frame_style(RIGHT, BOTH, True)
        return new_frame

    def render_compnent(self, frame: BaseFrame) -> None:
        pass


class EditCustomerFrame(BaseFrame):

    class CustomerEditEntity:

        __customer_id: int
        __customer_name:str
        __customer_balance: Decimal

        def __init__(self, id: int, name: str, balance: Decimal) -> None:
            self.__customer_id = id
            self.__customer_name = name
            self.__customer_balance = balance
    
        def set_customer_name(self, customer_name: str) -> None:
            self.__customer_name = customer_name

        def set_customer_balance(self, customer_balance: Decimal) -> None:
            self.__customer_balance = customer_balance

        def get_customer_id(self) -> int:
            return self.__customer_id

        def get_customer_name(self) -> str:
            return self.__customer_name
    
        def get_customer_balance(self) -> Decimal:
            return self.__customer_balance

        def is_ready_for_submit(self, customer_name_entry: LabelEntryPair, customer_balance_entry: LabelEntryPair) -> bool:
            if self.get_customer_name() is None or len(self.get_customer_name()) == 0:
                customer_name_entry.set_tip("Invalid Customer Name input")
                return False
            if self.get_customer_balance() is None:
                customer_balance_entry.set_tip("Invalid Customer Balance input")
                return False
            return True

    def __init__(self, frame_holder: FrameHolder, data_tuple: Tuple, callback: Subject, width: int = -1) -> None:
        super().__init__(frame_holder.get_base_frame(), width)
        self.draw_compnent(frame_holder, data_tuple, callback)

    def draw_compnent(self, frame_holder: FrameHolder, data_tuple: Tuple, callback: Subject) -> None:
        entity = EditCustomerFrame.CustomerEditEntity(int(data_tuple[0]), data_tuple[1], Decimal(data_tuple[2]))
        LabelEntryPair(self, "Customer ID:", default_value = entity.get_customer_id(), editable = False)
        customer_name_entry = LabelEntryPair(self, "Customer Name:", default_value = entity.get_customer_name())
        customer_name_entry.get_input_subject().pipe(
            operators.do_action(lambda _: customer_name_entry.set_tip(""))
        ).subscribe(lambda ipt: entity.set_customer_name(ipt))
        customer_balance_entry = LabelEntryPair(self, "Customer Balance:", default_value = entity.get_customer_balance())
        customer_balance_entry.get_input_subject().pipe(
            operators.do_action(lambda _: customer_balance_entry.set_tip(""))
        ).subscribe(
            on_next = lambda ipt: entity.set_customer_balance(MethodInvoker.execute(lambda: Decimal(ipt))),
            on_error = lambda error: print(f"{error}")
        )
        submit_button = OptionButton(self, "Edit Submit", Subject())
        cancel_button = OptionButton(self, "Edit Cancel", Subject())
        submit_button.get_button_subject().pipe(
            operators.map(lambda _: entity),
            operators.filter(lambda entity: entity.is_ready_for_submit(customer_name_entry, customer_balance_entry)),
            operators.flat_map(lambda entity: handler.edit_customer(entity.get_customer_id(), entity.get_customer_name(), entity.get_customer_balance())),
        ).subscribe(cancel_button.get_button_subject())
        cancel_button.get_button_subject().pipe(
            operators.do_action(lambda _: frame_holder.revert_frame(destory = True))
        ).subscribe(callback)


class ReactiveEditCustomerButton(AbstractMenuButton):

    __callback_subject: Subject
    __customer_tuple: Tuple[str]

    def __init__(self, parent: BaseFrame, name: str, frame_holder: FrameHolder, subject: Subject, callback: Subject) -> None:
        super().__init__(parent, name, frame_holder, subject)
        self.__callback_subject = callback

    def display_button(self) -> None:
        self.pack(side = RIGHT, padx = 10, pady = 10)
    
    def get_compnent_frame(self) -> BaseFrame:
        new_frame = EditCustomerFrame(self.get_frame_holder(), self.__customer_tuple, self.__callback_subject)
        new_frame.set_frame_style(RIGHT, BOTH, True)
        return new_frame
    
    def set_data_to_edit(self, data_tuple: Tuple[str]) -> None:
        self.__customer_tuple = data_tuple

    def render_compnent(self, frame: BaseFrame) -> None:
        pass


class AddProductFrame(BaseFrame):

    class ProductAddEntity:

        __product_name:str
        __product_price: Decimal

        def __init__(self) -> None:
            self.__product_name = None
            self.__product_price = None
    
        def set_product_name(self, product_name: str) -> None:
            self.__product_name = product_name

        def set_product_price(self, product_price: Decimal) -> None:
            self.__product_price = product_price

        def get_product_name(self) -> str:
            return self.__product_name
    
        def get_product_price(self) -> Decimal:
            return self.__product_price

        def is_ready_for_submit(self, product_name_entry: LabelEntryPair, product_price_entry: LabelEntryPair) -> bool:
            if self.get_product_name() is None or len(self.get_product_name()) == 0:
                product_name_entry.set_tip("Invalid Product Name input")
                return False
            if self.get_product_price() is None:
                product_price_entry.set_tip("Invalid Product Price input")
                return False
            return True

    def __init__(self, frame_holder: FrameHolder, callback: Subject, width: int = -1) -> None:
        super().__init__(frame_holder.get_base_frame(), width)
        self.draw_compnent(frame_holder, callback)

    def draw_compnent(self, frame_holder: FrameHolder, callback: Subject) -> None:
        entity = AddProductFrame.ProductAddEntity()
        product_name_entry = LabelEntryPair(self, "Product Name:")
        product_name_entry.get_input_subject().pipe(
            operators.do_action(lambda _: product_name_entry.set_tip(""))
        ).subscribe(lambda ipt: entity.set_product_name(ipt))
        product_price_entry = LabelEntryPair(self, "Product Balance:")
        product_price_entry.get_input_subject().pipe(
            operators.do_action(lambda _: product_price_entry.set_tip(""))
        ).subscribe(
            on_next = lambda ipt: entity.set_product_price(Decimal(ipt)),
            on_error = lambda error: print(f"{error}")
        )
        submit_button = OptionButton(self, "Add Submit", Subject())
        cancel_button = OptionButton(self, "Add Cancel", Subject())
        submit_button.get_button_subject().pipe(
            operators.map(lambda _: entity),
            operators.filter(lambda entity: entity.is_ready_for_submit()),
            operators.flat_map(lambda entity: handler.add_product(entity.get_product_name(), entity.get_product_price())),
        ).subscribe(cancel_button.get_button_subject())
        cancel_button.get_button_subject().pipe(
            operators.do_action(lambda _: frame_holder.revert_frame(destory = True))
        ).subscribe(callback)


class ReactiveAddProductButton(AbstractMenuButton):

    __callback_subject: Subject

    def __init__(self, frame: BaseFrame, name: str, frame_holder: FrameHolder, subject: Subject, callback: Subject) -> None:
        super().__init__(frame, name, frame_holder, subject)
        self.__callback_subject = callback

    def display_button(self) -> None:
        self.pack(side = RIGHT, padx = 10, pady = 10)
    
    def get_compnent_frame(self) -> BaseFrame:
        new_frame = AddProductFrame(self.get_frame_holder(),  self.__callback_subject)
        new_frame.set_frame_style(RIGHT, BOTH, True)
        return new_frame

    def render_compnent(self, frame: BaseFrame) -> None:
        pass

class EditProductFrame(BaseFrame):

    class ProductEditEntity:

        __product_id: int
        __product_name:str
        __product_price: Decimal

        def __init__(self, id: int, name: str, price: Decimal) -> None:
            self.__product_id = id
            self.__product_name = name
            self.__product_price = price
    
        def set_product_name(self, product_name: str) -> None:
            self.__product_name = product_name

        def set_product_price(self, product_price: Decimal) -> None:
            self.__product_price = product_price

        def get_product_id(self) -> int:
            return self.__product_id

        def get_product_name(self) -> str:
            return self.__product_name
    
        def get_product_price(self) -> Decimal:
            return self.__product_price

        def is_ready_for_submit(self, product_name_entry: LabelEntryPair, product_price_entry: LabelEntryPair) -> bool:
            if self.get_product_name() is None or len(self.get_product_name()) == 0:
                product_name_entry.set_tip("Invalid Product Name input")
                return False
            if self.get_product_price() is None:
                product_price_entry.set_tip("Invalid Product Price input")
                return False
            return True
        
    def __init__(self, frame_holder: FrameHolder, data_tuple: Tuple, callback: Subject, width: int = -1) -> None:
        super().__init__(frame_holder.get_base_frame(), width)
        self.draw_compnent(frame_holder, data_tuple, callback)

    def draw_compnent(self, frame_holder: FrameHolder, data_tuple: Tuple, callback: Subject) -> None:
        entity = EditProductFrame.ProductEditEntity(int(data_tuple[0]), data_tuple[1], Decimal(data_tuple[2]))
        LabelEntryPair(self, "Product ID:", default_value = entity.get_product_id(), editable = False)
        product_name_entry = LabelEntryPair(self, "Product Name:", default_value = entity.get_product_name())
        product_name_entry.get_input_subject().pipe(
            operators.do_action(lambda _: product_name_entry.set_tip(""))
        ).subscribe(lambda ipt: entity.set_product_name(ipt))
        product_price_entry = LabelEntryPair(self, "Product Balance:", default_value = entity.get_product_price())
        product_price_entry.get_input_subject().pipe(
            operators.do_action(lambda _: product_price_entry.set_tip(""))
        ).subscribe(
            on_next = lambda ipt: entity.set_product_price(MethodInvoker.execute(lambda: Decimal(ipt))),
            on_error = lambda error: print(f"{error}")
        )
        submit_button = OptionButton(self, "Edit Submit", Subject())
        cancel_button = OptionButton(self, "Edit Cancel", Subject())
        submit_button.get_button_subject().pipe(
            operators.map(lambda _: entity),
            operators.filter(lambda entity: entity.is_ready_for_submit()),
            operators.flat_map(lambda entity: handler.edit_product(entity.get_product_id(), entity.get_product_name(), entity.get_product_price())),
        ).subscribe(cancel_button.get_button_subject())
        cancel_button.get_button_subject().pipe(
            operators.do_action(lambda _: frame_holder.revert_frame(destory = True))
        ).subscribe(callback)


class ReactiveEditProductButton(AbstractMenuButton):

    __callback_subject: Subject
    __product_tuple: Tuple[str]

    def __init__(self, parent: BaseFrame, name: str, frame_holder: FrameHolder, subject: Subject, callback: Subject) -> None:
        super().__init__(parent, name, frame_holder, subject)
        self.__callback_subject = callback

    def display_button(self) -> None:
        self.pack(side = RIGHT, padx = 10, pady = 10)
    
    def get_compnent_frame(self) -> BaseFrame:
        new_frame = EditProductFrame(self.get_frame_holder(), self.__product_tuple, self.__callback_subject)
        new_frame.set_frame_style(RIGHT, BOTH, True)
        return new_frame
    
    def set_data_to_edit(self, data_tuple: Tuple[str]) -> None:
        self.__product_tuple = data_tuple

    def render_compnent(self, frame: BaseFrame) -> None:
        pass    

GUI(Tk(), '1200x800', 'Lincoln Office Supplies').mainloop()

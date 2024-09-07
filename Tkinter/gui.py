from tkinter import *
from tkinter import Event, Frame, ttk
from typing import TypeVar, List, Callable, Generic, Tuple
from reactivex import operators, Observable
from reactivex.subject import *
import abc, handler, page, customer, math, reactivex
from decimal import Decimal
from base_gui_compnent import *
from view_model import *
from page import *

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
        
        entity = CustomerListFilterEntity()
        customer_search= SearchBar(frame, "Customer Name:")

        class Table(PageableTreeTable[CustomerViewEntity]):

            def data_provider(self, page: int, page_size: int) -> Observable[Page[CustomerViewEntity]]:
                return handler.page_customers(entity, page, page_size)
            
            def column_provider(self, data: CustomerViewEntity) -> None:
                self.insert("", "end", values = (data.get_customer_id(), data.get_customer_name(), data.get_customer_balance()))

            def instance_provider(self, tuple: Tuple[str]) -> CustomerViewEntity:
                return CustomerViewEntity(int(tuple[0]), tuple[1], Decimal(tuple[2]))
        
        table = Table(frame, ['Customer Id', 'Customer Name', 'Customer Balance'])
        ReactiveAddCustomerButton(frame, "Add Customer", self.get_frame_holder(), Subject(), table.get_load_subject())
        edit_button = ReactiveEditCustomerButton(frame, "Edit Customer", self.get_frame_holder(), Subject(), table.get_load_subject())

        self.get_button_subject().subscribe(table.get_load_subject())
        self.get_button_subject().subscribe(lambda _: edit_button.hide_button())

        customer_search.get_input_subject().pipe(
            operators.do_action(lambda ipt: entity.set_customer_name(ipt))
        ).subscribe(table.get_load_subject())
        
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

        entity = ProductListFilterEntity()
        product_search = SearchBar(frame, "Product Name:")
        
        class Table(PageableTreeTable[ProductViewEntity]):

            def data_provider(self, page: int, page_size: int) -> Observable[Page[ProductViewEntity]]:
                return handler.page_products(entity, page, page_size)
            
            def column_provider(self, data: ProductViewEntity) -> None:
                return self.insert("", "end", values = (data.get_product_id(), data.get_product_name(), data.get_product_price()))
            
            def instance_provider(self, tuple: Tuple[str]) -> ProductViewEntity:
                return ProductViewEntity(int(tuple[0]), tuple[1], Decimal(tuple[2]))
        
        table = Table(frame, ['Product Id', 'Product Name', 'Product Price'])
        ReactiveAddProductButton(frame, "Add Product", self.get_frame_holder(), Subject(), table.get_load_subject())
        edit_button = ReactiveEditProductButton(frame, "Edit Product", self.get_frame_holder(), Subject(), table.get_load_subject())
        
        self.get_button_subject().subscribe(table.get_load_subject())
        self.get_button_subject().subscribe(lambda _: edit_button.hide_button())

        product_search.get_input_subject().pipe(
            operators.do_action(lambda ipt: entity.set_product_name(ipt))
        ).subscribe(table.get_load_subject())
        
        table.get_load_subject().subscribe(lambda _: edit_button.hide_button())
        table.get_selected_subject().pipe(
            operators.do_action(lambda item: edit_button.set_data_to_edit(item))
        ).subscribe(lambda _: edit_button.display_button())


class CreateOrderFrame(BaseFrame):

    __submit_subject: Subject

    def __init__(self, frame_holder: FrameHolder) -> None:
        super().__init__(frame_holder.get_base_frame())
        self.__submit_subject = Subject()
        self.draw_compnent(frame_holder)

    def get_submit_subject(self) -> Subject:
        return self.__submit_subject

    def draw_compnent(self, frame_holder: FrameHolder) -> None:
        entity = OrderCreateEntity()
        self.render_customer_select_area(entity)
        self.render_product_select_area(entity)
        self.render_option_area(entity)

    def render_customer_select_area(self, entity: OrderCreateEntity) -> None:
        
        customer_frame = BaseFrame(self)
        customer_frame.set_frame_style(TOP, X, False)
        
        customer_select_frame = BaseFrame(customer_frame)
        customer_select_frame.set_frame_style(LEFT, BOTH, True)
        
        customer_show_frame = BaseFrame(customer_frame)
        customer_show_frame.set_frame_style(LEFT, BOTH, True)
        
        customer_frame.display_frame()
        customer_select_frame.display_frame()
        customer_show_frame.display_frame()

        label = Label(customer_select_frame, text = "Please select a customer :")
        label.pack(side = TOP, padx = 10, pady = 10, anchor = W)
        customer_select_box = PrefixSearchCombobox[CustomerViewEntity](customer_select_frame, lambda: handler.all_customers())
        customer_select_box.get_load_subject().on_next(None)
        customer_text_box = BaseTextBox(customer_show_frame)
        
        customer_select_box.get_selected_subject().pipe(
            operators.do_action(lambda item: entity.set_customer(item.get_customer_id(), item.get_customer_name(), item.get_customer_balance())),
            operators.flat_map(lambda item: handler.customer_detail(item.get_customer_id()))
        ).subscribe(lambda item: customer_text_box.replace_text(item.text_print_on_text_box()))

        self.get_submit_subject().pipe(
            operators.do_action(lambda _: customer_select_box.config(state = DISABLED)),
            operators.flat_map(lambda _: handler.customer_detail(entity.get_customer().get_customer_id())),
        ).subscribe(lambda item: customer_text_box.replace_text(item.text_print_on_text_box()))


    def render_product_select_area(self, entity: OrderCreateEntity) -> None:
        
        product_frame = BaseFrame(self)
        product_frame.set_frame_style(TOP, X, False)

        product_select_frame = BaseFrame(product_frame)
        product_select_frame.set_frame_style(LEFT, BOTH, True)
        
        product_select_frame_1 = BaseFrame(product_select_frame)
        product_select_frame_1.set_frame_style(LEFT, BOTH, True)
        
        product_show_frame = BaseFrame(product_frame)
        product_show_frame.set_frame_style(LEFT, BOTH, True)
        
        product_frame.display_frame()
        product_select_frame.display_frame()
        product_select_frame_1.display_frame()
        product_show_frame.display_frame()

        product_label = Label(product_select_frame_1, text = "Please select a product :")
        product_label.pack(side = TOP, padx = 10, pady = 10, anchor = W)
        product_select_box = PrefixSearchCombobox[ProductViewEntity](product_select_frame_1, lambda: handler.all_products())
        product_select_box.get_load_subject().on_next(None)
        product_num_label = Label(product_select_frame_1, text = "Please select quntity :")
        product_num_label.pack(side = TOP, padx = 10, pady = 10, anchor = W)
        spin = BaseSpinBox(product_select_frame_1)
        spin.config(state = DISABLED)
        
        class AddOrderProductButton(AbstractButton):

            def display_button(self) -> None:
                self.pack(side = TOP, padx = 10, pady = 10, anchor = W)
    
        add_button = AddOrderProductButton(product_select_frame_1, "Add To Order", Subject())
        add_button.config(state = DISABLED)
        product_text_box = BaseTextBox(product_show_frame, heigh = 12)

        product_select_box.get_selected_subject().pipe(
            operators.do_action(lambda item: entity.set_temp_entity(item.get_product_id(), item.get_product_name(), item.get_product_price()))
        ).subscribe(lambda item: spin.config(state = NORMAL))

        spin.get_selected_subject().pipe(
            operators.do_action(lambda num: entity.set_temp_num(num))
        ).subscribe(lambda item: add_button.config(state = NORMAL))

        add_button.get_button_subject().pipe(
            operators.map(lambda _: entity),
            operators.do_action(lambda _: entity.confirm_product())
        ).subscribe(lambda entity: product_text_box.replace_text(entity.text_print_on_product_box()))

        self.get_submit_subject().pipe(
            operators.do_action(lambda _: product_select_box.config(state = DISABLED)),
            operators.do_action(lambda _: spin.config(state = DISABLED)),
            operators.do_action(lambda _: add_button.config(state = DISABLED))
        ).subscribe()

    def render_payment_area(self, entity: OrderCreateEntity) -> None:
        payment_frame = BaseFrame(self)
        payment_frame.set_frame_style(TOP, X, False)
    
    def render_option_area(self, entity: OrderCreateEntity) -> None:
        option_frame = BaseFrame(self)
        option_frame.set_frame_style(TOP, BOTH, True)
        option_frame.display_frame()

        class OperateButton(OptionButton):

            def display_button(self) -> None:
                self.pack(side = RIGHT, padx = 10, pady = 10, anchor = SE)
    
        submit_button = OperateButton(option_frame, "Submit", Subject())
        pay_button = OperateButton(option_frame, "Pay", Subject())
        pay_button.config(state = DISABLED)

        submit_button.get_button_subject().pipe(
            operators.filter(lambda _: entity.is_reay_for_submit()),
            operators.flat_map(lambda _: handler.create_new_order(entity)),
            operators.filter(lambda res: res == "success"),
            operators.do_action(lambda _: submit_button.config(state = DISABLED)),
            operators.do_action(lambda _: pay_button.config(state = NORMAL))
        ).subscribe(self.get_submit_subject())



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

    def __init__(self, frame_holder: FrameHolder, callback: Subject, width: int = -1) -> None:
        super().__init__(frame_holder.get_base_frame(), width)
        self.draw_compnent(frame_holder, callback)

    def draw_compnent(self, frame_holder: FrameHolder, callback: Subject) -> None:
        
        customer_name_entry = LabelEntryPair(self, "Customer Name:")
        customer_balance_entry = LabelEntryPair(self, "Customer Balance:")
        submit_button = OptionButton(self, "Add Submit", Subject())
        cancel_button = OptionButton(self, "Add Cancel", Subject())

        entity = CustomerAddEntity(
            FieldWrapper[str](None, lambda ipt: customer_name_entry.set_tip("Invalid Customer Name input")),
            FieldWrapper[Decimal](None, lambda ipt: customer_balance_entry.set_tip("Invalid Customer Balance input"))
        )
        
        customer_name_entry.get_input_subject().pipe(
            operators.do_action(lambda _: customer_name_entry.set_tip(""))
        ).subscribe(lambda ipt: entity.set_customer_name(ipt))
        
        customer_balance_entry.get_input_subject().pipe(
            operators.do_action(lambda _: customer_balance_entry.set_tip(""))
        ).subscribe(
            on_next = lambda ipt: entity.set_customer_balance(Decimal(ipt)),
            on_error = lambda error: print(f"{error}")
        )
        
        submit_button.get_button_subject().pipe(
            operators.map(lambda _: entity),
            operators.filter(lambda entity: entity.is_ready_for_submit()),
            operators.flat_map(lambda entity: handler.add_customer(entity))
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

    def __init__(self, frame_holder: FrameHolder, data: CustomerViewEntity, callback: Subject, width: int = -1) -> None:
        super().__init__(frame_holder.get_base_frame(), width)
        self.draw_compnent(frame_holder, data, callback)

    def draw_compnent(self, frame_holder: FrameHolder, data: CustomerViewEntity, callback: Subject) -> None:
        
        LabelEntryPair(self, "Customer ID:", default_value = data.get_customer_id(), editable = False)
        customer_name_entry = LabelEntryPair(self, "Customer Name:", default_value = data.get_customer_name())
        customer_balance_entry = LabelEntryPair(self, "Customer Balance:", default_value = data.get_customer_balance())
        submit_button = OptionButton(self, "Edit Submit", Subject())
        cancel_button = OptionButton(self, "Edit Cancel", Subject())

        data.set_name_error_hanlder(lambda ipt: customer_name_entry.set_tip("Invalid Customer Name input"))
        data.set_balance_error_hanlder(lambda ipt: customer_balance_entry.set_tip("Invalid Customer Balance input"))
        
        customer_name_entry.get_input_subject().pipe(
            operators.do_action(lambda _: customer_name_entry.set_tip(""))
        ).subscribe(lambda ipt: data.set_customer_name(ipt))
        
        customer_balance_entry.get_input_subject().pipe(
            operators.do_action(lambda _: customer_balance_entry.set_tip(""))
        ).subscribe(
            on_next = lambda ipt: data.set_customer_balance(MethodInvoker.execute(lambda: Decimal(ipt))),
            on_error = lambda error: print(f"{error}")
        )
        
        submit_button.get_button_subject().pipe(
            operators.map(lambda _: data),
            operators.filter(lambda entity: entity.is_ready_for_submit()),
            operators.flat_map(lambda entity: handler.edit_customer(entity))
        ).subscribe(cancel_button.get_button_subject())
        
        cancel_button.get_button_subject().pipe(
            operators.do_action(lambda _: frame_holder.revert_frame(destory = True))
        ).subscribe(callback)


class ReactiveEditCustomerButton(AbstractMenuButton):

    __callback_subject: Subject
    __customer_view: CustomerViewEntity

    def __init__(self, parent: BaseFrame, name: str, frame_holder: FrameHolder, subject: Subject, callback: Subject) -> None:
        super().__init__(parent, name, frame_holder, subject)
        self.__callback_subject = callback

    def display_button(self) -> None:
        self.pack(side = RIGHT, padx = 10, pady = 10)
    
    def get_compnent_frame(self) -> BaseFrame:
        new_frame = EditCustomerFrame(self.get_frame_holder(), self.__customer_view, self.__callback_subject)
        new_frame.set_frame_style(RIGHT, BOTH, True)
        return new_frame
    
    def set_data_to_edit(self, data: CustomerViewEntity) -> None:
        self.__customer_view = data

    def render_compnent(self, frame: BaseFrame) -> None:
        pass


class AddProductFrame(BaseFrame):

    def __init__(self, frame_holder: FrameHolder, callback: Subject, width: int = -1) -> None:
        super().__init__(frame_holder.get_base_frame(), width)
        self.draw_compnent(frame_holder, callback)

    def draw_compnent(self, frame_holder: FrameHolder, callback: Subject) -> None:
        
        product_name_entry = LabelEntryPair(self, "Product Name:")
        product_price_entry = LabelEntryPair(self, "Product Balance:")
        submit_button = OptionButton(self, "Add Submit", Subject())
        cancel_button = OptionButton(self, "Add Cancel", Subject())

        entity = ProductAddEntity(
            FieldWrapper[str](None, lambda ipt: product_name_entry.set_tip("Invalid Product Name input")),
            FieldWrapper[Decimal](None, lambda ipt: product_price_entry.set_tip("Invalid Product Price input"))
        )

        product_name_entry.get_input_subject().pipe(
            operators.do_action(lambda _: product_name_entry.set_tip(""))
        ).subscribe(lambda ipt: entity.set_product_name(ipt))
        
        product_price_entry.get_input_subject().pipe(
            operators.do_action(lambda _: product_price_entry.set_tip(""))
        ).subscribe(
            on_next = lambda ipt: entity.set_product_price(Decimal(ipt)),
            on_error = lambda error: print(f"{error}")
        )
        
        submit_button.get_button_subject().pipe(
            operators.map(lambda _: entity),
            operators.filter(lambda entity: entity.is_ready_for_submit()),
            operators.flat_map(lambda entity: handler.add_product(entity))
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
        
    def __init__(self, frame_holder: FrameHolder, data: ProductViewEntity, callback: Subject, width: int = -1) -> None:
        super().__init__(frame_holder.get_base_frame(), width)
        self.draw_compnent(frame_holder, data, callback)

    def draw_compnent(self, frame_holder: FrameHolder, data: ProductViewEntity, callback: Subject) -> None:

        LabelEntryPair(self, "Product ID:", default_value = data.get_product_id(), editable = False)
        product_name_entry = LabelEntryPair(self, "Product Name:", default_value = data.get_product_name())
        product_price_entry = LabelEntryPair(self, "Product Balance:", default_value = data.get_product_price())
        submit_button = OptionButton(self, "Edit Submit", Subject())
        cancel_button = OptionButton(self, "Edit Cancel", Subject())

        data.set_name_error_hanlder(lambda ipt: product_name_entry.set_tip("Invalid Product Name input"))
        data.set_price_error_hanlder(lambda ipt: product_price_entry.set_tip("Invalid Product Price input"))
        
        product_name_entry.get_input_subject().pipe(
            operators.do_action(lambda _: product_name_entry.set_tip(""))
        ).subscribe(lambda ipt: data.set_product_name(ipt))
        
        product_price_entry.get_input_subject().pipe(
            operators.do_action(lambda _: product_price_entry.set_tip(""))
        ).subscribe(
            on_next = lambda ipt: data.set_product_price(MethodInvoker.execute(lambda: Decimal(ipt))),
            on_error = lambda error: print(f"{error}")
        )
        
        submit_button.get_button_subject().pipe(
            operators.map(lambda _: data),
            operators.filter(lambda entity: entity.is_ready_for_submit()),
            operators.flat_map(lambda entity: handler.edit_product(entity))
        ).subscribe(cancel_button.get_button_subject())
        
        cancel_button.get_button_subject().pipe(
            operators.do_action(lambda _: frame_holder.revert_frame(destory = True))
        ).subscribe(callback)


class ReactiveEditProductButton(AbstractMenuButton):

    __callback_subject: Subject
    __product_view: ProductViewEntity

    def __init__(self, parent: BaseFrame, name: str, frame_holder: FrameHolder, subject: Subject, callback: Subject) -> None:
        super().__init__(parent, name, frame_holder, subject)
        self.__callback_subject = callback

    def display_button(self) -> None:
        self.pack(side = RIGHT, padx = 10, pady = 10)
    
    def get_compnent_frame(self) -> BaseFrame:
        new_frame = EditProductFrame(self.get_frame_holder(), self.__product_view, self.__callback_subject)
        new_frame.set_frame_style(RIGHT, BOTH, True)
        return new_frame
    
    def set_data_to_edit(self, data: ProductViewEntity) -> None:
        self.__product_view = data

    def render_compnent(self, frame: BaseFrame) -> None:
        pass    

GUI(Tk(), '1200x800', 'Lincoln Office Supplies').mainloop()
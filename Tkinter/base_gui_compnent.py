from tkinter import *
from tkinter import Event, Frame, ttk, font
from typing import TypeVar, List, Callable, Generic, Tuple, Dict
from reactivex import operators, Observable
from reactivex.subject import *
import abc, page, math, reactivex
from decimal import Decimal
from view_model import *
from tkinter.font import Font

## TypeVar used in some comenents for the type restriction
T = TypeVar("T")

## BaseFrame, control hidden and display options
## BaseFrame will also refresh all the refreshable compnents which regisred
class BaseFrame(Frame):

    def __init__(self, parent: Frame, width: int = -1) -> None:
        if width == -1:
            width = parent.winfo_width()
        Frame.__init__(self, parent, width = width)
        self.__fill: str = ''
        self.__side: str = ''
        self.__expand: bool = False
    

    def set_frame_style(self, side: str, fill: str, expand: bool = False) -> None:
        self.__side = side
        self.__fill = fill
        self.__expand = expand

    def display_frame(self) -> None:
        self.pack(fill = self.__fill, side = self.__side, expand = self.__expand)
        
    def hide_frame(self) -> None:
        self.pack_forget()

    def clear_all(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

## FrameHolder is used for holding the base frame and holing the current displayed frame
class FrameHolder:

    def __init__(self, frame: BaseFrame) -> None:
        self.__base_frame = frame
        self.__frame_stack: List[BaseFrame] = []

    def get_base_frame(self) -> BaseFrame:
        return self.__base_frame

    def get_current_frame(self) -> BaseFrame:
        if len(self.__frame_stack) > 0 :
            return self.__frame_stack[-1]
        return None
    
    def add_current_frame(self, frame: BaseFrame) -> None:
        self.__frame_stack.append(frame)
        frame.display_frame()

    def revert_frame(self, /, *, destory: bool) -> None:
        if len(self.__frame_stack) > 0 :
            old_frame = self.__frame_stack.pop()
            if destory:
                old_frame.destroy()
            else:
                old_frame.hide_frame()
        new_frame = self.get_current_frame()
        if new_frame is not None:
            new_frame.display_frame()


class AbstractButton(abc.ABC, Button):

    def __init__(self, parent: BaseFrame, name: str, subject: Subject) -> None:
        super().__init__(parent, text = name)
        self.__click_subject: Subject = subject
        self.bind('<Button-1>', self.on_click_event)
        self.display_button()

    def hide_button(self) -> None:
        self.pack_forget()

    def display_button(self) -> None:
        self.pack(expand = True, fill = X, padx = 10, pady = 10)

    def get_button_subject(self) -> Subject:
        return self.__click_subject

    def on_click_event(self, event: Event) -> None:
        if self.cget("state") != DISABLED:
            self.__click_subject.on_next(None)


class AbstractMenuButton(AbstractButton):

    def get_frame_holder(self) -> FrameHolder:
        return self.__frame_holder
    
    def get_compnent_frame(self) -> BaseFrame:
        return self.__compnent_frame;

    def __init__(self, parent: BaseFrame, name: str, frame_holder: FrameHolder, subject: Subject) -> None:
        super().__init__(parent, name, subject)
        self.__frame_holder: FrameHolder = frame_holder
        parent = frame_holder.get_base_frame()
        compnent_frame = BaseFrame(parent)
        compnent_frame.set_frame_style(RIGHT, BOTH, True)
        self.render_compnent(compnent_frame)
        self.__compnent_frame: BaseFrame = compnent_frame
        subject.subscribe(lambda _: self.__click_handler_chain())

    def __click_handler_chain(self) -> None:
        old_frame = self.get_frame_holder().get_current_frame()
        if old_frame is not None:
            old_frame.hide_frame()
        compnent_frame = self.get_compnent_frame()
        self.get_frame_holder().add_current_frame(compnent_frame)

    @abc.abstractmethod
    def render_compnent(self, frame: BaseFrame) -> None:
        pass

class OptionButton(AbstractButton):
    
    def __init__(self, parent: BaseFrame, name: str, subject: Subject) -> None:
        super().__init__(parent, name, subject)

    def display_button(self) -> None:
        self.pack(side = RIGHT, padx = 10, pady = 10)


class PageableTreeTable(ttk.Treeview, Generic[T], ABC):

    class PageButton(AbstractButton):

        def __init__(self, frame: BaseFrame, name: str, subject: Subject) -> None:
            super().__init__(frame, name, subject)

        def display_button(self) -> None:
            self.pack(side = LEFT)

    
    class TreeViewToolTip(Toplevel):

        def __init__(self, master: Misc) -> None:
            super().__init__(master)
            self.wm_overrideredirect(True)
            self.tooltip_label = Label(self, fg = "black", background = "white", borderwidth = 1, relief = SOLID)
            self.tooltip_label.pack()

        def set_text(self, text: str) -> None:
            self.tooltip_label.config(text = text)
        

    def get_page_size(self) -> int:
        return self.__page_size;

    def get_current_page(self) -> int:
        return self.__current_page
    
    def get_max_page_num(self) -> int:
        return self.__max_page_num;

    def set_current_page(self, current_page: int) -> None:
        self.__current_page = current_page
    
    def __set_max_page_num(self, max_page_num: int) -> None:
        self.__max_page_num = max_page_num

    def __init__(self, parent_frame: BaseFrame, columns: List[str], page_size: int = 35) -> None:
        
        super().__init__(parent_frame, show = "headings")
        
        self.__page_size: int = page_size
        self. __current_page: int = 1
        self.__max_page_num: int = 1

        self["columns"] = columns
        for col in columns:
            self.heading(col, text = col)
        
        pagination_frame = BaseFrame(parent_frame)

        load_subject = Subject()
        self.__load_subject: Subject = load_subject
        selected_subject = Subject()
        self.__selected_subject: Subject = selected_subject
        motion_subject = Subject()
        self.__motion_subject: Subject = motion_subject
        leave_subject: Subject = Subject()
        
        prev_button = PageableTreeTable.PageButton(pagination_frame, "prev", Subject())
        prev_button.get_button_subject().pipe(operators.do_action(lambda e: self.back_page())).subscribe(load_subject)
        
        next_button = PageableTreeTable.PageButton(pagination_frame, "next", Subject())
        next_button.get_button_subject().pipe(operators.do_action(lambda e: self.forward_page())).subscribe(load_subject)

        num_label = Label(pagination_frame)
        num_label.pack(side = LEFT)

        load_subject.pipe(
            operators.do_action(lambda _: self.clear()),
            operators.flat_map(lambda _: self.data_provider(self.get_current_page() - 1, self.get_page_size())),
            operators.do_action(lambda page_data: self.__set_max_page_num(math.ceil(page_data.get_total() / self.get_page_size()))),
            operators.do_action(lambda _: num_label.configure(text = "Page: {}/{}".format(self.get_current_page(), self.get_max_page_num()))),
            operators.flat_map(lambda page_data: reactivex.from_iterable(page_data.get_data())),
            operators.do_action(lambda data: self.column_provider(data))
        ).subscribe()

        load_subject.pipe(
            operators.do_action(lambda _: prev_button.config(state = NORMAL if self.get_current_page() > 1 else DISABLED)),
            operators.do_action(lambda _: next_button.config(state = NORMAL if self.get_current_page() < self.get_max_page_num() else DISABLED))
        ).subscribe()

        pagination_frame.pack(side = TOP, fill = X)
        
        self.tooltip_window: PageableTreeTable.TreeViewToolTip = None

        motion_subject.pipe(
            operators.flat_map(lambda event: motion_subject.pipe(
                operators.map(lambda _: self.identify_row(event.y)),
                operators.filter(lambda row: row is not None),
                operators.map(lambda row: self.item(row, "values")),
                operators.filter(lambda tuple: tuple is not None and len(tuple) > 0),
                operators.map(lambda tuple: self.on_motion_show(tuple)),
                operators.filter(lambda text: text is not None and len(text) > 0),
                operators.do_action(lambda _: self.__set_tooltip() if self.tooltip_window is None else None),
                operators.do_action(lambda text: self.tooltip_window.set_text(text)),
                operators.do_action(lambda _: self.tooltip_window.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}"))
            ))
        ).subscribe()

        leave_subject.pipe(
            operators.filter(lambda _: self.tooltip_window is not None),
            operators.do_action(lambda _: self.tooltip_window.destroy())
        ).subscribe(lambda _: self.__reset_tooltip())
        
        self.bind("<<TreeviewSelect>>", lambda _: selected_subject.on_next(self.instance_provider(self.item(self.selection()[0], 'values')) if self.selection() is not None else None))
        self.bind("<Motion>", lambda event: motion_subject.on_next(event))
        self.bind("<Leave>", lambda _: leave_subject.on_next(None))
        self.set_style()

    def set_style(self) -> None:
        self.pack(side = TOP, fill = BOTH, padx = 10, pady = 10, expand = True)
    
    def back_page(self) -> None:
        curr = self.get_current_page()
        if curr > 1:
            self.set_current_page(curr - 1)

    def forward_page(self) -> None:
        curr = self.get_current_page()
        if curr < self.get_max_page_num():
            self.set_current_page(curr + 1)

    @abstractmethod
    def data_provider(self, page: int, page_size: int) -> Observable[page.Page[T]]:
        pass
    
    @abstractmethod
    def column_provider(self, data: T) -> None:
        pass

    @abstractmethod
    def instance_provider(self, tuple: Tuple[str]) -> T:
        pass

    def on_motion_show(self, tuple: Tuple[str]) -> str:
        return None

    def __reset_tooltip(self):
        self.tooltip_window = None

    def __set_tooltip(self):
        self.tooltip_window = PageableTreeTable.TreeViewToolTip(self)
    
    def get_load_subject(self) -> Subject:
        return self.__load_subject
    
    def get_selected_subject(self) -> Subject:
        return self.__selected_subject
    
    def get_motion_subject(self) -> Subject:
        return self.__motion_subject

    def clear(self) -> None:
        for item in self.get_children():
            self.delete(item)


class LabelEntryPair(BaseFrame):
    
    def __init__(self, parent: Frame, label_name: str, /, *, anchor: str = W, default_value: str = "", editable: bool= True, width: int = -1) -> None:
        BaseFrame.__init__(self, parent, width = width)
        input_subject = Subject()
        self.__input_subject: Subject = input_subject
        self.draw_compnent(label_name, anchor, default_value, editable, input_subject)
        self.display_frame()

    def display_frame(self) -> None:
        self.pack(side = TOP, fill = X, expand = True)

    def draw_compnent(self, label_name: str, anchor: str, default_value: str, editable: bool, input_subject: Subject) -> None:
        label = Label(self, text = label_name, width = 20, anchor = anchor)
        entry_var = StringVar()
        entry_var.trace_add("write", lambda x, y, z: input_subject.on_next(entry_var.get()))
        entry = Entry(self, width = 30, relief = FLAT, borderwidth = 3, textvariable = entry_var)
        entry.insert(0, default_value)
        if not editable:
            entry.config(state = "readonly")
        tip_label = Label(self, width = 150)
        self.__entry: Entry = entry
        self.__tip_label: Label = tip_label
        self.set_style(label, entry, tip_label)
    
    def set_style(self, label: Label, entry: Label, tip: Label) -> None:
        label.pack(side = LEFT, fill = X, expand = True, padx = 20)
        entry.pack(side = LEFT, fill = X, expand = True, padx = 20)
        tip.pack(side = LEFT, fill = X, expand = True)

    def get_input_subject(self) -> Subject:
        return self.__input_subject

    def set_tip(self, tip: str) -> None:
        self.__tip_label.config(text = tip, fg = "red", anchor = W)

    def disable_input(self) -> None:
        self.__entry.config(state = DISABLED)

    def enable_input(self) -> None:
        self.__entry.config(state = NORMAL)


ENT = TypeVar("ENT", bound = SelectableEntity)

class PrefixSearchCombobox(ttk.Combobox, Generic[ENT]):

    def __init__(self, parent_frame: BaseFrame, data_function: Callable[[None], Observable[List[ENT]]]) -> None:
        super().__init__(parent_frame)
        selected_subject, load_subject = Subject(), Subject()
        self.__selected_subject: Subject = selected_subject
        self.__load_data_subject: Subject = load_subject
        self.__data_dict: Dict[str, ENT] = {}
        entry_var = StringVar()
        input_subject = Subject()
        entry_var.trace_add("write", lambda x, y, z: input_subject.on_next(entry_var.get()))
        self.config(textvariable = entry_var)
        
        input_subject.pipe(
            operators.map(lambda ipt: [item for item in self.__data_dict.keys()if ipt is None or len(ipt) == 0 or item.lower().startswith(ipt.lower())]),
            operators.filter(lambda list: list is not None and len(list) > 0),
            operators.do_action(lambda values: self.config(values = values)),
            operators.do_action(lambda _: self.event_generate('<Down>')),
            operators.do_action(lambda _: self.selection_clear()),
            operators.do_action(lambda _: self.icursor(END))
        ).subscribe(lambda _: self.focus_set())

        load_subject.pipe(
            operators.do_action(lambda _ : self.__data_dict.clear()),
            operators.flat_map(lambda _: data_function()),
            operators.map(lambda list: {item.get_selection_key(): item for item in list}),
            operators.do_action(lambda dicts : self.__data_dict.update(dicts))
        ).subscribe(lambda dicts: self.config(values = list(dicts.keys())))

        self.bind("<<ComboboxSelected>>", lambda _: selected_subject.on_next(self.__data_dict.get(self.get())))
        self.set_style()

    def get_selected_subject(self) -> Subject:
        return self.__selected_subject
    
    def get_load_subject(self) -> Subject:
        return self.__load_data_subject
    
    def set_style(self) -> None:
        self.pack(side = TOP, padx = 10, pady = 10, anchor = W)


class BaseTextBox(Text):
    
    def __init__(self, parent_frame: BaseFrame, width: int = 50, heigh: int = 5) -> None:
        super().__init__(parent_frame, width = width, height = heigh, borderwidth = 5)
        self.config(state = DISABLED, font = font.Font(size = 15))
        self.pack(side = TOP, padx = 10, pady = 10)

    def replace_text(self, text: str) -> None:
        self.config(state = NORMAL)
        self.delete(1.0, END)
        self.insert(END, text)
        self.config(state = DISABLED)

    def clear_all(self) -> None:
        self.delete(1.0, END)


class BaseSpinBox(Spinbox):

    def __init__(self, parent_frame: Frame, from_: int = 0, to: int = 100) -> None:
        super().__init__(parent_frame, from_ = from_, to = to)
        self.__selected_subject: Subject = Subject()
        int_var = IntVar()
        int_var.trace_add("write", lambda x, y, z: self.__selected_subject.on_next(int_var.get()))
        self.config(textvariable = int_var)
        self.set_style()

    def get_selected_subject(self) -> Subject:
        return self.__selected_subject
    
    def set_style(self) -> None:
        self.pack(side = TOP, padx = 10, pady = 10, anchor = NW)


class SearchBar(BaseFrame):
    
    def __init__(self, parent: Frame, label_name: str, /, *, width: int = -1) -> None:
        BaseFrame.__init__(self, parent, width = width)
        input_subject = Subject()
        self.__input_subject: Subject = input_subject
        self.draw_compnent(label_name, input_subject)
        self.display_frame()

    def display_frame(self) -> None:
        self.pack(side = TOP)

    def draw_compnent(self, label_name: str, input_subject: Subject) -> None:
        label = Label(self, text = label_name, width = 20)
        entry_var = StringVar()
        entry_var.trace_add("write", lambda x, y, z: input_subject.on_next(entry_var.get()))
        entry = Entry(self, width = 30, relief = FLAT, borderwidth = 3, textvariable = entry_var)
        self.set_style(label, entry)

    def set_style(self, label: Label, entry: Entry) -> None:
        label.pack(side = LEFT, padx = 20, anchor = E)
        entry.pack(side = LEFT, padx = 20, anchor = E)

    def get_input_subject(self) -> Subject:
        return self.__input_subject

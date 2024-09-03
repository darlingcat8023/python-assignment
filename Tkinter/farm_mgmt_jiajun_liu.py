# ============== TE WAIHORA FARM MANAGEMENT SYSTEM ==============
# Student Name: JIAJUN LIU
# Student ID :  1159501
# ================================================================
 
from datetime import datetime, timedelta     # datetime module is required for working with dates
from typing import Callable, TypeVar

import farm_data    # Makes the variables and function in farm_data.py available in this code


# Global variable values that can be referred to throughout your code.  
# (Do not change these values.)
current_date            = datetime(2024, 8, 26)
pasture_growth_rate     = 65    #kg DM/ha/day
stock_growth_rate       = 0.7   #kg per day
stock_consumption_rate  = 14    #kg DM/animal/day
earliest_birth_date     = "1/06/2022"
weight_range            = (250, 700)

# Collection variables from farm_data.py are available in this code (renamed here to remove the 'farm_data.' prefix).
mobs = farm_data.mobs
paddocks = farm_data.paddocks
stock = farm_data.stock

# Functions from farm_data.py are available in this code (renamed here to remove the 'farm_data.' prefix).
next_id = farm_data.next_id
display_formatted_row = farm_data.display_formatted_row
pasture_levels = farm_data.pasture_levels

current_date_formate = "%d/%m/%Y"   # date formate
T = TypeVar("T")                    # Var Type

def __print_by_group(key: str, key_func: Callable[[str], None], sub_title_func: Callable[[str], None], down_stream: Callable[[str], None]) -> None:
    """
    This is a helper function to apply for a lambda expression
    """
    if key_func is not None: key_func(key)
    if sub_title_func is not None: sub_title_func(key)
    down_stream(key)  

def list_all_stock():
    """
    Lists stock details (except birth date).
    """
    format_str = "{: <5} {: <7} {: <5} {: <5}"
    __print_by_group(None, None, lambda k: display_formatted_row(["ID", "Mob", "Age", "Weight"], format_str), lambda k: list(map(lambda data: display_formatted_row([data[i] for i in [0, 1, 3, 4]], format_str), sorted(stock, key = lambda x: x[0], reverse = True))))
    input("\nPress Enter to continue.")

def list_stock_by_mob():
    """
    Lists stock details (including birth date), grouped by mob name.
    """
    format_str = "{: <5} {: <7} {: <12} {: <5} {: <5}"
    down_stream = lambda k: list(map(lambda data: display_formatted_row([data[0], data[1], datetime.strftime(data[2], current_date_formate), data[3], data[4]], format_str), [i for i in stock if i[0] in mobs.get(k)]))
    list(map(lambda key: __print_by_group(key, lambda k: print("Group Name: {0}".format(k)), lambda k: display_formatted_row(["ID", "Mob", "Birth", "Age", "Weight"], format_str), down_stream), sorted(mobs.keys(), key = lambda x: x)))
    input("\nPress Enter to continue.")

def list_paddock_details():
    """
    List the paddock names and all details.
    """
    format_str = "{: <5} {: <6} {: <9} {: <6} {: <10}"
    list(map(lambda key: __print_by_group(key, lambda k: print("Paddock Name: {0}".format(k)), lambda k: display_formatted_row(list(paddocks.get(k).keys()), format_str), lambda k: display_formatted_row(list(paddocks.get(k).values()), format_str)), sorted(paddocks.keys(), key = lambda x: x)))
    input("\nPress Enter to continue.")

def __get_valid_user_input(convert_func: Callable[[str], T], predicate_func: Callable[[T], bool], show_tips: str = "") -> T:
    """
    Receive a user input in a loop until the input match the condition
    """
    input_str = input(show_tips).strip()
    try:
        converted = convert_func(input_str)
        if predicate_func(converted): return converted
    except Exception: pass
    print("\nThis is an invalid input, please enter again\n")
    return __get_valid_user_input(convert_func, predicate_func, show_tips)

def move_mobs_between_paddocks():
    """
    Change which paddock each mob is in. 
    """
    global paddocks, mobs
    paddock_options = [k for k, v in paddocks.items() if v["mob"] is None]
    if len(paddock_options) == 0: 
        print("There are no empty paddocks available for moving")
        return
    selected_mob = __get_valid_user_input(lambda ipt: ipt, lambda ipt: ipt in mobs.keys(), "Please select a valid mob: \n")
    selected_paddock =  __get_valid_user_input(lambda ipt: ipt, lambda ipt: ipt in paddock_options, "Please select a valid paddock from {0}: \n".format(paddock_options))
    paddocks = {k: {**v, "mob": None , "stock num": 0} if v["mob"] == selected_mob else v for k, v in paddocks.items()}
    paddocks.get(selected_paddock).update({"mob": selected_mob, "stock num": len(mobs.get(selected_mob))})
    print("\nSuccessfully update mob [{0}] to paddock [{1}] \n".format(selected_mob, selected_paddock))

def add_new_stock():
    """
    Add a new animal to the stock list.
    """
    __add_new_stock_dfs(datetime.strptime(earliest_birth_date, current_date_formate), "Y")

def __add_new_stock_dfs(birth_base: datetime, flag: str) -> None:
    if flag != "Y": return
    global paddocks
    inputed_mob = __get_valid_user_input(lambda ipt: ipt, lambda ipt: ipt in mobs.keys(), "Please enter a valid mob: ")
    inputed_birth = __get_valid_user_input(lambda ipt: datetime.strptime(ipt, current_date_formate), lambda ipt: ipt > birth_base and ipt < current_date, "Please enter a valid birthday using formate 'DD/MM/YYYY': ")
    inputed_weight = __get_valid_user_input(lambda ipt: float(ipt), lambda ipt: ipt <= weight_range[1] and ipt >= weight_range[0], "Please enter a valid weight between [{0}] and [{1}]: ".format(weight_range[0], weight_range[1]))
    gen_id = next_id(stock)
    stock.append([gen_id, inputed_mob, inputed_birth, __calculate_year_difference(birth_base, inputed_birth), inputed_weight])
    mobs.get(inputed_mob).append(gen_id)        # update mobs
    paddocks = {k: {**v, "stock num": v["stock num"] + 1} if v["mob"] == inputed_mob else v for k, v in paddocks.items()}  # update paddocks
    __add_new_stock_dfs(birth_base, __get_valid_user_input(lambda ipt: ipt, lambda ipt: True, "Successfully added a stock with ID [{0}], press [Y] to add another otherwise any key to exit. \n".format(gen_id)).upper())

def __calculate_year_difference(date1: datetime, date2: datetime) -> int:
    """
    This method used to calculate year differs between two different dates
    """
    year_diff = date2.year - date1.year
    if (date2.month, date2.day) < (date1.month, date1.day): year_diff -= 1
    return year_diff

def move_to_next_day():
    """
    Increase the current date by one day, making other required changes.
    """
    global current_date, stock, paddocks
    current_date += timedelta(days = 1)
    stock = [[item[0], item[1], item[2], __calculate_year_difference(item[2], current_date), item[4]] for item in stock]
    paddocks = {k: {**v, "dm/ha": res.get("dm/ha"), "total dm": res.get("total dm")} for k, v in paddocks.items() for res in [pasture_levels(v["area"], v["stock num"], v["total dm"], pasture_growth_rate, stock_consumption_rate)]}
    print("Date has moved successfully\n")

def disp_menu():
    """
    Displays the menu and current date.  No parameters required.
    """
    print("==== WELCOME TE WAIHORA FARM MANAGEMENT SYSTEM ===")
    print(" Today is [ {0} ]".format(datetime.strftime(current_date, current_date_formate)))
    print(" 1 - List All Stock")
    print(" 2 - List Stock Grouped by Mob")
    print(" 3 - List Paddock Details")
    print(" 4 - Move Mobs Between Paddocks")
    print(" 5 - Add New Stock")
    print(" 6 - Move to Next Day")
    print(" X - eXit (stops the program)")


# ------------ This is the main program ------------------------


# Don't change the menu numbering or function names in this menu.
# Although you can add arguments to the function calls, if you wish.
# Repeat this loop until the user enters an "X" or "x"
while True:
    disp_menu()
    # Display menu for the first time, and ask for response
    input_opt = __get_valid_user_input(lambda ipt: ipt.upper(), lambda ipt: True, "Please enter menu choice: ")
    print("\n")
    if input_opt == "1":    list_all_stock()
    elif input_opt == "2":  list_stock_by_mob()
    elif input_opt == "3":  list_paddock_details()
    elif input_opt == "4":  move_mobs_between_paddocks()
    elif input_opt == "5":  add_new_stock()
    elif input_opt == "6":  move_to_next_day()
    elif input_opt == "X":  print("\n=== Thank you for using Te Waihora Farm Management System! ===\n"); break
    else:                   print("\n*** Invalid response, please try again (enter 1-6 or X)")
    print("")
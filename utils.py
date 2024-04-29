from pandas import DataFrame
from simple_term_menu import TerminalMenu

from model_enums import ColumnsEnums


def goodbye():
    exit("\nSee you later, buddy 👋")


def generate_menu(list_of_options: list):
    options = []
    for index, option in enumerate(list_of_options):
        options.append(f"[{index + 1}] - {list_of_options[index][0]}")
    return options


def _select_multi_choice(options: list, title: str) -> list:
    terminal_menu = TerminalMenu(
        options,
        title=title,
        multi_select=True,
        show_multi_select_hint=True,
    )
    terminal_menu.show()
    return list(terminal_menu.chosen_menu_entries)


def _select_single_choice(options: list, title: str):
    terminal_menu = TerminalMenu(
        options,
        title=title,
        show_multi_select_hint=True,
    )
    index = terminal_menu.show()
    return options[index]


def _select_single_choice_index(options: list, title: str):
    terminal_menu = TerminalMenu(
        options,
        title=title,
        show_multi_select_hint=True,
    )
    index = terminal_menu.show()
    return index


def _filter_by_col_value(df: DataFrame, col_to_filter: str, msg_to_user):
    list_of_unique_values: list = df[col_to_filter].unique().tolist()

    if col_to_filter == ColumnsEnums.YEAR:
        list_of_unique_values = list(map(lambda x: str(x), list_of_unique_values))
        list_of_values_to_filter_by = _select_multi_choice(list_of_unique_values, msg_to_user)
        list_of_values_to_filter_by = list(map(lambda x: int(x), list_of_values_to_filter_by))
    else:
        list_of_values_to_filter_by = _select_multi_choice(list_of_unique_values, msg_to_user)

    df_filtered: DataFrame = df[df[col_to_filter].isin(list_of_values_to_filter_by)]
    return df_filtered


def _sub_menu(func, func_desc, *args):
    print("\nAny thing else I can help you with?")
    sub_menu_options = [f"{func_desc}", "Main Menu", "Exit"]
    index = _select_single_choice_index(sub_menu_options, "Please select:")
    match index:
        case 0:
            func(*args)
        case 1:
            from housely import start
            start()
        case 2:
            goodbye()

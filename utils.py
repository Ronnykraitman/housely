from pandas import DataFrame
from simple_term_menu import TerminalMenu

from model_enums import ColumnsEnums


def _select_multi_choice(options: list, title: str) -> list:
    terminal_menu = TerminalMenu(
        options,
        title=title,
        multi_select=True,
        show_multi_select_hint=True,
    )
    terminal_menu.show()
    return list(terminal_menu.chosen_menu_entries)


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

import numpy as np
from pandas import DataFrame

from colors import Bright_Blue, Color_Off, Bright_Magenta, Bright_Green
from data_encoder import get_unencoded_keys_from_mapping, get_encoded_values
from model import predict
from model_enums import TargetEnums, ColumnsEnums
from utils import _select_multi_choice, _select_single_choice, _sub_menu


def _filter_df_by_columns(df: DataFrame, cols: list):
    cols.append(ColumnsEnums.PREDICTIONS)
    return df.filter(cols)


def _predict_by_feature(model, mapping: dict, predict_by_feature: str, user_msg: str):
    list_of_values_for_selection: list = get_unencoded_keys_from_mapping(mapping, predict_by_feature)
    selected_values: list = _select_multi_choice(list_of_values_for_selection, user_msg)
    selected_feature_values_encoded: list = get_encoded_values(selected_values, mapping, predict_by_feature)

    second_main_key = ColumnsEnums.NUMBER_OF_ROOMS if predict_by_feature == ColumnsEnums.CITY else ColumnsEnums.CITY
    list_of_second_feature_values: list = get_unencoded_keys_from_mapping(mapping, second_main_key)
    second_feature_values_encoded: list = get_encoded_values(list_of_second_feature_values, mapping, second_main_key)

    predictions = predict(model, selected_feature_values_encoded, second_feature_values_encoded, predict_by_feature)

    return predictions, selected_values, list_of_second_feature_values


def _add_revenue(df: DataFrame):
    df.assign(revenue_by_percentage=None)
    df.assign(revenue_by_absolute_sum=None)

    df_with_revenue: DataFrame = df.copy()
    for index, row in df.iterrows():
        df_with_revenue.loc[index, 'revenue_by_absolute_sum'] = _absolute_sum(row)
        df_with_revenue.loc[index, 'revenue_by_percentage'] = _diff_by_percentage(row)

    return df_with_revenue


def _show_top_3_revenue(df_with_revenue: DataFrame):
    sorted_df_by_value = df_with_revenue.sort_values(by='revenue_by_absolute_sum', ascending=False)
    top_3_rows_by_value = sorted_df_by_value.head(3)

    print(f"\nHere are the {Bright_Green}TOP 3{Color_Off} apartments, by absolute revenue")
    for i, row in top_3_rows_by_value.iterrows():
        print(
            f"Apartment in {Bright_Blue}{row[ColumnsEnums.CITY]}{Color_Off} with"
            f" {Bright_Magenta}{row[ColumnsEnums.NUMBER_OF_ROOMS]}{Color_Off} rooms will get you "
            f"{row["revenue_by_absolute_sum"]} ₪ revenue")

    sorted_df_by_per = df_with_revenue.sort_values(by='revenue_by_percentage', ascending=False)
    top_3_rows_by_per = sorted_df_by_per.head(3)

    print(f"\nHere are the {Bright_Green}TOP 3{Color_Off} apartments, by percentage revenue")
    for i, row in top_3_rows_by_per.iterrows():
        print(
            f"Apartment in {Bright_Blue}{row[ColumnsEnums.CITY]}{Color_Off} with "
            f"{Bright_Magenta}{row[ColumnsEnums.NUMBER_OF_ROOMS]}{Color_Off} rooms will get you "
            f"{row["revenue_by_percentage"]}% revenue")


def _absolute_sum(row):
    avg_price = int(round(float(row["avg_price"]), 2) * 1000)
    return int(round(row["2024_prediction"] - avg_price))


def _diff_by_percentage(row):
    avg_price = int(round(float(row["avg_price"]), 2) * 1000)
    percentage = (row["2024_prediction"] / avg_price) * 100

    full_per = str(int(round(percentage, 2)))
    if len(full_per) > 2:
        full_per_str = "".join([full_per[1], full_per[2]])
        return int(full_per_str)
    return 0


def _get_basics(df: DataFrame):
    min_prediction = df[ColumnsEnums.PREDICTIONS].min().round(2)
    max_prediction = df[ColumnsEnums.PREDICTIONS].max().round(2)
    median_prediction = df[ColumnsEnums.PREDICTIONS].median().round(2)
    avg_prediction = df[ColumnsEnums.PREDICTIONS].mean().round(2)

    return min_prediction, max_prediction, median_prediction, avg_prediction


def _predict_by_single_feature_for_revenue(model, mapping: dict, df: DataFrame):
    options = ["City", "Number of rooms"]
    selected_filter = _select_single_choice(options, "Revenue by:")
    df['2024_prediction'] = None
    main_condition = ""

    main_feature = ColumnsEnums.NUMBER_OF_ROOMS if selected_filter == "Number of rooms" else ColumnsEnums.CITY
    predictions, main_feature_values, second_feature_values = _predict_by_feature(model, mapping, main_feature,
                                                                                  "Please select: ")
    prediction_index = 0

    match selected_filter:
        case "City":
            for city in main_feature_values:
                for room_type in second_feature_values:
                    city_condition = df[ColumnsEnums.CITY] == city
                    room_type_condition = df[ColumnsEnums.NUMBER_OF_ROOMS] == room_type
                    df['2024_prediction'] = np.where(city_condition & room_type_condition,
                                                     predictions[prediction_index], df['2024_prediction'])
                    prediction_index += 1
            main_condition = df[ColumnsEnums.CITY].isin(main_feature_values)

        case "Number of rooms":
            for room_type in main_feature_values:
                for city in second_feature_values:
                    city_condition = df[ColumnsEnums.CITY] == city
                    room_type_condition = df[ColumnsEnums.NUMBER_OF_ROOMS] == room_type
                    df['2024_prediction'] = np.where(city_condition & room_type_condition,
                                                     predictions[prediction_index], df['2024_prediction'])
                    prediction_index += 1
            main_condition = df[ColumnsEnums.NUMBER_OF_ROOMS].isin(main_feature_values)

    past_year_condition = df[ColumnsEnums.YEAR] == 2023
    filtered_df = df[past_year_condition & main_condition]

    df_with_revenue = _add_revenue(filtered_df)
    return df_with_revenue


def predict_by_city(model, mapping: dict):
    while True:
        predictions, cities, rooms = _predict_by_feature(model, mapping, ColumnsEnums.CITY, "Available cities:")

        prediction_index = 0
        for city in cities:
            print(f"\nHere are the {TargetEnums.YEAR_FOR_PREDICTION} predictions for {Bright_Blue}{city}{Color_Off}:")
            for room_type in rooms:
                print(f"{room_type} rooms apartment is predicted to cost: {predictions[prediction_index]} ₪")
                prediction_index += 1

        _sub_menu(predict_by_city, "Lets see other city prediction", model, mapping)


def predict_by_number_of_rooms(model, mapping: dict):
    while True:
        predictions, rooms, cities = _predict_by_feature(model, mapping, ColumnsEnums.NUMBER_OF_ROOMS,
                                                         "Available number of rooms:")

        prediction_index = 0
        for room_type in rooms:
            print(f"\nHere are the {TargetEnums.YEAR_FOR_PREDICTION} predictions for "
                  f"{Bright_Magenta}{room_type}{Color_Off} rooms, by city:")
            for city in cities:
                print(f"In {Bright_Blue}{city}{Color_Off} this type of apartment is predicted to cost: "
                      f"{predictions[prediction_index]} ₪")
                prediction_index += 1

        _sub_menu(predict_by_number_of_rooms, "Lets see other room types prediction", model, mapping)


def predict_by_district(model, mapping: dict, df: DataFrame):
    while True:
        unique_districts: list = df[ColumnsEnums.DISTRICT].unique().tolist()
        selected_districts: list = _select_multi_choice(unique_districts, "Available districts:")

        condition_district = df[ColumnsEnums.DISTRICT].isin(selected_districts)
        df_filtered: DataFrame = df[condition_district]
        cities_in_district: list = df_filtered[ColumnsEnums.CITY].unique().tolist()

        cities_in_district_encoded: list = get_encoded_values(cities_in_district, mapping, ColumnsEnums.CITY)
        list_of_rooms: list = get_unencoded_keys_from_mapping(mapping, ColumnsEnums.NUMBER_OF_ROOMS)
        room_types_encoded: list = get_encoded_values(list_of_rooms, mapping, ColumnsEnums.NUMBER_OF_ROOMS)

        predictions = predict(model, cities_in_district_encoded, room_types_encoded, ColumnsEnums.CITY)

        prediction_index = 0
        for city in cities_in_district:
            print(f"\nHere are the {TargetEnums.YEAR_FOR_PREDICTION} predictions for {Bright_Blue}{city}{Color_Off}:")
            for room_type in list_of_rooms:
                print(f"{Bright_Magenta}{room_type}{Color_Off} rooms apartment is predicted to cost: "
                      f"{predictions[prediction_index]} ₪")
                prediction_index += 1

        _sub_menu(predict_by_district, "Lets see other districts prediction", model, mapping, df)


def get_best_revenue_prediction(model, mapping: dict, df: DataFrame):
    while True:
        df_with_revenue: DataFrame = _predict_by_single_feature_for_revenue(model, mapping, df)
        _show_top_3_revenue(df_with_revenue)

        _sub_menu(get_best_revenue_prediction, "Lets see other revenue prediction", model, mapping, df)


def get_apartments_by_user_asset(model, df: DataFrame):
    while True:
        is_valid_input = False
        price_by_user = 0
        while not is_valid_input:
            try:
                user_input = input("Please enter the price in ₪ you are willing to pay, like 850000 or 2800000: ")
                price_by_user = int(user_input)
                is_valid_input = True
            except Exception:
                print("That is not a valid amount. Try again")

        predictions = model.predict(df[["num_of_rooms_encoded", "city_encoded", "year"]])
        predictions_rounded = list(map(lambda x: int(x.round(2) * 1000), predictions))

        df["2024_prediction"] = predictions_rounded
        past_year_condition = df[ColumnsEnums.YEAR] == 2023
        price_condition = df["2024_prediction"] <= price_by_user
        df_filtered = df[price_condition & past_year_condition]

        options = ["Show me top 3 most profitable apartments", "Show me all the apartments I can buy"]
        user_selection = _select_single_choice(options, "What would you like to see?")

        if user_selection == "Show me top 3 most profitable apartments":
            df_with_revenue: DataFrame = _add_revenue(df_filtered)
            _show_top_3_revenue(df_with_revenue)

        if user_selection == "Show me all the apartments I can buy":
            filtered_df_no_dup: DataFrame = df_filtered.drop_duplicates(subset=['city', 'num_of_rooms'])
            for index, row in filtered_df_no_dup.iterrows():
                print(
                    f"You can buy a {row[ColumnsEnums.NUMBER_OF_ROOMS]} apartment in "
                    f"{Bright_Blue}{row[ColumnsEnums.CITY]}{Color_Off} for estimated price of {row['2024_prediction']}")

        _sub_menu(get_apartments_by_user_asset, "Lets see other apartments prediction", model, df)

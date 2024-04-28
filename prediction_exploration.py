import numpy as np
from pandas import DataFrame

from data_encoder import get_unencoded_keys_from_mapping, get_encoded_values
from model import predict
from model_enums import TargetEnums, ColumnsEnums
from utils import _select_multi_choice, _select_single_choice

'''
6. tell me how much you have and I'll tell you where to invest
'''


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


def predict_by_city(model, mapping: dict):
    predictions, cities, rooms = _predict_by_feature(model, mapping, ColumnsEnums.CITY, "Available cities:")

    prediction_index = 0
    for city in cities:
        print(f"\nHere are the {TargetEnums.YEAR_FOR_PREDICTION} predictions for {city}:")
        for room_type in rooms:
            print(f"{room_type} rooms apartment is predicted to cost: {predictions[prediction_index]} ₪")
            prediction_index += 1
    print()


def predict_by_number_of_rooms(model, mapping: dict):
    predictions, rooms, cities = _predict_by_feature(model, mapping, ColumnsEnums.NUMBER_OF_ROOMS,
                                                     "Available number of rooms:")

    prediction_index = 0
    for room_type in rooms:
        print(f"\nHere are the {TargetEnums.YEAR_FOR_PREDICTION} predictions for {room_type} rooms, by city:")
        for city in cities:
            print(f"In {city} this type of apartment is predicted to cost: {predictions[prediction_index]} ₪")
            prediction_index += 1
    print()


def predict_by_district(model, mapping: dict, df: DataFrame):
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
        print(f"\nHere are the {TargetEnums.YEAR_FOR_PREDICTION} predictions for {city}:")
        for room_type in list_of_rooms:
            print(f"{room_type} rooms apartment is predicted to cost: {predictions[prediction_index]} ₪")
            prediction_index += 1


def get_best_revenue_prediction(model, mapping: dict, df: DataFrame):
    options = ["City", "Number of rooms"]
    selected_filter = _select_single_choice(options, "Revenue by:")
    df['2024_prediction'] = None
    df["revenue_by_percentage"] = None
    df["revenue_by_absolute_sum"] = None
    main_condition = ""

    main_feature = ColumnsEnums.NUMBER_OF_ROOMS if selected_filter == "Number of rooms" else ColumnsEnums.CITY
    predictions, main_feature_values, second_feature_values = _predict_by_feature(model, mapping, main_feature,"Please select: ")
    prediction_index = 0

    match selected_filter:
        case "City":
            for city in main_feature_values:
                for room_type in second_feature_values:
                    city_condition = df[ColumnsEnums.CITY] == city
                    room_type_condition = df[ColumnsEnums.NUMBER_OF_ROOMS] == room_type
                    df['2024_prediction'] = np.where(city_condition & room_type_condition, predictions[prediction_index], df['2024_prediction'])
                    prediction_index += 1
            main_condition = df[ColumnsEnums.CITY].isin(main_feature_values)

        case "Number of rooms":
            for room_type in main_feature_values:
                for city in second_feature_values:
                    city_condition = df[ColumnsEnums.CITY] == city
                    room_type_condition = df[ColumnsEnums.NUMBER_OF_ROOMS] == room_type
                    df['2024_prediction'] = np.where(city_condition & room_type_condition, predictions[prediction_index], df['2024_prediction'])
                    prediction_index += 1
            main_condition = df[ColumnsEnums.NUMBER_OF_ROOMS].isin(main_feature_values)


    past_year_condition = df[ColumnsEnums.YEAR] == 2023
    filtered_df = df[past_year_condition & main_condition]

    for index, row in filtered_df.iterrows():
        filtered_df.loc[index, 'revenue_by_absolute_sum'] = _absolute_sum(row)
        filtered_df.loc[index, 'revenue_by_percentage'] = _diff_by_percantege(row)

    sorted_df_by_value = filtered_df.sort_values(by='revenue_by_absolute_sum', ascending=False)
    top_3_rows_by_value = sorted_df_by_value.head(3)

    print("\nHere are the top 3 apartments, by absolute revenue")
    for i, row in top_3_rows_by_value.iterrows():
        print(f"Apartment in {row[ColumnsEnums.CITY]} with {row[ColumnsEnums.NUMBER_OF_ROOMS]} rooms will get you {row["revenue_by_absolute_sum"]} ₪ revenue")

    sorted_df_by_per = filtered_df.sort_values(by='revenue_by_percentage', ascending=False)
    top_3_rows_by_per = sorted_df_by_per.head(3)

    print("\nHere are the top 3 apartments, by percentage revenue")
    for i, row in top_3_rows_by_per.iterrows():
        print(f"Apartment in {row[ColumnsEnums.CITY]} with {row[ColumnsEnums.NUMBER_OF_ROOMS]} rooms will get you {row["revenue_by_percentage"]}% revenue")



def _absolute_sum(row):
    avg_price = int(round(float(row["avg_price"]), 2) * 1000)
    return row["2024_prediction"] - avg_price

def _diff_by_percantege(row):
    avg_price = int(round(float(row["avg_price"]), 2) * 1000)
    percentage = (row["2024_prediction"] / avg_price) * 100

    full_per = str(int(round(percentage, 2)))
    if len(full_per) > 2:
        full_per_str = "".join([full_per[1],full_per[2]])
        return int(full_per_str)
    return 0


def _get_basics(df: DataFrame):
    min_prediction = df[ColumnsEnums.PREDICTIONS].min().round(2)
    max_prediction = df[ColumnsEnums.PREDICTIONS].max().round(2)
    median_prediction = df[ColumnsEnums.PREDICTIONS].median().round(2)
    avg_prediction = df[ColumnsEnums.PREDICTIONS].mean().round(2)

    return min_prediction, max_prediction, median_prediction, avg_prediction

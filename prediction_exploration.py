import pandas as pd
from pandas import DataFrame

from data_encoder import encode_data
from data_prep import load_data, drop_nulls, split_data
from model import predict
from model_enums import PredictorsEnums, TargetEnums, ColumnsEnums
from utils import _select_multi_choice, _filter_by_col_value

'''
1. predict price in city - avg / range
2. predict price by num of rooms - avg
3. predict price by district
5. best predicted revenue
6. tell me how much you have and I'll tell you where to invest
'''


def _prepare_data_for_prediction():
    df_raw: DataFrame = load_data()
    df_no_nulls = drop_nulls(df_raw)
    df, mapping = encode_data(df_no_nulls, [PredictorsEnums.NUMBER_OF_ROOMS, PredictorsEnums.CITY])

    return df, mapping


def _get_unencoded_keys_from_mapping(mapping: dict, main_key: str):
    main_key_dict: dict = mapping[main_key]
    return list(main_key_dict.keys())


def _get_encoded_values(list_of_values: list, mapping: dict, main_key: str):
    encoded_dict: dict = mapping[main_key]
    list_of_values_encoded = []
    for value_to_encode in list_of_values:
        list_of_values_encoded.append(encoded_dict[value_to_encode])

    return list_of_values_encoded


def _predict_by_feature(model, mapping: dict, predict_by_feature: str, user_msg: str):
    list_of_values_for_selection: list = _get_unencoded_keys_from_mapping(mapping, predict_by_feature)
    selected_values: list = _select_multi_choice(list_of_values_for_selection, user_msg)
    selected_feature_values_encoded: list = _get_encoded_values(selected_values, mapping, predict_by_feature)

    second_main_key = ColumnsEnums.NUMBER_OF_ROOMS if predict_by_feature == ColumnsEnums.CITY else ColumnsEnums.CITY
    list_of_second_feature_values: list = _get_unencoded_keys_from_mapping(mapping, second_main_key)
    second_feature_values_encoded: list = _get_encoded_values(list_of_second_feature_values, mapping, second_main_key)

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

    cities_in_district_encoded: list = _get_encoded_values(cities_in_district, mapping, ColumnsEnums.CITY)
    list_of_rooms: list = _get_unencoded_keys_from_mapping(mapping, ColumnsEnums.NUMBER_OF_ROOMS)
    room_types_encoded: list = _get_encoded_values(list_of_rooms, mapping, ColumnsEnums.NUMBER_OF_ROOMS)

    predictions = predict(model, cities_in_district_encoded, room_types_encoded, ColumnsEnums.CITY)

    prediction_index = 0
    for city in cities_in_district:
        print(f"\nHere are the {TargetEnums.YEAR_FOR_PREDICTION} predictions for {city}:")
        for room_type in list_of_rooms:
            print(f"{room_type} rooms apartment is predicted to cost: {predictions[prediction_index]} ₪")
            prediction_index += 1


# # def get_best_revenue_prediction(model, mapping: dict, df: DataFrame):


def _get_basics(df: DataFrame):
    min_prediction = df[ColumnsEnums.PREDICTIONS].min().round(2)
    max_prediction = df[ColumnsEnums.PREDICTIONS].max().round(2)
    median_prediction = df[ColumnsEnums.PREDICTIONS].median().round(2)
    avg_prediction = df[ColumnsEnums.PREDICTIONS].mean().round(2)

    return min_prediction, max_prediction, median_prediction, avg_prediction


def get_city_prediction(df: DataFrame):
    df_filtered_by_city: DataFrame = _filter_by_col_value(df, ColumnsEnums.CITY, "Available cities:")
    # df_by_city = df.groupby(ColumnsEnums.CITY)

    min_prediction, max_prediction, median_prediction, avg_prediction = _get_basics(df_filtered_by_city)

    print(min_prediction, max_prediction, avg_prediction, median_prediction)


def _filter_df_by_columns(df: DataFrame, cols: list):
    cols.append(ColumnsEnums.PREDICTIONS)
    return df.filter(cols)


def explor():
    df_with_predictions: DataFrame = _prepare_data_for_prediction()

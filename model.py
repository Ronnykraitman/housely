import pandas as pd
from pandas import DataFrame
from sklearn import tree

from data_prep import split_data
from model_enums import PredictorsEnums, TargetEnums, ColumnsEnums

dtr_model = tree.DecisionTreeRegressor()


def get_model(df: DataFrame):
    train, test = split_data(df)
    predictors = [f"{PredictorsEnums.NUMBER_OF_ROOMS}_encoded", f"{PredictorsEnums.CITY}_encoded", PredictorsEnums.YEAR]
    target = TargetEnums.PRICE

    trained_model = _fit_model(train, predictors, target)
    return trained_model


def _fit_model(train, predictors, target):
    return dtr_model.fit(train[predictors], train[target])


def predict(model, city_encoded: list, num_of_rooms_encoded: list, main_feature: str):
    city_encoded_for_prediction, num_of_rooms_encoded_prediction, year_list_for_prediction = build_features(
        city_encoded, num_of_rooms_encoded, main_feature)

    input_data_2024 = pd.DataFrame({
        'num_of_rooms_encoded': num_of_rooms_encoded_prediction,
        'city_encoded': city_encoded_for_prediction,
        'year': year_list_for_prediction
    })

    predictions = model.predict(input_data_2024)
    return list(map(lambda x: int(x.round(2) * 1000), predictions))


def build_features(first_feature_list: list, second_feature_list: list, main_feature: str):
    year_list_for_prediction: list = []
    num_of_rooms_encoded_prediction: list = []
    city_encoded_for_prediction: list = []

    if main_feature == ColumnsEnums.CITY:
        for first_value in first_feature_list:
            for second_value in second_feature_list:
                city_encoded_for_prediction.append(first_value)
                num_of_rooms_encoded_prediction.append(second_value)
                year_list_for_prediction.append(TargetEnums.YEAR_FOR_PREDICTION)
    else:
        for first_value in first_feature_list:
            for second_value in second_feature_list:
                city_encoded_for_prediction.append(second_value)
                num_of_rooms_encoded_prediction.append(first_value)
                year_list_for_prediction.append(TargetEnums.YEAR_FOR_PREDICTION)

    return city_encoded_for_prediction, num_of_rooms_encoded_prediction, year_list_for_prediction

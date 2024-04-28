from pandas import DataFrame
from data_encoder import encode_data
from data_prep import load_data, drop_nulls, split_data
from model import predict, get_model
from model_enums import PredictorsEnums, TargetEnums
from prediction_exploration import _prepare_data_for_prediction, _filter_by_col_value, get_city_prediction, \
    predict_by_city, predict_by_number_of_rooms, predict_by_district
from model_enums import PredictorsEnums, TargetEnums, ColumnsEnums

if __name__ == "__main__":
    df, mapping = _prepare_data_for_prediction()
    model = get_model(df)


    predict_by_city(model, mapping)
    predict_by_number_of_rooms(model, mapping)
    predict_by_district(model, mapping, df)


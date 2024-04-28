from data_prep import prepare_data_for_prediction
from model import get_model
from prediction_exploration import predict_by_city, predict_by_number_of_rooms, predict_by_district, \
    get_best_revenue_prediction
from model_enums import PredictorsEnums, TargetEnums, ColumnsEnums

if __name__ == "__main__":
    df, mapping = prepare_data_for_prediction()
    model = get_model(df)


    predict_by_city(model, mapping)
    predict_by_number_of_rooms(model, mapping)
    predict_by_district(model, mapping, df)
    get_best_revenue_prediction(model, mapping, df)


#!/usr/bin/env python3

import signal
from data_prep import prepare_data_for_prediction
from model import get_model
from prediction_exploration import predict_by_city, predict_by_number_of_rooms, predict_by_district, \
    get_apartments_by_user_asset, get_best_revenue_prediction
from utils import goodbye, generate_menu, _select_single_choice_index


logo = r'''
Welcome to
  _   _                      _          
 | | | | ___  _   _ ___  ___| |   _   _ 
 | |_| |/ _ \| | | / __|/ _ \ |  | | | |
 |  _  | (_) | |_| \__ \  __/ |__| |_| |
 |_| |_|\___/ \__,_|___/\___|_____\__, |
                                  |___/ 
                                  
                          Housing by ML
                          
'''

ml_predictions = [("Predict price by city", predict_by_city),
                  ("Predict price by number of rooms", predict_by_number_of_rooms),
                  ("Predict by price by district", predict_by_district),
                  ("Find you the best affordable place", get_apartments_by_user_asset),
                  ("Help you get the best revenue", get_best_revenue_prediction),
                  ("Exit", goodbye)]


def signal_handler(signal, frame):
    goodbye()


def start():
    df, mapping = prepare_data_for_prediction()
    model = get_model(df)
    menu_options: list = generate_menu(ml_predictions)
    index = _select_single_choice_index(menu_options, "I can:")
    match index:
        case 2 | 4:
            ml_predictions[index][1](model, mapping, df)
        case 3:
            ml_predictions[index][1](model, df)
        case 5:
            ml_predictions[index][1]()
        case _:
            ml_predictions[index][1](model, mapping)




if __name__ == "__main__":
    try:
        signal.signal(signal.SIGINT, signal_handler)
        print(logo)
        start()
    except Exception as e:
        print("Oh no. Something terrible happened. Lets start over :)")
        start()

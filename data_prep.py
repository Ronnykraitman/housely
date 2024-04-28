from pandas import DataFrame
import pandas as pd
from sklearn.model_selection import train_test_split
import os

from data_encoder import encode_data
from model_enums import PredictorsEnums


def load_data():
    script_dir = os.path.dirname(__file__)
    relative_path = os.path.join(script_dir, "data/housely_data.csv")

    df: DataFrame = pd.read_csv(relative_path)
    return df


def drop_nulls(df: DataFrame):
    df.replace('-', pd.NA, inplace=True)
    df.dropna(inplace=True)
    return df


def set_dtypes(df):
    df["avg_price"] = df["avg_price"].astype(float)
    return df


def split_data(df: DataFrame, test_ration=0.15):
    input_data = df.drop(['avg_price'], axis=1)
    output_data = df['avg_price']
    input_for_train, input_for_test, output_for_train, output_for_test = train_test_split(input_data, output_data,
                                                                                          test_size=test_ration)
    train: DataFrame = input_for_train.join(output_for_train)
    test: DataFrame = input_for_test.join(output_for_test)

    return train, test

def prepare_data_for_prediction():
    df_raw: DataFrame = load_data()
    df_no_nulls = drop_nulls(df_raw)
    df, mapping = encode_data(df_no_nulls, [PredictorsEnums.NUMBER_OF_ROOMS, PredictorsEnums.CITY])

    return df, mapping

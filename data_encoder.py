from pandas import DataFrame
from sklearn.preprocessing import LabelEncoder


def _update_encoding_map(label_mapping, encode_map: dict, key: str) -> dict:
    for encoded_value, original_value in label_mapping.items():
        encode_map[key].update({original_value:encoded_value})
    return encode_map


def encode_data(df: DataFrame, cols_to_encode: list) -> tuple:
    encode_map = {}
    label_encoder = LabelEncoder()

    for col in cols_to_encode:
        encode_map[col] = {}
        df[f"{col}_encoded"] = label_encoder.fit_transform(df[col])
        label_mapping = {index: label for index, label in enumerate(label_encoder.classes_)}
        encode_map = _update_encoding_map(label_mapping, encode_map, col)

    return df, encode_map

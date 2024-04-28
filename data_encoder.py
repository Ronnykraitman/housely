from pandas import DataFrame
from sklearn.preprocessing import LabelEncoder


def _update_encoding_map(label_mapping, encode_map: dict, key: str) -> dict:
    for encoded_value, original_value in label_mapping.items():
        encode_map[key].update({original_value: encoded_value})
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


def get_unencoded_keys_from_mapping(mapping: dict, main_key: str):
    main_key_dict: dict = mapping[main_key]
    return list(main_key_dict.keys())


def get_encoded_values(list_of_values: list, mapping: dict, main_key: str):
    encoded_dict: dict = mapping[main_key]
    list_of_values_encoded = []
    for value_to_encode in list_of_values:
        list_of_values_encoded.append(encoded_dict[value_to_encode])

    return list_of_values_encoded

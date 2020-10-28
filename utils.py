import pandas as pd
from typing import Dict, Any, Tuple
import logging
from pathlib import Path

from sklearn.preprocessing import StandardScaler

LOGGER = logging.getLogger(__name__)


def user_data_to_csv(df: pd.DataFrame, config: Dict[str, Any]) -> None:
    LOGGER.info("Saving data to csv file.")
    csv_path = Path(config["user_data_file_path"])
    df.to_csv(csv_path)


def user_top_artist_data_to_csv(df: pd.DataFrame, config: Dict[str, Any]) -> None:
    LOGGER.info("Saving artist data to csv file.")
    csv_path = Path(config["user_top_artist_data_file_path"])
    df.to_csv(csv_path)


def get_features(config):
    return [feature for feature in config["features"]]


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def scale_data(
    df: pd.DataFrame, config: Dict[str, Any], scaler: StandardScaler = None,
) -> Tuple[pd.DataFrame, Any]:
    """Scale specified columns of the dataframe.

    If scaler object is not provided, we will initiate scaler and fit_transforrm the data. If scaler
    object is provided we will only transform the data with the given scaler.

    Args:
        df: Data on which scaling is performed.
        scaler: Scaler object.

    Returns:
        Scaled dataframe.
    """
    features = get_features(config)
    if scaler:
        df.loc[:, features] = scaler.transform(df[features])
    else:
        if config["scaler"] == "standard_scaler":
            scaler = StandardScaler()
        df.loc[:, features] = scaler.fit_transform(df[features])

    return df, scaler

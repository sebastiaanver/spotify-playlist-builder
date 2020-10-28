import logging
import sys
import yaml
import pandas as pd
from pathlib import Path

from gather_data_user import User
from utils import user_data_to_csv, user_top_artist_data_to_csv, scale_data
from model import (
    cluster_data,
    classify_new_points,
    find_optimal_k,
    analyse_k_value,
    find_closest_points_per_cluster,
)

LOGGER = logging.getLogger(__name__)


def main():
    user = User(
        config["client_id"],
        config["client_secret"],
        config["redirect_uri"],
        config["scope"],
    )

    if config["gather_data"]:
        # Get data of the user's top songs.
        song_uris = user.get_top_songs_uris()
        user_data_df = user.get_song_data(song_uris)
        user_data_to_csv(user_data_df, config)

        # Get data of the user's top artists.
        user_top_artists_uris = user.get_top_artists_uris()
        user_data_top_artist_songs_df = user.get_song_data(user_top_artists_uris)
        user_top_artist_data_to_csv(user_data_top_artist_songs_df, config)

    if config["tune_parameters"]:
        find_optimal_k(config)
        analyse_k_value(6, config)

    # Read and process spotify data.
    df = pd.read_csv("data/spotify_songs.csv")
    df_scaled, scaler = scale_data(df, config)

    model, df_clustered = cluster_data(df_scaled, config)

    # Read and process user data.
    df_user = pd.read_csv("data/user_data.csv")
    df_user_scaled, _ = scale_data(df_user, config, scaler)

    # Find clusters for the user's songs.
    df_user_clustered = classify_new_points(df_user_scaled, model, config)

    # Find closest points.
    close_points = find_closest_points_per_cluster(
        df_clustered, df_user_clustered, config
    ).sample(n=100)
    close_songs_uris = close_points["uri"].drop_duplicates()

    # Create playlist with closest points.
    user.create_playlist(close_songs_uris)


if __name__ == "__main__":
    config = yaml.load(Path("config.yml").read_text(), Loader=yaml.SafeLoader)
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s %(name)-4s: %(module)-4s :%(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()

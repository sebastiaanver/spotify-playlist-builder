import logging
import time
import pandas as pd
from typing import Dict, Any, Tuple

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from scipy import spatial


from utils import get_features


LOGGER = logging.getLogger(__name__)


def find_optimal_k(config):
    start = time.time()
    LOGGER.info("Training..")
    df = pd.read_csv("data/spotify_songs.csv")
    features = get_features(config)
    df = df[features]

    n_clusters = range(2, 21)
    ssd = []
    sc = []

    scaler = StandardScaler()
    songs_scaled = scaler.fit_transform(df)

    for n in n_clusters:
        kmean = KMeans(
            n_clusters=n, max_iter=300, n_init=10, init="k-means++", random_state=42
        )
        kmean.fit(songs_scaled)
        preds = kmean.predict(songs_scaled)
        centers = kmean.cluster_centers_
        ssd.append(kmean.inertia_)
        score = silhouette_score(songs_scaled, preds, metric="euclidean")
        sc.append(score)
        print("Number of Clusters = {}, Silhouette Score = {}".format(n, score))


def analyse_k_value(k, config):
    start = time.time()
    LOGGER.info("Training..")
    df_songs = pd.read_csv("data/spotify_songs.csv")
    features = get_features(config)
    df = df_songs[features]

    scaler = StandardScaler()
    songs_scaled = scaler.fit_transform(df)

    model = KMeans(n_clusters=k, random_state=42).fit(songs_scaled)
    pred = model.predict(songs_scaled)
    print("10 first clusters: ", model.labels_[:10])

    df_songs_scaled = pd.DataFrame(songs_scaled, columns=features)

    df_songs_scaled["cluster"] = model.labels_

    df_songs_scaled["cluster"].value_counts().plot(kind="bar")
    plt.xlabel("Cluster")
    plt.ylabel("Amount of songs")
    plt.title("Amount of songs per cluster")
    plt.show()

    df_songs_joined = pd.concat([df_songs, df_songs_scaled], axis=1).set_index(
        "cluster"
    )
    for cluster in range(k):
        print(df_songs_joined.loc[cluster, ["id"]].sample(frac=1).head(10))


def cluster_data(df: pd.DataFrame, config: Dict[str, Any]) -> Tuple[Any, pd.DataFrame]:
    start = time.time()
    LOGGER.info("Training..")

    features = get_features(config)
    kmeans = KMeans(n_clusters=6, random_state=0).fit(df[features])

    df["cluster"] = kmeans.labels_

    LOGGER.info("Training took: %.2f s", time.time() - start)

    return kmeans, df


def classify_new_points(
    df: pd.DataFrame, model: Any, config: Dict[str, Any]
) -> pd.DataFrame:
    """Classify unseen point, i.e. assign cluster."""
    features = get_features(config)
    df["cluster"] = model.predict(df[features])

    return df


def find_closest_points_per_cluster(
    spotify_df: pd.DataFrame, user_df: pd.DataFrame, config: Dict[str, Any]
) -> pd.DataFrame:
    """Find closest points to the user's song within the cluster."""
    clusters = spotify_df["cluster"].unique()
    features = get_features(config)

    close_points = pd.DataFrame()

    features = get_features(config)
    for cluster in clusters:
        spotify_df_cluster = spotify_df[spotify_df["cluster"] == cluster]
        user_df_cluster = user_df[user_df["cluster"] == cluster]

        spotify_df_cluster = spotify_df_cluster
        user_df_cluster = user_df_cluster

        tree = spatial.KDTree(spotify_df_cluster[features].values)
        idx = tree.query(user_df_cluster[features].values, k=5)[-1]

        idx = [i for ids in idx for i in ids]

        closes_songs = spotify_df_cluster.iloc[idx, :]
        close_points = close_points.append(closes_songs)

    close_points.drop_duplicates(inplace=True)
    close_points = close_points[
        close_points.apply(lambda x: x.uri not in user_df.uri, axis=1)
    ]
    return close_points

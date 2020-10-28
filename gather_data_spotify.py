import pandas as pd
import utils as utils


def get_audio_features_from_playlist_songs(playlists: str) -> pd.DataFrame:
    track_ids = []
    songs_info = []

    for playlist in playlists["items"]:
        print(str(i) + " - " + playlist["name"])
        results = sp.playlist(playlist["id"], fields="tracks(items(track(id)), next)")
        tracks = results["tracks"]
        track_ids += [
            track["track"]["id"]
            for track in tracks["items"]
            if track["track"]
            if track["track"]["id"]
        ]
        while tracks["next"]:
            tracks = sp.next(tracks)
            track_ids += [
                track["track"]["id"]
                for track in tracks["items"]
                if track["track"]
                if track["track"]["id"]
            ]

    songs_info = pd.DataFrame()
    for chunck in utils.chunks(track_ids, 100):
        try:
            songs_info = songs_info.append(
                pd.DataFrame([i for i in sp.audio_features(chunck) if i]),
                ignore_index=True,
            )
        except:
            pass

    return songs_info

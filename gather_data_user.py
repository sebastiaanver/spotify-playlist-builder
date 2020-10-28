import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import namegenerator
import logging
import time

from typing import Dict, Any, List

LOGGER = logging.getLogger(__name__)


class User:
    def __init__(self, client_id, client_secret, redirect_uri, scope):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.sp = self.initialize()
        self.user_id = self.sp.me()["id"]

    def initialize(self) -> spotipy.Spotify:
        """Initialize spotipy object."""
        return spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
            )
        )

    def get_top_songs_uris(self) -> Dict[str, Any]:
        """Get the uris of the user's top songs.

        Return:
            Dictionary with the uris per time range.
        """
        start = time.time()
        LOGGER.info("Gathering top songs of user.")

        data = {}
        for time_range in ["long_term", "medium_term", "short_term"]:
            top_songs = self.sp.current_user_top_tracks(
                limit=50, offset=0, time_range=time_range
            )
            data[time_range] = [song["uri"] for song in top_songs["items"]]

        LOGGER.info("Gathering top songs took: %.2f s", time.time() - start)
        return data

    def get_song_data(self, songs_uris: Dict[str, List]) -> pd.DataFrame:
        """Get all song features for the different time ranges.

        Returns:
            Dataframe containing all song features.
        """
        start = time.time()
        LOGGER.info("Gathering top song data of user.")

        song_features = pd.DataFrame()
        for time_range, data in songs_uris.items():
            for song_uri in data:
                song_info = self.sp.audio_features(song_uri)[0]
                song_info["time_range"] = time_range
                song_features = song_features.append(song_info, ignore_index=True)

        LOGGER.info("Gathering top song data took: %.2f s", time.time() - start)
        return song_features

    def get_playlist_from_user(self, user_id: str) -> Dict:

        playlists = self.sp.user_playlists(user_id, limit=50)
        all_playlists = {"items": []}
        while playlists:
            all_playlists["items"] += playlists["items"]
            if playlists["next"]:
                playlists = self.sp.next(playlists)
            else:
                break
        return all_playlists

    def get_top_artists_uris(self) -> Dict:
        start = time.time()
        LOGGER.info("Gathering top artists of user.")

        data = {}

        # Get top artists for different time ranges.
        for time_range in ["long_term", "medium_term", "short_term"]:
            top_artists = self.sp.current_user_top_artists(
                limit=50, offset=0, time_range=time_range
            )
            top_artists_uris = [artist["uri"] for artist in top_artists["items"]]

            data[time_range] = []

            # Get top tracks for each artist.
            for artist_uri in top_artists_uris:
                top_tracks = self.sp.artist_top_tracks(artist_uri)["tracks"]
                top_track_uris = [track["uri"] for track in top_tracks]
                data[time_range].append(top_track_uris)

        LOGGER.info("Gathering top artists took: %.2f s", time.time() - start)
        return data

    def create_playlist(self, songs, playlist_name=None):

        # Generate random playlist name if non was given.
        if not playlist_name:
            playlist_name = namegenerator.gen()

        LOGGER.info(f"Adding {len(songs)} to {playlist_name}.")
        playlists = self.sp.user_playlists(self.user_id)
        play_list_id = [
            playlist["id"]
            for playlist in playlists["items"]
            if playlist["name"] == playlist_name
        ]

        # Check if playlist already exists.
        if len(play_list_id) == 0:

            self.sp.user_playlist_create(self.user_id, playlist_name, public=True)

            playlists = self.sp.user_playlists(self.user_id)
            play_list_id = [
                playlist["id"]
                for playlist in playlists["items"]
                if playlist["name"] == playlist_name
            ]

            if len(play_list_id) > 0:
                self.sp.playlist_add_items(play_list_id[0], songs)
            else:
                LOGGER.info(f"Playlist name does not exists, songs are not added.")
                raise ValueError
        else:
            LOGGER.info(f"Playlist name does already exist.")
            raise ValueError

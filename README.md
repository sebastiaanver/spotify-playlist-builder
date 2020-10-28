# spotify-playlist-builder
This project was build during a hackathon organized by the KTH AI Society in approximately 10 hrs. 

The goal was to build a program that could create a new playlist based on the music that was listened to by the specified user most recently.


### configuration
Before running the program a few things need to be initialized:

* After creating a project on [Spotify's Developer portal](https://developer.spotify.com/dashboard/) both the `client_id` and `client_secret` can  be found and should be configured in `config.yml`.
* In [Spotify's Developer portal](https://developer.spotify.com/dashboard/) the `Redirect URI` should be set  according to the one specified in `config.yml`.


### running the program
Run the program by executing `python3 run main.py`.

## Program
The program consists of a few parts explained below.

### scraper
The scraper retrieves data from two sources:
* **Spotify playlist data**: Gathering all songs in spotify's public playlists.
* **User data**: Gathering the set of songs the user listened to most recently.

For each song the following features were collected:
* danceability
* energy
* key
* loudness
* mode
* speechiness
* acousticness
* instrumentalness
* liveness
* valence
* tempo
* duration_ms

### recommender
The recommender clusters the tracks from spotify's public playlists and find songs that are in the same clusters (and  close to ) as your recenlty listened tracks.

### playlist builder
The playlist builder takes the  recommended music and exports it to  a playlist created for the specified user. If no name  is  given a random name will be generated (e.g. thirsty-firebrick-snake)

from bs4 import BeautifulSoup
import requests
import spotipy
import dotenv
env = dotenv.dotenv_values()

spotify_id = env["SPOTIPY_CLIENT_ID"]
spotify_secret = env["SPOTIPY_CLIENT_SECRET"]
redirect_uri = "http://example.com"
scope = "playlist-modify-public"
auth = spotipy.oauth2.SpotifyOAuth(client_id=spotify_id, client_secret=spotify_secret, scope=scope,
                                   redirect_uri=redirect_uri, show_dialog=True)
auth.get_access_token(as_dict=False)
sp = spotipy.Spotify(auth_manager=auth)
user = sp.current_user()["id"]
user_input = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
try:
    res = requests.get(f"https://www.billboard.com/charts/hot-100/{user_input}")
    website = res.text
except Exception as e:
    print(e)
soup = BeautifulSoup(website, "html.parser")
songs = [song.string for song in soup.find_all(name="span",
                                               class_="chart-element__information__song text--truncate color--primary")]
year = user_input.split("-")[0]
song_uris = []
for song in songs:
    result = sp.search(q=song, type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{songs} doesn't exist in Spotify. Skipped.")
name = f'{soup.find("span", class_="sr--only").string} Week of {user_input}'
playlist = sp.user_playlist_create(user=user, name=name, public=True,
                                   description=f"The most songs listened Week of {user_input}")
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

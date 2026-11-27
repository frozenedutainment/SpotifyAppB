import streamlit as st


import spotipy
from spotipy.oauth2 import SpotifyOAuth

client = "9bd1a21279374ad09d28eec5b42406a4"
secret = "cc88755b6c8a442ca7bd4e74593dae6d"
redir = "http://127.0.0.1:8000/callback"
scope = "user-read-currently-playing"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client,
    client_secret=secret,
    redirect_uri=redir,
    scope=scope
))


gems = data.gems()


likert_scale = {0 : "unranked",1 : "Not at all", 2 : "Somewhat", 3 : "Moderatly", 4 :  "Quite a lot", 5 : "Very much"}

items = ["Wonder", "Transcendence", "Nostalgia", "Tenderness", "Joyful Activation", "Power", "Tension", "Sadness", "Anxiety"]

song_cont = st.container(border = True)

refresh_button = st.button("Refresh")

if "refreshtoggle" not in st.session_state:
    st.session_state.refreshtoggle = 0

if refresh_button:
    st.session_state.refreshtoggle = 1
    if st.session_state.refreshtoggle == 1:
        with song_cont:
            current_song = sp.currently_playing()
            if current_song is not None:
                col1, col2 = st.columns([1,3])
                with col2:
                    st.markdown(f" ## {current_song["item"]["name"]}")
                with col1:
                    cover_url = current_song['item']['album']['images'][0]['url']
                    st.image(cover_url, width=150)




        with st.container (border = True):
            for n in items:
                st.slider(n,0,5, 0)

    submit_button = st.button("Submit")

    if submit_button:
        pass
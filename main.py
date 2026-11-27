import streamlit as st


import data as data
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import log_in

if "user_id" not in st.session_state:
    st.session_state.user_id = log_in.log_in()

client = st.secrets["SPOTIFY_CLIENT_ID"]
secret = st.secrets["SPOTIFY_CLIENT_SECRET"]
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

items = ["Wonder", "Transcendence", "Nostalgia", "Tenderness", "Joyful_Activation", "Power", "Tension", "Sadness", "peacefulness", "Bewertung"]

song_cont = st.container(border = True)

refresh_button = st.button("Refresh")

if "refreshtoggle" not in st.session_state:
    st.session_state.refreshtoggle = 0

if refresh_button:
    st.session_state.current = sp.currently_playing()
    current_song = st.session_state.current

if refresh_button or  st.session_state.refreshtoggle == 1:
    st.session_state.refreshtoggle = 1
    if st.session_state.refreshtoggle == 1:
        with song_cont:
            if "current" not in st.session_state:
                st.session_state.current = sp.currently_playing()
                current_song = st.session_state.current

            if st.session_state.current is not None:
                col1, col2 = st.columns([1,3])
                with col2:
                    st.markdown(f" ## {st.session_state.current["item"]["name"]}")
                with col1:
                    cover_url = st.session_state.current['item']['album']['images'][0]['url']
                    st.image(cover_url, width=150)






        with st.container (border = True):
            counter = 3
            if "current" in st.session_state:
                current_gem_stats = gems.get_var("song_id", st.session_state.current["item"]["id"])

            for n in items:
                val = 0  # Default

                if current_gem_stats is not None and current_gem_stats != []:
                    if counter < len(current_gem_stats):
                        raw_val = current_gem_stats[counter]

                        # FIX: Falls raw_val ein Tupel/Liste ist, nimm das erste Element
                        if isinstance(raw_val, (tuple, list)):
                            val = int(raw_val[0]) if raw_val else 0
                        else:
                            # Falls es None ist oder ein falscher Typ, zu 0 konvertieren
                            try:
                                val = int(raw_val) if raw_val is not None else 0
                            except:
                                val = 0
                if n != "Bewertung":
                    st.slider(n, 0, 5, val, key=f"slider_{n}")
                elif n == "Bewertung":
                    st.slider(n, 0, 100, val, key=f"slider_{n}")

                counter += 1
    submit_button = st.button("Submit")




    if submit_button:

        cur_id = st.session_state.current["item"]["id"]
        cur_name = st.session_state.current["item"]["name"]

        wonder = st.session_state.slider_Wonder
        transcendence = st.session_state.slider_Transcendence
        nostalgia = st.session_state.slider_Nostalgia
        tenderness = st.session_state.slider_Tenderness
        joyful_activation = st.session_state.slider_Joyful_Activation
        power = st.session_state.slider_Power
        tension = st.session_state.slider_Tension
        sadness = st.session_state.slider_Sadness
        peacefulness = st.session_state.slider_peacefulness
        with st.container(border = True):
            bewertung = st.session_state.slider_Bewertung

        gems.add_ranking(st.session_state.user_id,cur_id, cur_name, wonder, transcendence, nostalgia, tenderness, joyful_activation, power, tension, sadness, peacefulness, bewertung)
        print("added", wonder, transcendence, nostalgia, tenderness, joyful_activation,power, tension, sadness, peacefulness, bewertung)
        print("wow")

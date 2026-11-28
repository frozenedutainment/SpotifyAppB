import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler
import data
import log_in

client = st.secrets["SPOTIFY_CLIENT_ID"]
secret = st.secrets["SPOTIFY_CLIENT_SECRET"]
redir = "https://spotifyappb.streamlit.app/"  # Exakt wie im Spotify Dashboard!
scope = "user-read-currently-playing"


st.session_state.user_id = log_in.log_in()

# Token nur im Session State dieses einen Nutzers speichern (keine .cache-Datei)
cache_handler = MemoryCacheHandler(token_info=st.session_state.get("spotify_token"))

auth_manager = SpotifyOAuth(
    client_id=client,
    client_secret=secret,
    redirect_uri=redir,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True  # Zeigt den Spotify-Login-Dialog für Account-Wechsel
)

# 1. Nutzer kommt gerade von Spotify zurück (URL enthält ?code=...)
if "code" in st.query_params:
    code = st.query_params["code"]
    token_info = auth_manager.get_access_token(code, as_dict=True)
    st.session_state["spotify_token"] = token_info
    st.query_params.clear()
    st.rerun()

# 2. Nutzer ist noch nicht mit Spotify verbunden -> Login-Button zeigen
if not st.session_state.get("spotify_token"):
    auth_url = auth_manager.get_authorize_url()
    st.link_button("🎧 Mit eigenem Spotify-Account verbinden", auth_url)
    st.stop()



# 3. Token ggf. automatisch erneuern & Spotipy starten
token_info = auth_manager.validate_token(st.session_state["spotify_token"])
st.session_state["spotify_token"] = token_info
sp = spotipy.Spotify(auth=token_info["access_token"])

gems = data.gems()

likert_scale = {0: "unranked", 1: "Not at all", 2: "Somewhat", 3: "Moderatly", 4: "Quite a lot", 5: "Very much"}
items = ["Wonder", "Transcendence", "Nostalgia", "Tenderness", "Joyful_Activation", "Power", "Tension", "Sadness", "Peacefulness", "Bewertung"]

song_cont = st.container(border=True)
refresh_button = st.button("Refresh")

if "refreshtoggle" not in st.session_state:
    st.session_state.refreshtoggle = 0

if refresh_button:
    st.session_state.current = sp.currently_playing()

if refresh_button or st.session_state.refreshtoggle == 1:
    st.session_state.refreshtoggle = 1

    # GEÄNDERT: Doppeltes "if st.session_state.refreshtoggle == 1:" entfernt
    with song_cont:
        if "current" not in st.session_state:
            st.session_state.current = sp.currently_playing()

        # GEÄNDERT: Zusätzlich geprüft, ob "item" existiert (verhindert Absturz, wenn Spotify pausiert/nichts spielt)
        if st.session_state.get("current") is not None and st.session_state.current.get("item") is not None:
            col1, col2 = st.columns([1, 3])
            with col2:
                # GEÄNDERT: Einfache Anführungszeichen im f-String für saubere Syntax
                st.markdown(f"## {st.session_state.current['item']['name']}")
            with col1:
                cover_url = st.session_state.current['item']['album']['images'][0]['url']
                st.image(cover_url, width=150)
        else:
            # GEÄNDERT: Hinweis hinzugefügt, falls kein Song läuft
            st.info("Aktuell wird kein Song auf Spotify abgespielt.")

    with st.container(border=True):
        # GEÄNDERT: Vorher initialisiert, damit es keinen NameError gibt, wenn kein Song läuft
        current_gem_stats = None

        # GEÄNDERT: Sicherer Check auf None + Kreuzsuche mit "user_id" ergänzt
        if st.session_state.get("current") is not None and st.session_state.current.get("item") is not None:
            rows = gems.get_var(
                "song_id", st.session_state.current["item"]["id"],
                "user_id", st.session_state.user_id
            )
            # GEÄNDERT: Erste Zeile (Tupel) aus der Ergebnis-Liste herausholen, sonst bleibt die Länge immer 1
            if rows:
                current_gem_stats = rows[0]

        # GEÄNDERT: Startwert von 3 auf 4 erhöht (0=id, 1=user_id, 2=song_id, 3=track_name, 4=wonder)
        counter = 4
        for n in items:
            val = 0
            if current_gem_stats is not None and counter < len(current_gem_stats):
                raw_val = current_gem_stats[counter]
                # GEÄNDERT: Vereinfacht, da current_gem_stats jetzt direkt die Zeile (Tupel) ist
                try:
                    val = int(raw_val) if raw_val is not None else 0
                except (ValueError, TypeError):
                    val = 0

            if n != "Bewertung":
                st.slider(n, 0, 5, val, key=f"slider_{n}")
            else:
                st.slider(n, 0, 100, val, key=f"slider_{n}")

            counter += 1

    submit_button = st.button("Submit")

    if submit_button:
        # GEÄNDERT: Schutz vor Absturz, falls auf Submit geklickt wird, wenn kein Song läuft
        if st.session_state.get("current") is not None and st.session_state.current.get("item") is not None:
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
            peacefulness = st.session_state.slider_Peacefulness
            # GEÄNDERT: Unnötigen "with st.container(border = True):" entfernt
            bewertung = st.session_state.slider_Bewertung

            # GEÄNDERT: st.session_state.user_id als ersten Parameter übergeben
            gems.add_ranking(
                st.session_state.user_id,
                cur_id, cur_name,
                wonder, transcendence, nostalgia, tenderness,
                joyful_activation, power, tension, sadness, peacefulness, bewertung
            )
            # GEÄNDERT: Visuelles Feedback in der App hinzugefügt
            st.success(f"Bewertung für '{cur_name}' gespeichert!")
            print("added", wonder, transcendence, nostalgia, tenderness, joyful_activation, power, tension, sadness, peacefulness, bewertung)
        else:
            st.warning("Kein aktiver Song zum Speichern gefunden.")
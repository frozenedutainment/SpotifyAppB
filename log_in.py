import streamlit as st
import extra_streamlit_components as stx
import datetime
import hashlib


def log_in():
    st.set_page_config(page_title="Meine Mobile App")

    # --- ZUGANGSDATEN DIREKT IM CODE (FÜRS ERSTE TESTEN) ---
    USERS = {
        "admin": "wow",
        "blokz": "small",
        "freund": "NochEinPasswort456!",
    }
    COOKIE_SECRET = "ein_langer_zufaelliger_geheimschluessel_fuer_cookies"
    COOKIE_NAME = "spotify_app_auth"

    cookie_manager = stx.CookieManager()


    def make_token(username: str, password: str, secret: str) -> str:
        raw = f"{username}:{password}:{secret}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()


    # Alle gültigen Tokens für konfigurierte Benutzer berechnen
    VALID_TOKENS = {
        make_token(user, pw, COOKIE_SECRET): user
        for user, pw in USERS.items()
    }

    # Cookie auslesen
    cookies = cookie_manager.get_all()
    auth_cookie = cookies.get(COOKIE_NAME)

    if auth_cookie in VALID_TOKENS:
        st.session_state["authenticated"] = True
        st.session_state["username"] = VALID_TOKENS[auth_cookie]

    # --- LOGIN-BEREICH ---
    if not st.session_state.get("authenticated", False):
        st.title("🔒 Login")

        with st.form("login_form"):
            username = st.text_input("Benutzername").strip()
            password = st.text_input("Passwort", type="password")
            remember_me = st.checkbox("Angemeldet bleiben (30 Tage)", value=True)
            submit = st.form_submit_button("Einloggen")

            if submit:
                expected_pw = USERS.get(username)
                if expected_pw is not None and password == expected_pw:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username

                    if remember_me:
                        token = make_token(username, password, COOKIE_SECRET)
                        expires = datetime.datetime.now() + datetime.timedelta(days=30)
                        cookie_manager.set(
                            COOKIE_NAME,
                            token,
                            expires_at=expires,
                            key="set_auth_cookie",
                        )
                    st.rerun()
                else:
                    st.error("Benutzername oder Passwort falsch.")

        st.stop()



    # --- GESCHÜTZTER BEREICH ---
    st.title("📱 Willkommen!")
    st.write(f"Eingeloggt als **{st.session_state.get('username')}**.")

    if st.sidebar.button("Ausloggen"):
        cookie_manager.delete(COOKIE_NAME)
        st.session_state["authenticated"] = False
        st.session_state.pop("username", None)
        st.rerun()

    return st.session_state.get("username")


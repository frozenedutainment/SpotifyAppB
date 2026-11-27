import streamlit as st
import spotipy
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, date
from collections import Counter
import json
from spotipy.oauth2 import SpotifyOAuth



from sphinx.util.display import progress_message


class spotify:
    def __init__(self):
        client = "9bd1a21279374ad09d28eec5b42406a4"
        secret = "cc88755b6c8a442ca7bd4e74593dae6d"
        redir = "http://127.0.0.1:8000/callback"
        scope = "user-read-currently-playing"

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client,
            client_secret=secret,
            redirect_uri=redir,
            scope=scope
        ))

    def current(self):
        return self.sp.currently_playing()

    def get(self, song_id):
        return self.sp.track(song_id)

class sqlite_db:
    def __init__(self):
        self.conn = sqlite3.connect('data_new.db')
        self.cursor = self.conn.cursor()
        self.setup()
    def setup(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS save_stamp_2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_key TEXT,
                song_id TEXT,
                track_name TEXT NOT NULL,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                progress_ms INTEGER,
                synced INTEGER
            )
        ''')
    def add(self,stamp):

        id = stamp["id"]
        song_id = stamp["song_id"]
        track_name = stamp["track_name"]
        played_at = stamp["played_at"]
        progress_ms = stamp["progress_ms"]
        synced = 1

        self.cursor.execute('''
                INSERT OR IGNORE INTO save_stamp_2 
                (id, song_id, track_name, played_at, progress_ms, synced)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (id, song_id, track_name, played_at, progress_ms, synced))

        self.conn.commit()

    def get_var(self, var, value):

        allowed_columns = ['id', 'song_id', 'track_name', 'played_at', 'progress_ms', 'synced', 'all']

        if var not in allowed_columns:
            raise ValueError(f"Ungültige Spalte: {var}")

        if var == "all":
            query = f"SELECT {value} FROM save_stamp_2"

            self.cursor.execute(query)
        else:
            query = f"SELECT * FROM save_stamp_2 WHERE {var} = ?"

            self.cursor.execute(query, (value,))
        return self.cursor.fetchall()

    def get_all(self):
        query = f"SELEcT * FROM save_stamp_2"
        self.cursor.execute(query)
        return self.cursor.fetchall()

class song_lib:
    def __init__(self):
        self.conn = sqlite3.connect('data_new.db')
        self.tab = "song_lib"
        self.cursor = self.conn.cursor()
        self.setup()

    def setup(self):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tab} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id TEXT UNIQUE,
                track_name TEXT NOT NULL,
                full_ms INTEGER,
                extras TEXT
            )
        ''')
    def add(self, full_song_dict):

        if full_song_dict is not None:
            if self.get(full_song_dict["item"]["id"]) != []:
                return None
            song_id = full_song_dict["item"]["id"]
            track_name = full_song_dict["item"]["name"]
            full_ms = full_song_dict["item"]["duration_ms"]
            extras = json.dumps(full_song_dict)

            self.cursor.execute(f'''
                            INSERT OR IGNORE INTO {self.tab}
                            (song_id, track_name, full_ms, extras)
                            VALUES (?, ?, ?, ?)
                        ''', (song_id, track_name, full_ms, extras))

            self.conn.commit()
        else:
            return None

    def get(self, song_id):
        query = f"SELECT * FROM {self.tab} WHERE song_id = ?"
        self.cursor.execute(query, (song_id,))
        row = self.cursor.fetchone()

        if row is None:
            return []

        return {
            "col_id": row[0],
            "song_id": row[1],
            "track_name": row[2],
            "full_ms": row[3],
            "extras": json.loads(row[4]),
        }

        return {"col_id" : col_id, "song_id" : song_id, "track_name" : track_name, "full_ms" : full_ms, "extras" : extras}

    def get_all(self):
        query = f"SELECT * FROM {self.tab}"
        self.cursor.execute(query)
        return self.cursor.fetchall()




class gems:
    def __init__(self):
        self.conn = sqlite3.connect('data_new.db')
        self.cursor = self.conn.cursor()
        self.setup()

    def setup(self):
        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS extra_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        song_id TEXT,
                        track_name TEXT NOT NULL,
                        wonder INTEGER,
                        transcendence INTEGER,
                        nostalgia INTEGER,
                        tenderness INTEGER,
                        joyful_activation INTEGER,
                        power INTEGER,
                        tension INTEGER,
                        sadness INTEGER,
                        peacefulness INTEGER,
                        bewertung INTEGER
                    )
                ''')

    def add_ranking(self, user_id, song_id, track_name, wonder, transcendence, nostalgia, tenderness, joyful_activation, power, tension, sadness, peacefulness, bewertung):
        # GEÄNDERT: Nach oben verschoben, damit get_var schon nach "admin" statt None sucht
        if user_id is None:
            user_id = "admin"

        added_ids_by_user = self.get_var("all", "song_id", "user_id", user_id)

        if song_id in added_ids_by_user:
            self.cursor.execute('''
                UPDATE extra_data
                -- GEÄNDERT: "user_id = ?" hier entfernt, da die user_id im WHERE geprüft wird
                SET wonder = ?, 
                    transcendence = ?, 
                    nostalgia = ?, 
                    tenderness = ?, 
                    joyful_activation = ?, 
                    power = ?, 
                    tension = ?, 
                    sadness = ?, 
                    peacefulness = ?,
                    bewertung = ?
                -- GEÄNDERT: "AND user_id = ?" ergänzt, damit nur der Eintrag dieses Nutzers aktualisiert wird
                WHERE song_id = ? AND user_id = ?
            -- GEÄNDERT: user_id im Tupel von ganz vorne nach ganz hinten (passend zum WHERE) verschoben
            ''', (wonder, transcendence, nostalgia, tenderness, joyful_activation, power, tension, sadness, peacefulness, bewertung, song_id, user_id))
            print("update", song_id)
            self.conn.commit()
        else:
            self.cursor.execute('''
                INSERT INTO extra_data
                (user_id, song_id, track_name, wonder, transcendence, nostalgia, tenderness, joyful_activation, power, tension, sadness, peacefulness, bewertung)
                -- GEÄNDERT: 13. Fragezeichen ergänzt (vorher waren es nur 12 für 13 Spalten)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, song_id, track_name, wonder, transcendence, nostalgia, tenderness, joyful_activation, power, tension, sadness, peacefulness, bewertung))
            self.conn.commit()
            print("added", song_id)


    def del_id(self,song_id):
        self.cursor.execute('DELETE FROM extra_data WHERE song_id = ?', (song_id,))
        self.conn.commit()
        print(f"Song {song_id} wurde gelöscht.")

    def get_var(self, var1, val1, var2=None, val2=None):
        """
        Szenario 1: get_var("id", 5) -> Zeile mit ID 5
        Szenario 2: get_var("all", "track_name") -> Alle Track-Namen als Liste
        Szenario 3: get_var("all", "song_id", "user_id", "user1") -> Alle song_ids von user1 als Liste
        Szenario 4: get_var("user_id", "user1", "song_id", "abc") -> Zeile mit user1 UND song abc
        """
        if var1 == "all":
            if var2 is not None:
                query = f"SELECT {val1} FROM extra_data WHERE {var2} = ?"
                self.cursor.execute(query, (val2,))
            else:
                query = f"SELECT {val1} FROM extra_data"
                self.cursor.execute(query)
            return [row[0] for row in self.cursor.fetchall()]
        else:
            if var2 is not None:
                query = f"SELECT * FROM extra_data WHERE {var1} = ? AND {var2} = ?"
                self.cursor.execute(query, (val1, val2))
            else:
                query = f"SELECT * FROM extra_data WHERE {var1} = ?"
                self.cursor.execute(query, (val1,))
            return self.cursor.fetchall()

    def get_all(self):
        self.cursor.execute("SELECT * FROM extra_data")
        return self.cursor.fetchall()

    def gems_items(self):
        return ["wonder", "transcendence", "nostalgia", "tenderness", "joyful_activation", "power", "tension", "sadness", "peacefulness"]

class analytics:
    def __init__(self):
        self.sql = sqlite_db()

    def day_stamps(self):
        data = self.sql.get_var("all", "played_at")

        sorteddict = {}
        for n in data:
            dt_obj = datetime.fromisoformat(n[0])
            tag = dt_obj.date()

            if tag not in sorteddict:
                sorteddict[tag] = []
            sorteddict[tag].append(dt_obj)
        return sorteddict

    def get_hourly_of_day(self, day_list):
        counts = Counter(dt.hour for dt in day_list)
        return {hour: counts.get(hour, 0) for hour in range(24)}

    def get_avg_hourly_of_day(self, day_stamps_dict):
        combineddict = {hour: [] for hour in range(24)}

        # FEHLER WAR HIER: Du musst über die VALUES (die Listen der Zeitstempel) loopen
        for day_list in day_stamps_dict.values():
            # Berechne die Verteilung für diesen einen Tag
            day_counts = self.get_hourly_of_day(day_list)

            # Füge die Counts der jeweiligen Stunde zum combineddict hinzu
            for hour in range(24):
                combineddict[hour].append(day_counts[hour])

        # Durchschnitt berechnen
        avg_dict = {}
        for hour, counts_list in combineddict.items():
            avg_dict[hour] = sum(counts_list) / len(counts_list) if counts_list else 0

        return avg_dict

    def get_stamps_day(self,date_inp):
        day_sorted = self.day_stamps()
        if date_inp in day_sorted:
            data = day_sorted[date_inp]
            return data
        else:
            return {}

    def get_week(self):
        heute = datetime.now().date()
        week = []
        for i in range(6,-1,-1):
            week.append(heute - timedelta(days=i))
        week_stamps = []
        for n in week:
            week_stamps.append(self.get_stamps_day(n))

        return week_stamps
    def get_stats_week(self):
        pass

    def one_song(self, song_id):
        stamps = self.sql.get_var("song_id",song_id)
        stamp_list = []

        return [datetime.fromisoformat(n[3]) for n in stamps]

    def get_top_songs(self,amount):
        all = self.sql.get_all()
        dictbyid = {}

        for n in all:
            if n[1] not in dictbyid:
                dictbyid[n[1]] = [n[3]]
            elif n[1] in dictbyid:
                dictbyid[n[1]].append(n[3])
        lendict = {}
        for n in dictbyid:
            lendict[n] = len(dictbyid[n])

        counts = Counter(lendict)
        top_n = counts.most_common(amount)
        print(top_n)

        return top_n





#song_lib.get()
#gems = gems()
#tag = datetime(2026, 3, 1).date()
#sql = sqlite_db()
#analytic.get_top_songs(5)
#print(analytic.day_stamps())
#print(analytic.get_avg_hourly_of_day(analytic.day_stamps()))



GEMS = gems()
print(GEMS.get_all())






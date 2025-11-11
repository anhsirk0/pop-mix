#!/usr/bin/env python3

from dataclasses import dataclass
from typing import List
import time
import sqlite3
import os


@dataclass
class Playlist:
    id: int
    name: str


class Track:
    def __init__(self, id: int, name: str, uri: str, artist: str, album: str):
        self.id: int = id
        self.name: str = name
        self.uri: str = uri
        self.artist: str = artist
        self.album: str = album

    def __repr__(self) -> str:
        return f"{self.name} ⦑{self.artist}⦒「{self.album}」"


class LollypopPlaylist:
    def __init__(self):
        PLAYLIST_DB = "~/.local/share/lollypop/playlists.db"
        self.connection = sqlite3.connect(os.path.expanduser(PLAYLIST_DB))
        self.cursor = self.connection.cursor()

    def get_all(self) -> List[str]:
        self.cursor.execute("""
        select id, name from playlists
        """)
        rows = self.cursor.fetchall()
        return [Playlist(row[0], row[1]) for row in rows]

    def insert_uris_into_playlist(self, playlist_id: int, tracks_uri: List[str]):
        insert_query = "insert into tracks (playlist_id, uri) values (?, ?)"
        data = [(playlist_id, uri) for uri in tracks_uri]
        self.cursor.executemany(insert_query, data)
        self.connection.commit()

    def create(self, name: str, tracks_uri: List[str]):
        all_playlists = self.get_all()
        exists = len([plist for plist in all_playlists if plist.name == name]) > 0
        if exists:
            print(f"Playlist already exists")
            name = f"{name}_{int(time.time())}"
        self.cursor.execute(
            f"insert into playlists (name, mtime) values ('{name}', current_timestamp)"
        )
        playlist_id = self.cursor.lastrowid
        if playlist_id:
            self.insert_uris_into_playlist(playlist_id, tracks_uri)

    def close(self):
        self.connection.close()


class Lollypop:
    def __init__(self):
        LOLLYPOP_DB = "~/.local/share/lollypop/lollypop.db"
        self.connection = sqlite3.connect(os.path.expanduser(LOLLYPOP_DB))
        self.cursor = self.connection.cursor()

    def get_tracks(self) -> List[Track]:
        self.cursor.execute("""
        select tracks.id, tracks.name, tracks.uri, artists.name, albums.name from tracks
        join track_artists on track_artists.track_id = tracks.id
        join artists on track_artists.artist_id = artists.id
        join albums on tracks.album_id = albums.id
        """)
        rows = self.cursor.fetchall()
        return [
            Track(
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
            )
            for row in rows
        ]

    def close(self):
        self.connection.close()


def main():
    l = Lollypop()
    for track in l.get_tracks():
        print(track)
    l.close()
    # p = LollypopPlaylist()
    # for playlist in p.get_all():
    #     print(playlist)
    # p.create("New", ["file://myfile"])
    # p.close()


if __name__ == "__main__":
    main()

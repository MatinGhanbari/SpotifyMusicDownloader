import datetime
import os
import threading
import time

import pafy
import spotipy
from eyed3.core import AudioFile
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from youtubesearchpython import VideosSearch, Search
import youtube_dl
import eyed3.id3
import eyed3
import lyricsgenius
import av
from AppUI import startSplash

spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(client_id='a145db3dcd564b9592dacf10649e4ed5',
                                                        client_secret='389614e1ec874f17b8c99511c7baa2f6'))
genius = lyricsgenius.Genius('biZZReO7F98mji5oz3cE0FiIG73Hh07qoXSIzYSGNN3GBsnY-eUrPAVSdJk_0_de')
market = [
    "AD", "AE", "AG", "AL", "AM", "AO", "AR", "AT", "AU", "AZ", "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ",
    "BN", "BO", "BR", "BS", "BT", "BW", "BY", "BZ", "CA", "CD", "CG", "CH", "CI", "CL", "CM", "CO", "CR", "CV", "CW",
    "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE", "EG", "ES", "FI", "FJ", "FM", "FR", "GA", "GB", "GD",
    "GE", "GH", "GM", "GN", "GQ", "GR", "GT", "GW", "GY", "HK", "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IN", "IQ",
    "IS", "IT", "JM", "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KR", "KW", "KZ", "LA", "LB", "LC", "LI", "LK",
    "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MC", "MD", "ME", "MG", "MH", "MK", "ML", "MN", "MO", "MR", "MT", "MU",
    "MV", "MW", "MX", "MY", "MZ", "NA", "NE", "NG", "NI", "NL", "NO", "NP", "NR", "NZ", "OM", "PA", "PE", "PG", "PH",
    "PK", "PL", "PS", "PT", "PW", "PY", "QA", "RO", "RS", "RW", "SA", "SB", "SC", "SE", "SG", "SI", "SK", "SL", "SM",
    "SN", "SR", "ST", "SV", "SZ", "TD", "TG", "TH", "TJ", "TL", "TN", "TO", "TR", "TT", "TV", "TW", "TZ", "UA", "UG",
    "US", "UY", "UZ", "VC", "VE", "VN", "VU", "WS", "XK", "ZA", "ZM", "ZW"]


class Song:
    def __init__(self, link):
        self.link = link
        self.song = spotify.track(link, market=None)
        self.trackName = self.song['name']
        self.filename = self.song['name']
        self.artist = self.song['artists'][0]['name']
        self.artists = self.song['artists']
        self.artist_data = spotify.artists([self.artists[0]['id']])
        self.trackNumber = self.song['track_number']
        self.album = self.song['album']['name']
        self.releaseDate = int(self.song['album']['release_date'][:4])
        self.duration = int(self.song['duration_ms'])
        self.ui = None

    def Features(self):
        if len(self.artists) > 1:
            features = "(Ft."
            for artistPlace in range(0, len(self.artists)):
                try:
                    if artistPlace < len(self.artists) - 2:
                        artistft = self.artists[artistPlace + 1]['name'] + ", "
                    else:
                        artistft = self.artists[artistPlace + 1]['name'] + ")"
                    features += artistft
                except:
                    pass
        else:
            features = ""
        return features

    def ConvertTimeDuration(self):
        target_datetime_ms = self.duration
        base_datetime = datetime.datetime(1900, 1, 1)
        delta = datetime.timedelta(0, 0, 0, target_datetime_ms)
        target_datetime1 = base_datetime + delta
        target_datetime1 = target_datetime1.replace(microsecond=0)
        target_datetime2 = target_datetime1 + datetime.timedelta(seconds=1)
        target_datetime3 = target_datetime1 + datetime.timedelta(seconds=2)
        target_datetime4 = target_datetime1 + datetime.timedelta(seconds=3)

        target_datetime5 = target_datetime1 - datetime.timedelta(seconds=1)
        target_datetime6 = target_datetime1 - datetime.timedelta(seconds=2)
        target_datetime7 = target_datetime1 - datetime.timedelta(seconds=3)

        return target_datetime1, \
               target_datetime2, \
               target_datetime3, \
               target_datetime4, \
               target_datetime5, \
               target_datetime6, \
               target_datetime7

    def downloadSongCover(self):
        response = requests.get(self.song['album']['images'][0]['url'])
        imageFileName = "core/music/cover/" + self.trackName + ".png"
        image = open(imageFileName, "wb")
        image.write(response.content)
        image.close()
        return imageFileName

    def downloadArtistPic(self):
        response = requests.get(self.artist_data['artists'][0]['images'][0]['url'])
        imageFileName = f'core/images/artists/{self.artist}.png'
        image = open(imageFileName, "wb")
        image.write(response.content)
        image.close()
        return imageFileName

    def YTLink(self):
        results = Search(str(self.trackName + " " + self.artist), limit=1).result()
        YTLink = results['result'][0]['link']
        return YTLink

    def download(self):
        video = pafy.new(self.YTLink())
        audio = video.getbestaudio()
        audio.download(filepath=f'core/music/{self.trackName}.webm', quiet=True, callback=self.mycb)
        self.setMetaData()

    def setMetaData(self):
        changeToMp3(self.trackName)
        audio = eyed3.load(f"core/music/{self.trackName}.mp3")
        if not audio.tag:
            audio.initTag()
        audio.tag.artist = self.artist
        audio.tag.album = self.album
        audio.tag.album_artist = self.artist
        audio.tag.title = self.trackName + self.Features()
        audio.tag.track_num = self.trackNumber
        audio.tag.year = self.trackNumber
        try:
            songGenius = genius.search_song(self.trackName, self.artist)
            audio.tag.lyrics.set(songGenius.lyrics)
        except:
            pass
        audio.tag.images.set(3, open(self.downloadSongCover(), 'rb').read(), 'image/png')
        audio.tag.save()

    def mycb(self, total, recvd, ratio, rate, eta):
        print(total, recvd, ratio, rate, eta)
        threading.Thread(target=self.ui.setProgressBar, args=(round(ratio * 100), eta,)).start()


def album(link):
    results = spotify.album_tracks(link)
    albums = results['items']
    while results['next']:
        results = spotify.next(results)
        albums.extend(results['items'])
    return albums


def artist(link):
    results = spotify.artist_top_tracks(link)
    albums = results['tracks']
    return albums


def searchalbum(track):
    results = spotify.search(track)
    return results['tracks']['items'][0]['album']['external_urls']['spotify']


def playlist(link):
    results = spotify.playlist_tracks(link)
    return results['items'][:50]


def searchsingle(track):
    results = spotify.search(track)
    return results['tracks']['items'][0]['href']


def searchartist(searchstr):
    results = spotify.search(searchstr)
    return results['tracks']['items'][0]['artists'][0]["external_urls"]['spotify']


def changeToMp3(trackName):
    webm_file = f"core/music/{trackName}.webm"
    mp3_file = f"core/music/{trackName}.mp3"

    with av.open(webm_file, 'r') as inp:
        # f = SpooledTemporaryFile(mode="w+b")
        f = mp3_file
        with av.open(f, 'w', format="mp3") as out:  # Open file, setting format to mp3
            out_stream = out.add_stream("mp3")
            for frame in inp.decode(audio=0):
                frame.pts = None
                for packets in out_stream.encode(frame):
                    out.mux(packets)
            for packets in out_stream.encode(None):
                out.mux(packets)
    os.remove(webm_file)


if __name__ == '__main__':
    song = Song('https://open.spotify.com/track/7xNpg7MR3kj9FGRKxIMs0D')
    # song = Song('https://open.spotify.com/track/5p4kiC9UWPNDTU1GW16dmS')
    print(song.artist_data)

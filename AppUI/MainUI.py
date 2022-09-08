import os
import threading
import time
import typing
import urllib
import webbrowser
from datetime import datetime
from typing import Optional
import ctypes
from PyQt5 import uic
from PyQt5.QtCore import QObject, QSize, Qt
from PyQt5.QtGui import QIcon, QIntValidator, QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QFrame
from threading import Thread

from song import Song


class MainUi(QFrame):
    mainWidget: Optional[QWidget]
    songWidget: Optional[QWidget]
    artistWidget: Optional[QWidget]
    downloadWidget: Optional[QWidget]

    main_page_logo: Optional[QLabel]
    main_page_developer: Optional[QLabel]
    trackName: Optional[QLabel]
    artist: Optional[QLabel]
    trackNumber: Optional[QLabel]
    album: Optional[QLabel]
    releaseDate: Optional[QLabel]
    duration: Optional[QLabel]
    cover: Optional[QLabel]
    artist_pic: Optional[QLabel]
    artist_name: Optional[QLabel]
    followers: Optional[QLabel]

    music_link_input: Optional[QLineEdit]

    search_button: Optional[QPushButton]
    back: Optional[QPushButton]
    download: Optional[QPushButton]

    progressBar: Optional[QProgressBar]

    song: Song

    def __init__(self):
        self.onlyInt = QIntValidator(0, 200000)
        super(MainUi, self).__init__()
        uic.loadUi("core/ui/app.ui", self)
        self.setWindowTitle("SoundCloud Music Downloader")
        self.setWindowIcon(QIcon("core/images/logo.ico"))
        self.setFrameShape(QFrame.StyledPanel)
        self.loginTime = datetime.now()
        self.setMouseTracking(True)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()
        self.setUIChildOptions()

    def setMouseTracking(self, flag):
        def recursive_set(parent):
            for child in parent.findChildren(QObject):
                try:
                    child.setMouseTracking(flag)
                except:
                    pass
                recursive_set(child)

        QWidget.setMouseTracking(self, flag)
        recursive_set(self)

    def initUI(self):
        self.mainWidget = self.findChild(QWidget, "mainWidget")
        self.songWidget = self.findChild(QWidget, "songWidget")
        self.artistWidget = self.findChild(QWidget, "artistWidget")
        self.downloadWidget = self.findChild(QWidget, "downloadWidget")

        self.main_page_logo = self.findChild(QLabel, "main_page_logo")
        self.main_page_developer = self.findChild(QLabel, "main_page_developer")
        self.trackName = self.findChild(QLabel, "trackName")
        self.trackNumber = self.findChild(QLabel, "trackNumber")
        self.album = self.findChild(QLabel, "album")
        self.releaseDate = self.findChild(QLabel, "releaseDate")
        self.duration = self.findChild(QLabel, "duration")
        self.cover = self.findChild(QLabel, "cover")
        self.artist_name = self.findChild(QLabel, "artist_name")
        self.followers = self.findChild(QLabel, "followers")
        self.genres = self.findChild(QLabel, "genres")
        self.id = self.findChild(QLabel, "id")
        self.popularity = self.findChild(QLabel, "popularity")
        self.type = self.findChild(QLabel, "type")
        self.artist_pic = self.findChild(QLabel, "artist_pic")
        self.download_logo = self.findChild(QLabel, "download_logo")
        self.remain = self.findChild(QLabel, "remain")

        self.music_link_input = self.findChild(QLineEdit, "music_link_input")

        self.artist = self.findChild(QPushButton, "artist")
        self.backToSong = self.findChild(QPushButton, "backToSong")
        self.search_button = self.findChild(QPushButton, "search_button")
        self.back = self.findChild(QPushButton, "back")
        self.download = self.findChild(QPushButton, "download")
        self.spotifyProfile = self.findChild(QPushButton, "spotifyProfile")

        self.progressBar = self.findChild(QProgressBar, "progressBar")

    def setUIChildOptions(self):
        self.mainWidget.setVisible(True)
        self.songWidget.setVisible(False)
        self.artistWidget.setVisible(False)
        self.downloadWidget.setVisible(False)
        self.progressBar.setValue(0)
        self.main_page_logo.setText('')
        self.main_page_developer.setText('''
        App developed by Matin Ghanbari
        
        Email: GhanbariMatin6@gmail.com
        Telegram: t.me/Ghanbari_Matin
        ''')
        self.main_page_logo.setPixmap(QPixmap('core/images/logo.png').scaled(200, 200))
        self.download_logo.setPixmap(QPixmap('core/images/logo.png').scaled(200, 200))

        self.search_button.clicked.connect(self.searchSongData)
        self.back.clicked.connect(lambda e: self.setWidgets(True, False, False))
        self.backToSong.clicked.connect(lambda e: self.setWidgets(False, True, False))
        self.download.clicked.connect(self.downloadSong)
        self.artist.clicked.connect(self.artistInfo)
        self.spotifyProfile.clicked.connect(self.gotoSpotifyProfile)

    def backToSongQW(self):
        self.setWidgets(False, True, False)

    def gotoSpotifyProfile(self):
        webbrowser.open(self.song.artist_data['artists'][0]['external_urls']['spotify'])

    def searchSongData(self):
        if self.music_link_input.text() == '' or self.music_link_input.text() is None:
            ctypes.windll.user32.MessageBoxW(0, "Please paste music link and try again.", "Music Link Error", 0)
            return

        songLink = self.music_link_input.text()[
                   :self.music_link_input.text().find("?")] if self.music_link_input.text().find(
            "?") > 0 else self.music_link_input.text()
        while True:
            try:
                self.song = Song(songLink)
                break
            except:
                time.sleep(1)
        self.setWidgets(False, True, False)
        self.trackName.setText(self.song.trackName)
        self.artist.setText(self.song.artist + " " + self.song.Features())
        self.trackNumber.setText(str(self.song.trackNumber))
        self.album.setText(self.song.album)
        self.releaseDate.setText(str(self.song.releaseDate))
        self.duration.setText(str(self.song.duration))
        self.cover.setPixmap(QPixmap(self.song.downloadSongCover()).scaled(250, 250))

    def artistInfo(self):
        self.setWidgets(False, False, True)
        self.artist_name.setText(self.song.artist_data['artists'][0]['name'])
        self.followers.setText(str(self.song.artist_data['artists'][0]['followers']['total']))
        self.genres.setText(str(self.song.artist_data['artists'][0]['genres']))
        self.id.setText(self.song.artist_data['artists'][0]['id'])
        self.popularity.setText(str(self.song.artist_data['artists'][0]['popularity']))
        self.type.setText(self.song.artist_data['artists'][0]['type'])
        self.artist_pic.setPixmap(QPixmap(self.song.downloadArtistPic()).scaled(250, 250))

    def backToMain(self):
        self.setWidgets(True, False, False)

    def downloadSong(self):
        self.setWidgets(False, False, False)
        self.downloadWidget.setVisible(True)
        self.song.ui = self
        threading.Thread(target=self.song.download, args=()).start()

    def setWidgets(self, f1, f2, f3):
        self.mainWidget.setVisible(f1)
        self.songWidget.setVisible(f2)
        self.artistWidget.setVisible(f3)

    def setProgressBar(self, value: int, remainTime):
        self.progressBar.setValue(value)
        self.remain.setText(f"Remain Time: {remainTime}s")

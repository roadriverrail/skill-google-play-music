# Copyright 2017 Rhett Aultman
#
# Thisis free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.


import time
from os.path import dirname
import re

from gmusicapi import Mobileclient

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
try:
    from mycroft.skills.audioservice import AudioService
except:
    from mycroft.util import play_mp3
    AudioService = None

__author__ = 'roadriverrail'

LOGGER = getLogger(__name__)


class GooglePlayMusicSkill(MycroftSkill):
    def __init__(self):
        super(GooglePlayMusicSkill, self).__init__(name="GooglePlayMusicSkill")
        self.api = Mobileclient()
        self.logged_in = False
        self.process = None
        self.audioservice = None

    def initialize(self):
#        song_intent = IntentBuilder("GooglePlayMusicSongArtistIntent").require(
#            "GooglePlayMusicKeyword").require("Song").require("Artist").build()
#        self.register_intent(song_intent, self.handle_intent)


        self.register_intent_file('play.genre.intent', self.handle_intent)

#        station_intent = IntentBuilder("GooglePlayMusicStationIntent").require(
#            "GooglePlayMusicKeyword").require("Query").build()
#        self.register_intent(station_intent, self.handle_intent)


        self.register_intent_file('stop.intent', self.handle_stop)

#        stop_intent = IntentBuilder("GooglePlayMusicStopIntent") \
#                .require("GooglePlayMusicStopVerb") \
#                .require("GooglePlayMusicKeyword").build()
#        self.register_intent(stop_intent, self.handle_stop)

        if not self.settings['account_name'] or not self.settings['account_password']:
            self.speak_dialog('google-play-no-settings')

        if AudioService:
            self.audioservice = AudioService(self.emitter)

    def login_if_necessary(self):
        if (not self.logged_in):
            if self.api.is_authenticated():
                self.logged_in = True
            elif not self.settings['account_name'] or not self.settings['account_password']:
                self.speak_dialog('google-play-no-settings')
            else:
                self.logged_in = self.api.login(self.settings['account_name'], self.settings['account_password'], Mobileclient.FROM_MAC_ADDRESS)

    def play_track(self, track_id):
        stream_url = self.api.get_stream_url(track_id)

        self.stop()

        self.speak_dialog('google-play')

        time.sleep(5)

        # Pause for the intro, then start the new stream
        # if audio service module is available use it
        if self.audioservice:
            self.audioservice.play(stream_url)
        else: # othervice use normal mp3 playback
            self.process = play_mp3(stream_url)

    def play_station(self, query):
        results = self.api.search(query, 5)

        station_hits = results.get('station_hits', [])

        if not station_hits:
            self.speak_dialog('google-play-no-match')
            return

        station = station_hits[0].get('station')

        station_seed = station.get('stationSeeds')[0].get('curatedStationId')

        if not station_seed:
            self.speak_dialog('google-play-no-match')
            return
 
        created_station = self.api.create_station(query + " radio", curated_station_id=station_seed)

        tracks = self.api.get_station_tracks(created_station)

        track_id = tracks[0].get('id', tracks[0].get('nid', ''))

        self.play_track(track_id)

    def play_song_artist(self, song, artist):
        artist_hits = self.api.search(artist).get('artist_hits')
        song_hits = self.api.search(song).get('song_hits', [])
        for song in song_hits:
            artist_ids = song.get('artistId')
            for artist_id in artist_ids:
                for artist in artist_hits:
                    if artist.get('artistId') == artist_id:
                        track_id = song.get('id', song.get('nid', ''))
                        self.play_track(track_id)
        else:
            self.speak_dialog('google-play-no-match')

    def handle_intent(self, message):
        self.login_if_necessary()
#        try:
        if message.data.get('genre'):
            self.play_station(message.data.get('genre'))
#        elif message.data.get("Song") and message.data.get("Artist"):
#            self.play_song_artist(message.data.get("Song"), message.data.get("Artist"))

#        except Exception as e:
#            LOGGER.error("Error: {0}".format(e))

    def handle_stop(self, message):
        self.stop()

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()
            self.speak_dialog('google-play-stop')


def create_skill():
    return GooglePlayMusicSkill()

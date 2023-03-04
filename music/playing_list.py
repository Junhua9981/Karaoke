from typing import List
from music.netease.netease import Track as NetEaseTrack
from .base_track import Track as BaseTrack

class PlayingList:
    def __init__(self) -> None:
        self.tracks: List[BaseTrack] = []
        self.current_track: BaseTrack = None

    def add_track(self, track: BaseTrack):
        if track.playable:
            self.tracks.append(track)
        else:
            track.setup_track()
            print(track.music_url, track.music_video_url)
            if track.playable:
                self.tracks.append(track)
            else:
                raise Exception("Track is not playable.")
            
        if not self.current_track:
            self.current_track = self.tracks[0]

    def get_current_track(self):
        for track in self.tracks:
            print( track )
        return self.current_track

    def next(self):
        if len(self.tracks) > 1:
            self.tracks.pop(0)
            self.current_track = self.tracks[0]
            print(self.current_track)
        else:
            self.current_track = None

playing_list = PlayingList()
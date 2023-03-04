class Track:
    def __init__(self, song_id: str, name: str, artists_name: str, album_name: str, mvid: str):
        self.song_id = song_id
        self.name = name
        self.artists = artists_name
        self.album_name = album_name
        self.mvid = mvid
        self.lyrics = None
        self.music_url = None
        self.music_video_url = None
        self.playable = True if self.music_url else False
    
    def __str__(self):
        return f"Track: {self.name} by {self.artists} {self.album_name} (id: {self.song_id}) mv: {self.mvid}"
    
    def get_lyrics(self):
        "Should be implemented by subclass"
        raise NotImplementedError
    
    def get_url(self):
        "Should be implemented by subclass"
        raise NotImplementedError
    
    def get_music_video_url(self):
        "Should be implemented by subclass"
        raise NotImplementedError
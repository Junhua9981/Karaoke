from pydantic import BaseModel
from typing import Optional

class TrackId(BaseModel):
    track_id : int

class MvId(BaseModel):
    mv_id : int
    res : int

class SearchResult(BaseModel):
    song_id : int
    name : Optional[str] = None
    artists : Optional[list[str]]= None
    album_name : Optional[str] = None
    mvid : int
    lyrics : Optional[str] = None
    music_url : Optional[str] = None
    music_video_url : Optional[str] = None

class SearchResults(BaseModel):
    results : list[SearchResult]
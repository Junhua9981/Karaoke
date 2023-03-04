from fastapi import APIRouter
from fastapi import Request
from model.TrackModels import SearchResult
from music.netease.netease import Track 
from manager.ws_conn import manager
from music.playing_list import playing_list
import json

router = APIRouter()

@router.post("/add")
async def add(request: Request, track: SearchResult):
    playing_list.add_track(Track(track.song_id, track.name, track.artists, track.album_name, track.mvid))
    
    return {"status": "ok"}

@router.post("/mute")
async def mute(request: Request):
    await manager.mute()
    return {"status": "ok"}
from fastapi import APIRouter
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from model.TrackModels import SearchResult, SearchResults, TrackId, MvId
import json
router = APIRouter()

@router.get("/search")
async def search(request:Request, keyword: str):
    # Search for the keyword and get the results
    search_results = request.app.netease.Search(keyword)
    # Convert the results into the format that the frontend expects
    result = SearchResults(results = [ SearchResult(song_id=search_result.song_id,
                                                    name=search_result.name,
                                                    artists=search_result.artists,
                                                    album_name=search_result.album_name,
                                                    mvid=search_result.mvid,
                                                    lyrics=search_result.lyrics,
                                                    music_url=search_result.music_url,
                                                    music_video_url=search_result.music_video_url ) for search_result in search_results ])
    # Return the result to the frontend
    return result


@router.get("/lyrics")
async def lyrics(request:Request, id: int):
    result = request.app.netease.GetParsedLyrics(id)
    
    return result

@router.get("/music_url")
async def music_url(request:Request, id: int):
    result = request.app.netease.GetMusicUrl(id)
    return result

@router.get("/music_video_url")
async def music_video_url(request:Request, mvid: MvId):
    result = request.app.netease.GetMusicVideoUrl(mvid.mv_id, mvid.res)
    return result



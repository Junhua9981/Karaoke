from pyncm.apis.login import LoginViaAnonymousAccount, GetCurrentSession, GetCurrentLoginStatus
from pyncm import DumpSessionAsString, SetCurrentSession, LoadSessionFromString
from pyncm.apis.track import GetTrackAudio, GetTrackDetail
from pyncm.apis.video import GetMVResource
from pyncm.apis.cloudsearch import GetSearchResult
from pyncm.apis import EapiCryptoRequest, WeapiCryptoRequest, LoginRequiredApi
from logging import getLogger
from .parseLyrics import LyricsByWord
import json
# from ..base_music import BaseMusic

logger = getLogger(__name__)

@EapiCryptoRequest
def GetTrackLyricsByWord(song_id: str, 
  cp  = False,
  tv  = 0,
  lv  = 0,
  rv  = 0,
  kv  = 0,
  yv  = 0,
  ytv = 0,
  yrv = 0):
  
  return "/eapi/song/lyric/v1", {
      "id": str(song_id),
      "cp": str(cp),
      "tv": str(tv),
      "lv": str(lv),
      "rv": str(rv),
      "kv": str(kv),
      "yv": str(yv),
      "ytv": str(ytv),
      "yrv": str(yrv)
  }

@WeapiCryptoRequest
def GetOriginalSearchResult(keyword: str, 
                            type: int = 1,
                            limit: int = 20,
                            offset: int = 0 ):
    return "/weapi/search/get", {
        "s": str(keyword),
        "type": str(type),
        "limit": str(limit),
        "offset": str(offset)
    } , 'POST'

@EapiCryptoRequest
def GetCloudSearchResult(keyword: str, 
                         type: int = 1,
                         limit: int = 20,
                         offset: int = 0,
                         total: bool = True ):
    
# input_ type: 1: 单曲, 10: 专辑, 100: 歌手, 1000: 歌单, 1002: 用户, 1004: MV, 1006: 歌词, 1009: 电台, 1014: 视频
# Via https://github.com/Binaryify/NeteaseCloudMusicApi/blob/master/module/cloudsearch.js
    return "/eapi/cloudsearch/pc", {
        "s": str(keyword),
        "type": str(type),
        "limit": str(limit),
        "offset": str(offset),
        "total": str(total).lower()
    }, 'POST'


class Track:
    def __init__(self, song_id: str, name: str = None, artists_name: str = None, album_name: str = None, mvid: str = None):
        self.song_id = song_id
        self.name = name
        self.artists = artists_name
        self.album_name = album_name
        self.mvid = mvid
        self.lyrics = None
        self.music_url = None
        self.music_video_url = None
    
    def __str__(self):
        return f"Track: {self.name} by {self.artists} {self.album_name} (id: {self.song_id}) mv: {self.mvid}"
    
    # def get_track_info(self):
    #     if self.name and self.artists and self.album_name:
    #         return
    #     else:
    #         track_info = GetTrackDetail(self.song_id)
    #         print(track_info)

    def get_lyrics(self):
        if self.lyrics:
            return self.lyrics
        else:
            # raw_lyrics = NetEaseMusic.GetLyrics(self.song_id)
            # lyrics = NetEaseMusic.ParseLyrics(raw_lyrics.get("yrc", ""))
            lyrics = NetEaseMusic.GetParsedLyrics(self.song_id)
            self.lyrics = lyrics
            return self.lyrics
    
    def get_url(self):
        if self.music_url:
            return self.music_url
        else:
            url = NetEaseMusic.GetMusicUrl(self.song_id)
            self.music_url = url
            return self.music_url
    
    def get_music_video_url(self):
        if self.music_video_url:
            return self.music_video_url
        else:
            url = NetEaseMusic.GetMusicVideoUrl(self.song_id)
            self.music_video_url = url
            return self.music_video_url
        
    def setup_track(self):
        self.get_lyrics() 
        print( self.get_url() )
        print( self.get_music_video_url() )
        # print(self.music_url, self.music_video_url)
    
    @property
    def playable(self):
        return self.music_url != None
    
    # def to_json(self):
    #     return json.dumps(
    #         {
    #             "song_id": self.song_id,
    #             "name": self.name,
    #             "artists": self.artists,
    #             "album_name": self.album_name,
    #             "mvid": self.mvid,
    #             "lyrics": self.lyrics,
    #             "music_url": self.music_url,
    #             "music_video_url": self.music_video_url
    #         }
    #     )
    
    def json(self):
        return {
            "lyrics": self.lyrics.to_json(),
            "music_url": self.music_url,
            "music_video_url": self.music_video_url
        }
    


class NetEaseMusic:
    def __init__(self):
        self.login()
    
    def login(self):
        try:
            SetCurrentSession(LoadSessionFromString(open(r"session_files\netease_session.txt").read()))

            if GetCurrentSession().login_info.get("success", False) == False:
                logger.info(" Session Timeout, Login again")
            else:
                GetCurrentSession().headers['X-Real-IP'] = '118.88.88.88'
                logger.info("Login successfully")
                return
            
            logger.info("Trying to login anonymously")
            self.login = LoginViaAnonymousAccount()
            GetCurrentSession().headers['X-Real-IP'] = '118.88.88.88'
            DumpSessionAsString(GetCurrentSession())
            logger.info(f"保存登陆信息于 : session_files\netease_session.txt")
            open(r"session_files\netease_session.txt", "w").write(DumpSessionAsString(GetCurrentSession()))

        except Exception as e:
            print(e)
            raise Exception("Login failed")
    
    @staticmethod
    def Search(keyword: str, limit: int = 10):
        try:
            result = GetSearchResult(keyword, stype=1, limit=limit, offset=0)
            # result = GetCloudSearchResult(keyword, limit)

            result = result.get("result", {}).get("songs", [])

            search_result = []
            for i in result:
                try:
                    artists_name = []
                    if type( i.get("ar") ) == dict:
                        artists_name.append(i.get("ar").get("name"))
                    else:
                        for j in i.get("ar"):
                            artists_name.append(j.get("name"))
                    print("Track: ", i.get("id", "No Id"), i.get("name", "No Name"), artists_name)
                    search_result.append(Track(song_id= i.get("id", None), name= i.get("name", "No Name"), artists_name= artists_name, album_name= i.get("al", {}).get("name"), mvid= i.get("mv") ) )
                except Exception as e:
                    print(e)
        except:
            raise Exception("Search failed")

        return search_result
    
    @staticmethod
    def GetLyrics(id: int):
        try:
            result = GetTrackLyricsByWord(id)

        except:
            raise Exception("Get lyrics failed")
        return result
    
    @staticmethod
    def ParseLyrics(lrc: str):
        lyrics = LyricsByWord(lrc, translate=True)

        return lyrics
    
    @staticmethod
    def GetParsedLyrics(id: int):
        try:
            raw_lyrics = NetEaseMusic.GetLyrics(id)
            lyrics = NetEaseMusic.ParseLyrics(raw_lyrics.get("yrc", {}).get("lyric", ""))
            # print(lyrics.to_json())
        except:
            raise Exception("Get lyrics failed")
        return lyrics
    
    @staticmethod
    def GetMusicUrl(id: int):
        try:
            data = GetTrackAudio(id).get('data', [])
            print(data)
            result = None
            for d in data:
                result = d.get('url', None) if result == None else result
        except:
            raise Exception("Get music url failed")
        return result
    
    @staticmethod
    def GetMusicVideoUrl(mvid: int, resolution: int = 720):
        try:
            result = GetMVResource(mvid, resolution)
            result = result.get("data", {}).get("url", None)
        except:
            raise Exception("Get music video url failed")
        return result
    


if __name__ == '__main__':
    raw_lyrics = None
    with open("test.txt", "r", encoding="UTF-8") as f:
        raw_lyrics = json.loads(f.read())

    print( "\n".join( raw_lyrics.get("yrc", {}).get("lyric", "").split('\n') )) 
    lyrics = NetEaseMusic.ParseLyrics(raw_lyrics.get("yrc", {}).get("lyric", ""))

    # netease = NetEaseMusic()
    
    # netease.Search( "五月天" )
    # id = input()
    # raw_lyrics = netease.GetLyrics(id)
    # lyrics = netease.ParseLyrics(raw_lyrics.get("yrc", "").get("lyric", ""))
    
    # print(netease.GetMusicUrl(id))
    # print(netease.GetMusicVideoUrl(id))
    # lyrics = netease.GetParsedLyrics(id)

    # with open("test.json", "w") as f:
        # f.write(lyrics.to_json())
    # print(lyrics.to_json())
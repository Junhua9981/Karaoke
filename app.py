from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from music.playing_list import PlayingList
from music.netease.netease import NetEaseMusic
from routers.search import router as search_router
from routers.playing import router as playing_router
from manager.ws_conn import manager
import pyncm
import json

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "ws://localhost",
    "ws://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.netease = NetEaseMusic()


app.include_router(search_router, prefix="/search")
app.include_router(playing_router, prefix="/playing")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            if data.get("type", None):
                manager.set_conn_type(websocket, data["type"])
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


app.mount("/static", StaticFiles(directory="static"), name="static")
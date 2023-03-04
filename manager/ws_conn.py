from typing import List
from fastapi import WebSocket
import asyncio
from music.playing_list import playing_list
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
        self.loop = asyncio.get_event_loop()

        self.loop.create_task(self.check_connections())
        # self.loop.run_forever()

    async def check_connections(self):
        while True:
            await asyncio.sleep(1)
            for connection, conn_type in self.active_connections.items():
                # print( connection, conn_type)
                if conn_type == "waiting" and len(playing_list.tracks) > 0:
                    # await self.send_personal_message( str(jsonable_encoder( playing_list.get_current_track() )).replace("'",'"').replace(', "trans": True', "").replace(', "translate": True', "").replace("None", 'null'), connection)
                    ret_str = json.dumps(playing_list.get_current_track(), default=lambda o: o.__dict__, sort_keys=True)
                    
                    await self.send_personal_message(ret_str , connection)
                    self.set_conn_type(connection, "playing")
                    playing_list.next()

    async def mute(self):
        await self.broadcast("mute")

    async def connect(self, websocket: WebSocket):
        # print( "ws connected")
        await websocket.accept()
        self.active_connections[websocket] = "waiting"

    def disconnect(self, websocket: WebSocket):
        self.active_connections.pop(websocket)

    def set_conn_type(self, websocket: WebSocket, conn_type: str):
        self.active_connections[websocket] = conn_type

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        print("broadcasted: ", message)
        for connection in self.active_connections.keys():
                await connection.send_text(message)

    


manager = ConnectionManager()
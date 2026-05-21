import asyncio
import fastapi

from common.web_socket_manager import WebSocketManager
from common.app_data import AppData

import routers.utility as utility
import schemas.common as common

# --- TASK ---

async def reader(ws: fastapi.WebSocket, _: AppData) -> None:
    """Read from web socket

    Args:
        ws (fastapi.WebSocket): Web socket
    """
    
    while True:
        
        msg = await ws.receive_json()
        
        print(msg)

async def sender(ws: fastapi.WebSocket, data: AppData) -> None:
    """Write to web socket

    Args:
        ws (fastapi.WebSocket): Web socket
    """
    
    while True:
        
        if data.send_enabled:
            
            print("SENDING...")
            
            await ws.send_json({"Text": "Polling"})
            
        await asyncio.sleep(1)

# --- HTTP ---

router: fastapi.APIRouter = fastapi.APIRouter(prefix='/ws', tags=['Web Socket'])

# >>> WEBSOCKET

@router.websocket("")
async def websocket_endpoint(websocket: fastapi.WebSocket):
    """Manage the web socket endpoint

    Args:
        websocket (fastapi.WebSocket): Receiving web socket
    """
    
    # * Accecpt client
    
    wsm: WebSocketManager = websocket.app.state.wsm
    
    await wsm.connect(websocket)
    
    print("Client connected: ", websocket.base_url)
    
    # * Tasks
    
    data: AppData = websocket.app.state.data
    
    await websocket.send_json(
        {
            "type": "info",
            "database":
            {
                "connected": data.db != None,
                "name": data.db_name,
                "url": data.mongo_url
            }
        })
    
    read_task = asyncio.create_task(reader(websocket, data))
    send_task = asyncio.create_task(sender(websocket, data))
    
    _, pending = await asyncio.wait({ read_task, send_task }, return_when=asyncio.FIRST_EXCEPTION)
    
    for task in pending: task.cancel()
    
    print("Client disconnected: ", websocket.base_url)
    
    wsm.disconnect(websocket)

# >>> GET

@router.get("/start")
async def start(request: fastapi.Request):
    
    print("STARTED")
    
    data: AppData = request.app.state.data
    
    data.send_enabled = True
    
    return {"message": "STARTED"}

@router.get("/end")
async def end(request: fastapi.Request):
    
    print("ENDED")
    
    data: AppData = request.app.state.data
    
    data.send_enabled = False
    
    return {"message": "ENDED"}

# >>> PUT

@router.put("/stop-simulation", response_model=common.ActionModel)
async def start(request: fastapi.Request):
    
    data: AppData = request.app.state.data
    
    data.stop_simulation = True
    
    return utility.ok("Ok")
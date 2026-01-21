import asyncio
import contextlib
import fastapi
import pydantic

from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

import converter
import database
import schemas.spacecraft_schema as spacecraft_schema

from routers.spacecraft import router as router_spacecraft

# --- CONTEXT ---

@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    
    # * Startup code
    
    database.client = AsyncIOMotorClient("mongodb://localhost:27017")
    
    db = database.client["spacecraft_dynamics_lab"]
    
    print("Connected to MongoDB!")
    
    # * Check existing collections
    
    existing_collections: list = await db.list_collection_names()
    
    # * Create missing collections
    
    required_collections: list = ["spacecrafts"]
    
    for collection in required_collections:
        
        pydantic_schema: dict | None = None
        
        mongodb_schema: dict | None = None
        
        if collection == "spacecrafts":
            
            pydantic_schema: dict = spacecraft_schema.SpacecraftModel.model_json_schema()
        
        if pydantic_schema:
            
            mongodb_schema: dict = converter.convert_pydantic_to_mongo(schema=pydantic_schema)
        
        if collection not in existing_collections:
            
            await db.create_collection(collection, validator={"$jsonSchema": mongodb_schema})
            
            print(f"Created missing collection: {collection}")
            
        else:
            
            await db.command("collMod", collection, validator={"$jsonSchema": mongodb_schema})
            
            print(f"Updated collection: {collection}")
    
    print("MongoDB ready!")

    yield
    
    # * Shutdown code
    
    database.client.close()
    
# --- APP ---

app: fastapi.FastAPI = fastapi.FastAPI(title="Spacecraft Dynamics Lab - Server",
                                       version="1.0.0",
                                       lifespan=lifespan)

app.add_middleware(CORSMiddleware,
                   allow_origins=[ 'http://localhost:5173', 'http://127.0.0.1:5173' ], # ? Electron App
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

app.include_router(router=router_spacecraft)

@app.get("/")
async def get_root():
    
    return {"message": "Hello from FastAPI!"}

# --- WEB SOCKET ---

app.state.send_enabled = False # ? CHeck if I can send to web socket

async def reader(ws: fastapi.WebSocket) -> None:
    """Read from web socket

    Args:
        ws (fastapi.WebSocket): Web socket
    """
    
    while True:
        
        msg = await ws.receive_json()
        
        print(msg)
        
async def sender(ws: fastapi.WebSocket) -> None:
    """Write to web socket

    Args:
        ws (fastapi.WebSocket): Web socket
    """
    
    while True:
        
        if app.state.send_enabled:
            
            print("SENDING...")
            
            await ws.send_json({"Text": "Polling"})
            
        await asyncio.sleep(1)

@app.websocket("/ws")
async def websocket_endpoint(websocket: fastapi.WebSocket):
    """Manage the web socket endpoint

    Args:
        websocket (fastapi.WebSocket): Receiving web socket
    """
    
    # * Accecpt client
    
    await websocket.accept()
    
    print("Client connected: ", websocket.base_url)
    
    # * Tasks
    
    read_task = asyncio.create_task(reader(websocket))
    send_task = asyncio.create_task(sender(websocket))
    
    _, pending = await asyncio.wait({ read_task, send_task }, return_when=asyncio.FIRST_EXCEPTION)
    
    for task in pending: task.cancel()
    
    print("Client disconnected: ", websocket.base_url)

@app.get("/start")
async def start():
    print("STARTED")
    app.state.send_enabled = True
    return {"message": "STARTED"}

@app.get("/end")
async def end():
    print("ENDED")
    app.state.send_enabled = False
    return {"message": "ENDED"}
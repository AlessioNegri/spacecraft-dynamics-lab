import fastapi as fa
import asyncio

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from motor.motor_asyncio import AsyncIOMotorClient

from contextlib import asynccontextmanager

class NameRequest(BaseModel):
    name: str
    mass: float


@asynccontextmanager
async def lifespan(app: fa.FastAPI):
    # Startup code
    app.mongodb_client = AsyncIOMotorClient("mongodb://localhost:27017")
    app.mongodb = app.mongodb_client["spacecraft_dynamics_lab"]
    
    print("Connected to MongoDB!")
    
    # Check existing collections
    
    existing_collections = await app.mongodb.list_collection_names()
    
    # Create missing collections
    
    required_collections = ["spacecrafts"]
    
    for collection in required_collections:
        if collection not in existing_collections:
            await app.mongodb.create_collection(collection, validator={"$jsonSchema": spacecraft_schema} if collection == "spacecrafts" else None)
            print(f"Created missing collection: {collection}")
        else:
            await app.mongodb.command("collMod", collection, validator={"$jsonSchema": spacecraft_schema} if collection == "spacecrafts" else None)
            print(f"Updated collection: {collection}")
    
    print("MongoDB ready!")

    yield

    # Shutdown code
    app.mongodb_client.close()

app : fa.FastAPI = fa.FastAPI(
    title="Spacecraft Dynamics Lab - Server",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(CORSMiddleware, allow_origins=[ 'http://localhost:5173' ], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.state.send_enabled = False

async def reader(ws: fa.WebSocket):
    while True:
        msg = await ws.receive_json()
        print(msg)
        
async def sender(ws: fa.WebSocket):
    while True:
        if app.state.send_enabled:
            print("SENDING...")
            await ws.send_json({"Text": "Polling"})
        await asyncio.sleep(1)

@app.websocket("/ws")
async def websocket_endpoint(websocket: fa.WebSocket):
    await websocket.accept()
    print("Client connected")
    
    read_task = asyncio.create_task(reader(websocket))
    send_task = asyncio.create_task(sender(websocket))
    
    done, pending = await asyncio.wait(
        { read_task, send_task }, return_when=asyncio.FIRST_EXCEPTION
    )
    
    for task in pending: task.cancel()
    print("Client disconnected")
    
    # try:
    #     while True:
    #         data = await websocket.receive_json()
    #         print("Received from Electron:", data)
            
    #         await websocket.send_json(f"{data}")
    # except Exception:
    #     print("Client disconnected")

spacecraft_schema = {
    "bsonType": "object",
    "required": ["name", "mass"],
    "properties": {
        "name": {
            "bsonType": "string",
            "description": "Name of the spacecraft"
        },
        "mass": {
            "bsonType": "number",
            "description": "Mass of the spacecraft in kilograms"
        },
        # "inertia_tensor": {
        #     "bsonType": "array",
        #     "items": {
        #         "bsonType": "number"
        #     },
        #     "minItems": 9,
        #     "maxItems": 9,
        #     "description": "Inertia tensor represented as a flat array (3x3 matrix)"
        # }
    }
}

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI!"}


@app.post("/spacecraft/insert")
async def insert_spacecraft(payload: NameRequest):
    print(f"Received payload: {payload}")
    
    result = await app.mongodb["spacecrafts"].insert_one(payload.model_dump())
    print(f"Inserted document ID: {result.inserted_id}")
    
    return {"response": "Done!"}

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
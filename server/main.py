import contextlib
import fastapi

from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

import common.converter as converter
import common.database as database

import schemas.spacecraft_schema as spacecraft_schema

from common.web_socket_manager import WebSocketManager
from common.app_data import AppData

from routers.web_socket import router as router_web_socket
from routers.spacecraft import router as router_spacecraft
from routers.interplanetary import router as router_interplanetary

# --- CONTEXT ---

@contextlib.asynccontextmanager
async def lifespan(_: fastapi.FastAPI):
    """Manage application lifespan events

    Args:
        app (fastapi.FastAPI): Application instance
    """
    
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
            
            if collection == "spacecrafts":
            
                await db["spacecrafts"].update_many({
                                                        "$or":
                                                        [
                                                            { "style": { "$exists": False } },
                                                            { "model": { "$exists": False } }
                                                        ]
                                                    },
                                                    {
                                                        "$set": 
                                                        {
                                                            "style.width": 4,
                                                            "style.color": "#FFFFFF",
                                                            "model": ""
                                                        }
                                                    })

            await db.command("collMod",
                             collection,
                             validator={"$jsonSchema": mongodb_schema},
                             validationLevel="moderate",
                             validationAction="warn")
            
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

app.state.wsm   = WebSocketManager()
app.state.data  = AppData()

app.include_router(router=router_web_socket)
app.include_router(router=router_spacecraft)
app.include_router(router=router_interplanetary)

@app.get("/")
async def get_root():
    
    return {"message": "Hello from FastAPI!"}
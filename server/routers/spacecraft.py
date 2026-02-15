import base64
import bson
import fastapi
import json
import typing

import common.database as database
import routers.utility as utility
import schemas.common as common
import schemas.spacecraft_schema as schema

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

# --- UTILITY ---

def serialize_spacecraft(doc: schema.SpacecraftModel) -> dict:
    """Serialize the DB document in a JSON dictionary

    Args:
        doc (SpacecraftModel): MongoDB collection document

    Returns:
        dict: JSON dictionary
    """
    
    return {
        "_id": str(doc["_id"]),
        "name": doc["name"],
        "mass": doc["mass"],
        "orbit": doc["orbit"],
        "style": doc["style"],
        "image": base64.b64encode(doc["image"]).decode() if doc.get("image") else None,
        "model": doc["model"]
    }
    
def convert_orbit(orbit_data: dict) -> dict:
    """Convert orbit data in float

    Args:
        orbit_data (dict): Orbit data

    Returns:
        dict: Converted orbit data
    """
    
    return {
        "sma": float(orbit_data["sma"]),
        "ecc": float(orbit_data["ecc"]),
        "inc": float(orbit_data["inc"]),
        "raan": float(orbit_data["raan"]),
        "aop": float(orbit_data["aop"]),
        "tan": float(orbit_data["tan"])
    }

# --- HTTP ---

router: fastapi.APIRouter = fastapi.APIRouter(prefix='/spacecraft', tags=['Spacecraft'])

# >>> GET

@router.get(path='/items', response_model=typing.List[schema.SpacecraftModelInfo])
async def get_items(client: AsyncIOMotorClient = fastapi.Depends(database.get_client)):
    """HTTP GET spacecrafts collection

    Args:
        client (AsyncIOMotorClient, optional): MongoDB client. Defaults to fastapi.Depends(database.get_client).

    Returns:
        [SpacecraftModel]: List of spacecrafts
    """
    
    spacecrafts: AsyncIOMotorCollection = client["spacecraft_dynamics_lab"]["spacecrafts"]
    
    result: typing.List[schema.SpacecraftModelInfo] = await spacecrafts.find().to_list()
    
    # * Serialize for frontend
    
    serialized = [serialize_spacecraft(doc) for doc in result]
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=serialized)

# >>> POST

@router.post("/insert", response_model=common.ActionModel)
async def post_insert(name: str = fastapi.Form(...),
                      mass: float = fastapi.Form(...),
                      orbit: str = fastapi.Form(...),
                      style: str = fastapi.Form(...),
                      image: fastapi.UploadFile | None = fastapi.File(None),
                      model: str = fastapi.Form(...),
                      client: AsyncIOMotorClient = fastapi.Depends(database.get_client)):
    """HTTP POST INSERT spacecrafts collection

    Args:
        name (str, optional): Name. Defaults to fastapi.Form(...).
        mass (float, optional): Mass. Defaults to fastapi.Form(...).
        orbit (str, optional): Orbit parameters. Defaults to fastapi.Form(...).
        style (str, optional): Style parameters. Defaults to fastapi.Form(...).
        image (fastapi.UploadFile | None, optional): Image. Defaults to fastapi.File(None).
        model (str, optional): 3D model name. Defaults to fastapi.Form(...).
        client (AsyncIOMotorClient, optional): MongoDB client. Defaults to fastapi.Depends(database.get_client).

    Returns:
        ActionModel: Result
    """
    
    spacecrafts: AsyncIOMotorCollection = client["spacecraft_dynamics_lab"]["spacecrafts"]
    
    # * Check existing name
    
    exist: schema.SpacecraftModel | None = await spacecrafts.find_one({ "name": name })
    
    if exist:
        
        return utility.error(fastapi.status.HTTP_400_BAD_REQUEST, f"{name} already existing")
    
    # * Parse orbit JSON
    
    try:
        
        orbit_data = convert_orbit(json.loads(orbit))
        
    except Exception:
        
        return utility.error(fastapi.status.HTTP_400_BAD_REQUEST, "Invalid orbit JSON")
    
    # * Parse style JSON
    
    try:
        
        style_data = json.loads(style)
        
    except Exception:
        
        return utility.error(fastapi.status.HTTP_400_BAD_REQUEST, "Invalid style JSON")
    
    # * Read image if provided
    
    image_bytes: bson.Binary | None = None
    
    if image is not None:
        
        image_bytes = await image.read()
        image_bytes = bson.Binary(image_bytes)

    # * Insert into MongoDB
    
    doc: dict =\
    {
        "name": name,
        "mass": mass,
        "orbit": orbit_data,
        "style": style_data,
        "image": image_bytes,
        "model": model
    }
    
    try:
        
        result = await spacecrafts.insert_one(doc)
        
        return utility.ok(str(result.inserted_id))
        
    except Exception as e:
        
        return utility.error(fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database insert failed: {str(e)}")

@router.post("/update/{id}", response_model=common.ActionModel)
async def post_update(id: str,
                      name: str = fastapi.Form(...),
                      mass: float = fastapi.Form(...),
                      orbit: str = fastapi.Form(...),
                      style: str = fastapi.Form(...),
                      image: fastapi.UploadFile | None = fastapi.File(None),
                      model: str = fastapi.Form(...),
                      client: AsyncIOMotorClient = fastapi.Depends(database.get_client)):
    """HTTP POST UPDATE spacecrafts collection

    Args:
        id (str): Document id
        name (str, optional): Name. Defaults to fastapi.Form(...).
        mass (float, optional): Mass. Defaults to fastapi.Form(...).
        orbit (str, optional): Orbit parameters. Defaults to fastapi.Form(...).
        style (str, optional): Style parameters. Defaults to fastapi.Form(...).
        image (fastapi.UploadFile | None, optional): Image. Defaults to fastapi.File(None).
        model (str, optional): 3D model name. Defaults to fastapi.Form(...).
        client (AsyncIOMotorClient, optional): MongoDB client. Defaults to fastapi.Depends(database.get_client).

    Returns:
        ActionModel: Result
    """
    
    spacecrafts: AsyncIOMotorCollection = client["spacecraft_dynamics_lab"]["spacecrafts"]
    
    # * Check existing name
    
    items: typing.List[schema.SpacecraftModel] = await spacecrafts.find({ "name": name }).to_list()
    
    if len(items) > 0:
        
        item: dict = serialize_spacecraft(items[0])
        
        if item["_id"] != id:
        
            return utility.error(fastapi.status.HTTP_403_FORBIDDEN, f"{name} already existing")
    
    # * Validate ID
    
    if not bson.ObjectId.is_valid(id):
        
        return utility.error(fastapi.status.HTTP_400_BAD_REQUEST, "Invalid ID")
    
    # * Parse orbit JSON
    
    try:
        
        orbit_data = convert_orbit(json.loads(orbit))
        
    except Exception:
        
        return utility.error(fastapi.status.HTTP_400_BAD_REQUEST, "Invalid orbit JSON")
    
     # * Parse style JSON
    
    try:
        
        style_data = json.loads(style)
        
    except Exception:
        
        return utility.error(fastapi.status.HTTP_400_BAD_REQUEST, "Invalid style JSON")

    # * Build document
    
    update_doc =\
    {
        "name": name,
        "mass": mass,
        "orbit": orbit_data,
        "style": style_data,
        "model": model
    }
    
    # * Read image if provided
    
    image_bytes: bson.Binary | None = None
    
    if image is not None:
        
        image_bytes = await image.read()
        
        update_doc["image"] = bson.Binary(image_bytes)

    # * Insert into MongoDB
    
    result = await spacecrafts.update_one({ "_id": bson.ObjectId(id) }, { "$set": update_doc })
    
    if result.matched_count == 0:
        
        return utility.error(fastapi.status.HTTP_404_NOT_FOUND, "Spacecraft not found")

    return utility.ok(str(id))

# >>> DELETE

@router.delete("/{id}", response_model=common.ActionModel)
async def delete_spacecraft(id: str,
                            client: AsyncIOMotorClient = fastapi.Depends(database.get_client)):
    """HTTP DELETE spacecrafts collection

    Args:
        id (str): Document id
        client (AsyncIOMotorClient, optional): MongoDB client. Defaults to fastapi.Depends(database.get_client).

    Returns:
        ActionModel: Result
    """
    
    spacecrafts: AsyncIOMotorCollection = client["spacecraft_dynamics_lab"]["spacecrafts"]

    # * Validate ID
    
    if not bson.ObjectId.is_valid(id):
        
        return utility.error(fastapi.status.HTTP_400_BAD_REQUEST, "Invalid ID")

    # * Attempt deletion
    
    result = await spacecrafts.delete_one({ "_id": bson.ObjectId(id) })

    if result.deleted_count == 0:
        
        return utility.error(fastapi.status.HTTP_404_NOT_FOUND, "Spacecraft not found")

    return utility.ok(str(id))
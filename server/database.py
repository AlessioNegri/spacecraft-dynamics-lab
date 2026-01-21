from motor.motor_asyncio import AsyncIOMotorClient

client: AsyncIOMotorClient | None = None

def get_client() -> AsyncIOMotorClient:
    """Retrieve the MongoDB client connection

    Returns:
        AsyncIOMotorClient: MongoDB client
    """
    
    if client is None:
        
        raise RuntimeError("MongoDB client not initialized")
    
    return client
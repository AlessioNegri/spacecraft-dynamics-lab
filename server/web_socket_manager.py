import fastapi

class WebSocketManager:
    """Manager for the web sockets
    """
    
    def __init__(self) -> None:
        """Constructor
        """
        
        self.clients: list[fastapi.WebSocket] = []

    async def connect(self, websocket: fastapi.WebSocket) -> None:
        """Connect a new web socket

        Args:
            websocket (fastapi.WebSocket): Web Socket connection
        """
        
        await websocket.accept()
        
        self.clients.append(websocket)

    def disconnect(self, websocket: fastapi.WebSocket) -> None:
        """Disconnect the existing web socket

        Args:
            websocket (fastapi.WebSocket): Web Socket connection
        """
        
        if websocket in self.clients:
            
            self.clients.remove(websocket)

    async def send_json(self, data: dict) -> None:
        """Send JSON data to all connected clients

        Args:
            data (dict): JSON dictionary data
        """
        
        for ws in self.clients:
            
            await ws.send_json(data)
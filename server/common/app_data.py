class AppData:
    
    mongo_enabled: bool = False
    mongo_error: str = ""
    mongo_url: str = ""
    db = None
    db_name: str = ""
    send_enabled: bool = False # ? Check if I can send to web socket
    stop_simulation: bool = False
import fastapi

def error(status_code: fastapi.status, message: str) -> fastapi.responses.JSONResponse:
    """Generate a standardized error JSON response

    Args:
        status_code (fastapi.status): Status code for the response
        message (str): Error message

    Returns:
        fastapi.responses.JSONResponse: JSON response with error message
    """
    
    return fastapi.responses.JSONResponse(status_code=status_code, content={ "error": message })

def ok(message: str) -> fastapi.responses.JSONResponse:
    """Generate a standardized success JSON response

    Args:
        status_code (fastapi.status): Status code for the response
        message (str): Success message
    Returns:
        fastapi.responses.JSONResponse: JSON response with success message
    """
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content={ "id": message })
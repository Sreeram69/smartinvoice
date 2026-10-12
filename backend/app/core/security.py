from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Validates that incoming requests contain the authorized API key.
    Prevents unauthorized public access to your PC's SQLite database,
    OCR, and document generation endpoints when exposed via a tunnel.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing 'X-API-Key' authentication header. Please configure your API key in the connection settings.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key.strip() != settings.API_KEY.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 'X-API-Key'. Access denied.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key

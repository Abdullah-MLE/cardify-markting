"""Auth Router."""
from fastapi import APIRouter, HTTPException
from backend.api.schemas import LoginRequest
from services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(req: LoginRequest):
    """
    Validates user credentials (username and password).
    Returns user data on successful login, or throws an error if invalid.
    """
    result = auth_service.authenticate_user(req.username, req.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result

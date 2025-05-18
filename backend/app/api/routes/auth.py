from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.ory import ory_client, verify_auth
from app.schemas.auth import AuthResponse, UserInfo
from typing import Dict, Any, Optional

router = APIRouter()


@router.get("", response_model=UserInfo)
async def auth(request: Request):
    """
    Get the current authenticated user's information
    
    This endpoint proxies the request to Ory Kratos and returns
    the user's traits in a simplified format.
    """
    try:
        # Get all cookies from the request
        cookies = request.cookies
        
        # Call Ory's whoami endpoint with the cookies
        user_data = await ory_client.whoami(cookies)
        
        # Extract user traits and ID
        return {
            "id": user_data["identity"]["id"],
            "traits": user_data["identity"]["traits"]
        }
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing authentication: {str(e)}"
        )


@router.get("/protected-example")
async def protected_example(user_data: Dict[str, Any] = Depends(verify_auth)):
    """
    Example of a protected route that requires authentication
    
    This route uses the verify_auth dependency to ensure the user is authenticated.
    """
    try:
        # Extract user email from the identity traits
        email = user_data.get("identity", {}).get("traits", {}).get("email", "unknown")
        
        return {
            "message": f"Hello, {email}! This is a protected route.",
            "user_id": user_data.get("identity", {}).get("id")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing protected route: {str(e)}"
        ) 
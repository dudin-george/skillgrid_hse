from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.ory import ory_client, verify_auth
from app.schemas.auth import AuthResponse, UserInfo, UserTraits
from typing import Dict, Any, Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=UserInfo)
async def auth(request: Request):
    """
    Get the current authenticated user's information
    
    This endpoint proxies the request to Ory Kratos and returns
    the user's traits in the structure defined by the Ory schema.
    """
    try:
        # Get all cookies from the request
        cookies = request.cookies
        
        if not cookies or not any(key.startswith("ory_session") for key in cookies.keys()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No valid Ory session cookie found"
            )
        
        # Call Ory's whoami endpoint with the cookies
        user_data = await ory_client.whoami(cookies)
        
        # Extract and validate user traits
        traits = user_data.get("identity", {}).get("traits", {})
        
        if not traits:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User identity traits missing in Ory response"
            )
        
        # Validate the traits match our expected schema
        try:
            # Even if name and surname are not in traits, they'll be None in validated_traits
            validated_traits = UserTraits(
                email=traits.get("email"),
                person_type=traits.get("person_type"),
                name=traits.get("name"),
                surname=traits.get("surname")
            )
        except Exception as validation_error:
            logger.error(f"Validation error: {str(validation_error)}")
            logger.error(f"User traits: {traits}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid user data: {str(validation_error)}"
            )
        
        # Return in the expected format
        return UserInfo(traits=validated_traits)
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger.exception("Error in auth endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing authentication: {str(e)}"
        ) 
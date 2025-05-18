from fastapi import Depends, Request, HTTPException, status
from typing import Dict, Any, Optional, Annotated, Union
from uuid import UUID
from app.core.ory import verify_auth, ory_client
from app.schemas.auth import UserTraits

class AuthDependency:
    """
    Authentication dependencies for endpoints that require authentication
    """
    
    @staticmethod
    async def authenticated_user(request: Request) -> Dict[str, Any]:
        """
        Dependency for endpoints requiring authentication
        Returns the full user data from Ory
        """
        return await verify_auth(request)
    
    @staticmethod
    async def get_user_id(request: Request) -> UUID:
        """
        Dependency for getting just the user ID
        """
        user_data = await verify_auth(request)
        return user_data.get("identity", {}).get("id")
    
    @staticmethod
    async def get_user_traits(request: Request) -> Dict[str, Any]:
        """
        Dependency for getting just the user traits
        """
        user_data = await verify_auth(request)
        return user_data.get("identity", {}).get("traits", {})
    
    @staticmethod
    async def require_person_type(request: Request, required_type: str) -> Dict[str, Any]:
        """
        Dependency for requiring a specific person type (candidate or recruiter)
        """
        user_data = await verify_auth(request)
        traits = user_data.get("identity", {}).get("traits", {})
        
        if traits.get("person_type") != required_type:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This endpoint requires {required_type} access"
            )
        
        return user_data
    
    @staticmethod
    async def require_candidate(request: Request) -> Dict[str, Any]:
        """
        Dependency for endpoints requiring candidate user type
        """
        return await AuthDependency.require_person_type(request, "candidate")
    
    @staticmethod
    async def require_recruiter(request: Request) -> Dict[str, Any]:
        """
        Dependency for endpoints requiring recruiter user type
        """
        return await AuthDependency.require_person_type(request, "recruiter")


# Common dependencies for use in routes
get_user_id = AuthDependency.get_user_id
get_user_traits = AuthDependency.get_user_traits
require_candidate = AuthDependency.require_candidate
require_recruiter = AuthDependency.require_recruiter
authenticated_user = AuthDependency.authenticated_user 
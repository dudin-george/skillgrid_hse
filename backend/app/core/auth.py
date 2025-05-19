from fastapi import Depends, Request, HTTPException, status
from typing import Dict, Any, Optional, Annotated, Union
from uuid import UUID
from app.core.ory import verify_auth, ory_client
from app.schemas.auth import UserTraits, AdminIdentityResponse

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
    
    @staticmethod
    async def get_identity_by_id(identity_id: str) -> Dict[str, Any]:
        """
        Get a user's complete identity information by ID
        
        This method uses the Ory Admin API to fetch the identity information
        for any user based on their ID. This is useful when you need to get
        information about users other than the currently authenticated one.
        
        Args:
            identity_id: The Ory identity ID to fetch
            
        Returns:
            The complete identity data from Ory
        """
        return await ory_client.get_identity(identity_id)
    
    @staticmethod
    async def get_parsed_identity_by_id(identity_id: str) -> AdminIdentityResponse:
        """
        Get a parsed and validated user identity by ID
        
        This method fetches the identity using the admin API and returns
        a validated Pydantic model with the most commonly needed fields.
        
        Args:
            identity_id: The Ory identity ID to fetch
            
        Returns:
            AdminIdentityResponse: A parsed and validated identity response
        """
        identity_data = await ory_client.get_identity(identity_id)
        return AdminIdentityResponse.from_ory_admin_response(identity_data)


# Common dependencies for use in routes
get_user_id = AuthDependency.get_user_id
get_user_traits = AuthDependency.get_user_traits
require_candidate = AuthDependency.require_candidate
require_recruiter = AuthDependency.require_recruiter
authenticated_user = AuthDependency.authenticated_user
get_identity_by_id = AuthDependency.get_identity_by_id
get_parsed_identity_by_id = AuthDependency.get_parsed_identity_by_id 
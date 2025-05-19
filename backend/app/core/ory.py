import os
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import httpx
from fastapi import Request, HTTPException, Depends, Header
from app.core.config import settings


class OryConfig:
    """Configuration for Ory Kratos integration"""
    ORY_PROJECT_ID = "cd3eac85-ed95-41dd-9969-9012ab8dea73"
    ORY_PROJECT_SLUG = "infallible-shaw-gpsjwuc0lg"
    ORY_BASE_URL = "https://auth.skillgrid.tech"
    ORY_ADMIN_BASE_URL = "https://infallible-shaw-gpsjwuc0lg.projects.oryapis.com"
    ORY_ADMIN_API_KEY = "ory_pat_e9NRxnc9W9vDIYjYqSlfgrGqEHo6zgex"
    

class OryClient:
    """Client for interacting with Ory APIs"""
    
    def __init__(self):
        self.base_url = OryConfig.ORY_BASE_URL
        self.admin_base_url = OryConfig.ORY_ADMIN_BASE_URL
        self.admin_api_key = OryConfig.ORY_ADMIN_API_KEY
        self.http_client = httpx.AsyncClient(base_url=self.base_url, follow_redirects=True)
        self.admin_http_client = httpx.AsyncClient(
            base_url=self.admin_base_url,
            headers={"Authorization": f"Bearer {self.admin_api_key}"},
            follow_redirects=True
        )
    
    async def whoami(self, cookies: dict) -> dict:
        """Get the current user's session information using session cookie"""
        try:
            # Pass the cookie from the frontend to Ory
            response = await self.http_client.get(
                "/sessions/whoami",
                cookies=cookies
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise HTTPException(status_code=401, detail="Not authenticated")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ory error: {response.text}"
                )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to Ory: {str(exc)}")
    
    async def get_identity(self, identity_id: str) -> dict:
        """
        Get a user's identity information from the Ory Admin API
        
        Args:
            identity_id: The Ory identity ID to fetch
            
        Returns:
            The identity data from Ory
            
        Raises:
            HTTPException: If the request fails or returns an error
        """
        try:
            response = await self.admin_http_client.get(f"/admin/identities/{identity_id}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Identity not found")
            elif response.status_code == 401:
                raise HTTPException(status_code=401, detail="Not authorized to access Ory admin API")
            else:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"Ory admin error: {response.text}"
                )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to Ory admin API: {str(exc)}")
    
    async def update_identity_metadata(self, identity_id: str, metadata: Dict[str, Any]) -> dict:
        """
        Update a user's metadata in Ory
        
        Args:
            identity_id: The Ory identity ID to update
            metadata: The metadata to store
            
        Returns:
            The updated identity data from Ory
            
        Raises:
            HTTPException: If the request fails or returns an error
        """
        try:
            # First get the current identity
            current_identity = await self.get_identity(identity_id)
            
            # Create the patch data
            patch_data = {
                "metadata_public": metadata
            }
            
            # Update the identity
            response = await self.admin_http_client.put(
                f"/admin/identities/{identity_id}",
                json=patch_data
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Identity not found")
            elif response.status_code == 401:
                raise HTTPException(status_code=401, detail="Not authorized to access Ory admin API")
            else:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"Ory admin error: {response.text}"
                )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error connecting to Ory admin API: {str(exc)}")
    
    async def close(self):
        """Close the HTTP client sessions"""
        await self.http_client.aclose()
        await self.admin_http_client.aclose()


# Create a global instance of the Ory client
ory_client = OryClient()


async def verify_auth(request: Request) -> Dict[str, Any]:
    """
    Dependency for verifying authentication
    
    Extracts the session cookie from the request and verifies it with Ory
    """
    cookies = request.cookies
    return await ory_client.whoami(cookies) 
import os
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import httpx
from fastapi import Request, HTTPException, Depends
from app.core.config import settings


class OryConfig:
    """Configuration for Ory Kratos integration"""
    ORY_PROJECT_ID = "cd3eac85-ed95-41dd-9969-9012ab8dea73"
    ORY_PROJECT_SLUG = "infallible-shaw-gpsjwuc0lg"
    ORY_BASE_URL = "https://auth.skillgrid.tech"
    

class OryClient:
    """Client for interacting with Ory APIs"""
    
    def __init__(self):
        self.base_url = OryConfig.ORY_BASE_URL
        self.http_client = httpx.AsyncClient(base_url=self.base_url)
    
    async def whoami(self, cookies: dict) -> dict:
        """Get the current user's session information"""
        try:
            # Pass the cookie from the frontend to Ory
            response = await self.http_client.get(
                "/api/kratos/public/sessions/whoami",
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
    
    async def close(self):
        """Close the HTTP client session"""
        await self.http_client.aclose()


# Create a global instance of the Ory client
ory_client = OryClient()


async def verify_auth(request: Request) -> Dict[str, Any]:
    """
    Dependency for verifying authentication
    
    Can be used on routes that require authentication:
    @router.get("/protected")
    async def protected_route(user_data: dict = Depends(verify_auth)):
        return {"message": f"Hello, {user_data['identity']['traits']['email']}"}
    """
    cookies = request.cookies
    return await ory_client.whoami(cookies) 
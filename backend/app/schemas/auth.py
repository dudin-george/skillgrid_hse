from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List, Literal
from uuid import UUID
from datetime import datetime


class OryIdentity(BaseModel):
    """Represents an Ory Identity"""
    id: UUID
    schema_id: str = Field(alias="schema_id")
    schema_url: str = Field(alias="schema_url")
    state: Optional[str] = None
    state_changed_at: Optional[datetime] = Field(None, alias="state_changed_at")
    traits: Dict[str, Any]
    verifiable_addresses: Optional[List[Dict[str, Any]]] = Field(None, alias="verifiable_addresses")
    recovery_addresses: Optional[List[Dict[str, Any]]] = Field(None, alias="recovery_addresses")
    metadata_public: Optional[Dict[str, Any]] = Field(None, alias="metadata_public")
    created_at: Optional[datetime] = Field(None, alias="created_at")
    updated_at: Optional[datetime] = Field(None, alias="updated_at")

    
class OrySession(BaseModel):
    """Represents an Ory Session response"""
    id: UUID
    active: bool
    expires_at: datetime = Field(alias="expires_at")
    authenticated_at: datetime = Field(alias="authenticated_at")
    issued_at: datetime = Field(alias="issued_at")
    identity: OryIdentity
    

class AuthResponse(BaseModel):
    """Response schema for auth endpoints"""
    session: OrySession
    user_id: UUID
    
    @classmethod
    def from_ory_session(cls, ory_data: dict) -> "AuthResponse":
        """Create an AuthResponse from an Ory session response"""
        return cls(
            session=OrySession(**ory_data),
            user_id=ory_data["identity"]["id"]
        )


class UserTraits(BaseModel):
    """User traits according to the Ory schema"""
    email: EmailStr = Field(..., title="E-Mail", max_length=320)
    person_type: Literal["candidate", "recruiter"] = Field(..., title="Person Type")
    name: Optional[str] = Field(None, title="First Name")
    surname: Optional[str] = Field(None, title="Last Name")
    
    class Config:
        extra = "forbid"


class UserInfo(BaseModel):
    """User information matching the Ory schema structure"""
    traits: UserTraits
    user_id: UUID


class AdminIdentityResponse(BaseModel):
    """Parsed response from Ory Admin API for identities"""
    id: UUID
    state: str
    traits: UserTraits
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_ory_admin_response(cls, data: dict) -> "AdminIdentityResponse":
        """Create an AdminIdentityResponse from an Ory admin API response"""
        return cls(
            id=data["id"],
            state=data["state"],
            traits=UserTraits(**data["traits"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        ) 
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    location: Optional[str] = None


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    location: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# Artist Schemas
class ArtistBase(BaseModel):
    name: str
    ticketmaster_id: Optional[str] = None


class ArtistCreate(ArtistBase):
    pass


class ArtistResponse(ArtistBase):
    id: UUID
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# Event Schemas
class EventBase(BaseModel):
    name: str
    ticketmaster_id: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    ticket_url: Optional[str] = None


class EventCreate(EventBase):
    artist_id: UUID


class EventResponse(EventBase):
    id: UUID
    artist_id: UUID
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# Interest Schemas
class InterestBase(BaseModel):
    user_id: UUID
    artist_id: UUID


class InterestCreate(InterestBase):
    pass


class InterestResponse(InterestBase):
    id: UUID
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# SavedEvent Schemas
class SavedEventBase(BaseModel):
    user_id: UUID
    event_id: UUID


class SavedEventCreate(SavedEventBase):
    pass


class SavedEventResponse(SavedEventBase):
    id: UUID
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.schemas import ArtistCreate, ArtistResponse, ArtistUpdate
from app.database.database_handler import (
    create_artist,
    get_artists,
    get_artist_by_id,
    update_artist,
    delete_artist,
)
from app.database.database import get_db
from app.main import get_current_admin

router = APIRouter(
    prefix="/artists",
    tags=["artists"],
    dependencies=[Depends(get_current_admin)],  # Admin-only for all artist CRUD
)

@router.post("/", response_model=ArtistResponse, status_code=status.HTTP_201_CREATED)
def create_artist_route(
    artist_in: ArtistCreate,
    db: Session = Depends(get_db),
):
    return create_artist(db, artist_in)

@router.get("/", response_model=list[ArtistResponse])
def list_artists_route(
    db: Session = Depends(get_db),
):
    return get_artists(db)

@router.get("/{artist_id}", response_model=ArtistResponse)
def read_artist_route(
    artist_id: UUID,
    db: Session = Depends(get_db),
):
    artist = get_artist_by_id(db, artist_id)
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found")
    return artist

@router.patch("/{artist_id}", response_model=ArtistResponse)
def update_artist_route(
    artist_id: UUID,
    artist_in: ArtistUpdate,
    db: Session = Depends(get_db),
):
    updated = update_artist(db, artist_id, artist_in)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found")
    return updated

@router.delete("/{artist_id}", response_model=ArtistResponse)
def delete_artist_route(
    artist_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = delete_artist(db, artist_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found")
    return deleted

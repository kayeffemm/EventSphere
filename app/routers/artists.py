from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.models import User
from app.schemas.schemas import ArtistCreate, ArtistResponse, ArtistUpdate
from app.database.database_handler import (
    create_artist,
    get_artists,
    get_artist_by_id,
    update_artist,
    delete_artist,
)
from app.database.database import get_db
from app.main import get_current_user

router = APIRouter(prefix="/artists", tags=["artists"])

@router.post("/", response_model=ArtistResponse)
def create_artist_route(
    artist_in: ArtistCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # create a new artist
    return create_artist(db, artist_in)

@router.get("/", response_model=list[ArtistResponse])
def list_artists_route(db: Session = Depends(get_db)):
    # list all artists
    return get_artists(db)

@router.get("/{artist_id}", response_model=ArtistResponse)
def read_artist(
    artist_id: UUID,
    db: Session = Depends(get_db)
):
    # get one artist
    artist = get_artist_by_id(db, artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist

@router.patch("/{artist_id}", response_model=ArtistResponse)
def update_artist_route(
    artist_id: UUID,
    artist_in: ArtistUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # update artist info
    updated = update_artist(db, artist_id, artist_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Artist not found")
    return updated

@router.delete("/{artist_id}", response_model=ArtistResponse)
def delete_artist_route(
    artist_id: UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # delete an artist
    deleted = delete_artist(db, artist_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Artist not found")
    return deleted

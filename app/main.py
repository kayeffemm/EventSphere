from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta, timezone

from app.database.database import Base, engine, get_db
from app.models.models import User, Interest, Artist
from app.schemas.schemas import (
    UserCreate, UserResponse, UserUpdate, Token,
    ArtistResponse, EventResponse
)
from app.database.database_handler import (
    create_user, get_users, get_user_by_id, update_user, delete_user,
    get_or_create_artist_by_ticketmaster_data,
    get_or_create_event_by_ticketmaster_data, get_events_for_artist
)
from app.services.discoveryapi import search_artist, get_upcoming_events
from app.auth import verify_password, create_access_token, verify_access_token

SYNC_THRESHOLD = timedelta(hours=12)

# Initialize the database
Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# Public auth endpoints
@app.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return create_user(db, user_data)


@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token({"sub": str(user.id)}, timedelta(minutes=60))
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# Discovery + follow + sync routes
@app.get("/artists/search/{artist_name}")
def find_artist(artist_name: str):
    results = search_artist(artist_name)
    if not results:
        raise HTTPException(status_code=404, detail="Artist not found")
    return results


@app.get("/artists/{artist_id}/discovery_events", response_model=list[EventResponse])
def find_events(artist_id: str):
    events = get_upcoming_events(artist_id)
    return events or []


@app.post("/follow_artist/{artist_name}", response_model=ArtistResponse)
def follow_artist_route(
    artist_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    raw = search_artist(artist_name)
    if not raw:
        raise HTTPException(status_code=404, detail="Artist not found")
    artist = get_or_create_artist_by_ticketmaster_data(db, raw[0])
    link = db.query(Interest).filter_by(user_id=current_user.id, artist_id=artist.id).first()
    if not link:
        db.add(Interest(user_id=current_user.id, artist_id=artist.id))
        db.commit()
    return artist


@app.post("/sync_events/{artist_id}", response_model=list[EventResponse])
def sync_events_route(
    artist_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user follows the artist
    link = db.query(Interest).filter_by(user_id=current_user.id, artist_id=artist_id).first()
    if not link:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Must follow to sync events")

    # Load the Artist record
    artist = db.query(Artist).filter_by(id=artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    # If data synced recently, just return data from DB
    if artist.last_synced_at and (datetime.now(timezone.utc) - artist.last_synced_at) < SYNC_THRESHOLD:
        return get_events_for_artist(db, artist_id)

    # If not synced recently, fetch from Ticketmaster API
    raw_events = get_upcoming_events(artist.ticketmaster_id) or []
    synced = []
    for ev in raw_events:
        synced.append(get_or_create_event_by_ticketmaster_data(db, artist_id, ev))

    # Mark the sync time
    artist.last_synced_at = datetime.now(timezone.utc)
    db.commit()

    return synced


@app.get("/artists/{artist_id}/events", response_model=list[EventResponse])
def list_stored_events_route(
    artist_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    link = db.query(Interest).filter_by(user_id=current_user.id, artist_id=artist_id).first()
    if not link:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Must follow to view events")
    return get_events_for_artist(db, artist_id)


# User management
@app.get("/users/", response_model=list[UserResponse])
def list_users_route(db: Session = Depends(get_db)):
    return get_users(db)


@app.get("/users/{user_id}", response_model=UserResponse)
def read_user_route(user_id: UUID, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user_route(
    user_id: UUID,
    user_in: UserUpdate,
    db: Session = Depends(get_db)
):
    updated = update_user(db, user_id, user_in)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@app.delete("/users/{user_id}", response_model=UserResponse)
def delete_user_route(user_id: UUID, db: Session = Depends(get_db)):
    deleted = delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted


# Mount routers for grouped CRUD
from app.routers import artists, events, interests, saved_events

app.include_router(artists.router)
app.include_router(events.router)
app.include_router(interests.router)
app.include_router(saved_events.router)

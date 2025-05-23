from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import timedelta

from app.models import models
from app.schemas import schemas
from app.database import database_handler
from app.database.database import get_db, Base, engine
from app.services.discoveryapi import search_artist, get_upcoming_events
from app.auth import hash_password, verify_password, create_access_token, verify_access_token


# Initialize the database
Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    print("Received token:", token)  #TODO only for debugging, remove later

    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


@app.get("/")
def read_root():
    return {"message": "Welcome to EventSphere API"}


@app.post("/signup", response_model=schemas.UserResponse)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Registers a new user using the database_handler function."""
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    return database_handler.create_user(db, user_data)


@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Generate JWT token
    access_token = create_access_token({"sub": str(user.id)}, timedelta(minutes=60))
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


# User Endpoints
@app.get("/users/", response_model=list[schemas.UserResponse])
def list_users(db: Session = Depends(get_db)):
    return database_handler.get_users(db)


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = database_handler.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: UUID, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    updated_user = database_handler.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@app.delete("/users/{user_id}", response_model=schemas.UserResponse)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    deleted_user = database_handler.delete_user(db, user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user


# Artist Endpoints
@app.post("/artists/", response_model=schemas.ArtistResponse)
def create_artist(artist: schemas.ArtistCreate, db: Session = Depends(get_db)):
    return database_handler.create_artist(db, artist)


@app.get("/artists/", response_model=list[schemas.ArtistResponse])
def list_artists(db: Session = Depends(get_db)):
    return database_handler.get_artists(db)


# Event Endpoints
@app.post("/events/", response_model=schemas.EventResponse)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    return database_handler.create_event(db, event)


@app.get("/events/", response_model=list[schemas.EventResponse])
def list_events(db: Session = Depends(get_db)):
    return database_handler.get_events(db)


# Interest Endpoints
@app.post("/interests/", response_model=schemas.InterestResponse)
def create_interest(
    interest: schemas.InterestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Override interest.user_id to prevent spoofing
    interest.user_id = current_user.id
    return database_handler.create_interest(db, interest)


@app.get("/interests/", response_model=list[schemas.InterestResponse])
def list_interests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return database_handler.get_interests_for_user(db, current_user.id)


# Saved Event Endpoints
@app.post("/saved_events/", response_model=schemas.SavedEventResponse)
def create_saved_event(
    saved_event: schemas.SavedEventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    saved_event.user_id = current_user.id
    return database_handler.create_saved_event(db, saved_event)


@app.get("/saved_events/", response_model=list[schemas.SavedEventResponse])
def list_saved_events(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return database_handler.get_saved_events_for_user(db, current_user.id)

#TODO: filter results, add artist search based on location
@app.get("/artists/search/{artist_name}")
def find_artist(artist_name: str):
    """Search for an artist on Ticketmaster."""
    results = search_artist(artist_name)
    if not results:
        return {"message": "No artists found"}
    return results


@app.get("/events/{artist_id}")
def find_events(artist_id: str):
    """Get upcoming events for an artist."""
    events = get_upcoming_events(artist_id)
    if not events:
        return {"message": "No events found"}
    return events


@app.post("/follow_artist/{artist_name}", response_model=schemas.ArtistResponse)
def follow_artist(
    artist_name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    results = search_artist(artist_name)
    if not results:
        raise HTTPException(status_code=404, detail="Artist not found")

    artist_data = results[0]

    artist = database_handler.get_or_create_artist_by_ticketmaster_data(db, artist_data)

    interest_exists = db.query(models.Interest).filter_by(
        user_id=current_user.id,
        artist_id=artist.id
    ).first()

    if not interest_exists:
        new_interest = models.Interest(user_id=current_user.id, artist_id=artist.id)
        db.add(new_interest)
        db.commit()

    return artist


@app.post("/sync_events/{artist_id}", response_model=list[schemas.EventResponse])
def sync_events(
    artist_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify the user follows this artist
    interest = (
        db.query(models.Interest)
          .filter_by(user_id=current_user.id, artist_id=artist_id)
          .first()
    )
    if not interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You must follow this artist before syncing events"
        )

    # Load the artist from the DB
    artist = db.query(models.Artist).filter_by(id=artist_id).first()
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found")

    # Fetch & clean events via your Discovery API
    raw_events = get_upcoming_events(artist.ticketmaster_id)
    if not raw_events:
        return []

    # Persist each event (get_or_create helper)
    synced_events = []
    for ev_data in raw_events:
        ev = database_handler.get_or_create_event_by_ticketmaster_data(
            db, artist.id, ev_data
        )
        synced_events.append(ev)

    return synced_events


@app.get("/artists/{artist_id}/events", response_model=list[schemas.EventResponse])
def list_stored_events(
    artist_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    interest = (
        db.query(models.Interest)
          .filter_by(user_id=current_user.id, artist_id=artist_id)
          .first()
    )
    if not interest:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must follow this artist to view its events"
        )

    return database_handler.get_events_for_artist(db, artist_id)
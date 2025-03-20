import models, schemas, database_handler
from discoveryapi import search_artist, get_upcoming_events
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db, Base, engine
from uuid import UUID
from auth import hash_password, verify_password, create_access_token, verify_access_token
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Initialize the database
Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


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
def create_interest(interest: schemas.InterestCreate, db: Session = Depends(get_db)):
    return database_handler.create_interest(db, interest)


@app.get("/interests/", response_model=list[schemas.InterestResponse])
def list_interests(db: Session = Depends(get_db)):
    return database_handler.get_interests(db)


# Saved Event Endpoints
@app.post("/saved_events/", response_model=schemas.SavedEventResponse)
def create_saved_event(saved_event: schemas.SavedEventCreate, db: Session = Depends(get_db)):
    return database_handler.create_saved_event(db, saved_event)


@app.get("/saved_events/", response_model=list[schemas.SavedEventResponse])
def list_saved_events(db: Session = Depends(get_db)):
    return database_handler.get_saved_events(db)

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
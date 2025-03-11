from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Base, engine
import models, schemas, crud
from uuid import UUID

# Initialize the database
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to EventSphere API"}

# User Endpoints
@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.get("/users/", response_model=list[schemas.UserResponse])
def list_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: UUID, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/{user_id}", response_model=schemas.UserResponse)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    deleted_user = crud.delete_user(db, user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user

# Artist Endpoints
@app.post("/artists/", response_model=schemas.ArtistResponse)
def create_artist(artist: schemas.ArtistCreate, db: Session = Depends(get_db)):
    return crud.create_artist(db, artist)

@app.get("/artists/", response_model=list[schemas.ArtistResponse])
def list_artists(db: Session = Depends(get_db)):
    return crud.get_artists(db)

# Event Endpoints
@app.post("/events/", response_model=schemas.EventResponse)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    return crud.create_event(db, event)

@app.get("/events/", response_model=list[schemas.EventResponse])
def list_events(db: Session = Depends(get_db)):
    return crud.get_events(db)

# Interest Endpoints
@app.post("/interests/", response_model=schemas.InterestResponse)
def create_interest(interest: schemas.InterestCreate, db: Session = Depends(get_db)):
    return crud.create_interest(db, interest)

@app.get("/interests/", response_model=list[schemas.InterestResponse])
def list_interests(db: Session = Depends(get_db)):
    return crud.get_interests(db)

# Saved Event Endpoints
@app.post("/saved_events/", response_model=schemas.SavedEventResponse)
def create_saved_event(saved_event: schemas.SavedEventCreate, db: Session = Depends(get_db)):
    return crud.create_saved_event(db, saved_event)

@app.get("/saved_events/", response_model=list[schemas.SavedEventResponse])
def list_saved_events(db: Session = Depends(get_db)):
    return crud.get_saved_events(db)

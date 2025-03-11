from sqlalchemy.orm import Session
import models
import schemas
import uuid
from uuid import UUID

# User CRUD
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(id=uuid.uuid4(), **user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session):
    return db.query(models.User).all()

def get_user_by_id(db: Session, user_id: UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()

def update_user(db: Session, user_id: UUID, user_update: schemas.UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: UUID):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    db.delete(db_user)
    db.commit()
    return db_user

# Artist CRUD
def create_artist(db: Session, artist: schemas.ArtistCreate):
    db_artist = models.Artist(id=uuid.uuid4(), **artist.model_dump())
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist

def get_artists(db: Session):
    return db.query(models.Artist).all()

# Event CRUD
def create_event(db: Session, event: schemas.EventCreate):
    db_event = models.Event(id=uuid.uuid4(), **event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_events(db: Session):
    return db.query(models.Event).all()

# Interest CRUD
def create_interest(db: Session, interest: schemas.InterestCreate):
    db_interest = models.Interest(id=uuid.uuid4(), **interest.model_dump())
    db.add(db_interest)
    db.commit()
    db.refresh(db_interest)
    return db_interest

def get_interests(db: Session):
    return db.query(models.Interest).all()

# SavedEvent CRUD
def create_saved_event(db: Session, saved_event: schemas.SavedEventCreate):
    db_saved_event = models.SavedEvent(id=uuid.uuid4(), **saved_event.model_dump())
    db.add(db_saved_event)
    db.commit()
    db.refresh(db_saved_event)
    return db_saved_event

def get_saved_events(db: Session):
    return db.query(models.SavedEvent).all()

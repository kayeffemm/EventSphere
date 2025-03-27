from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
import uuid
from uuid import UUID
from app.auth import hash_password


# User CRUD
def create_user(db: Session, user_data: schemas.UserCreate):
    """Handles user creation, including password hashing."""
    hashed_pw = hash_password(user_data.password)
    new_user = models.User(
        id=uuid.uuid4(),
        name=user_data.name,
        email=user_data.email,
        password=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


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
def create_interest(db: Session, interest_data: schemas.InterestCreate):
    existing = db.query(models.Interest).filter_by(
        user_id=interest_data.user_id,
        artist_id=interest_data.artist_id
    ).first()

    if existing:
        return existing

    new_interest = models.Interest(
        user_id=interest_data.user_id,
        artist_id=interest_data.artist_id
    )
    db.add(new_interest)
    db.commit()
    db.refresh(new_interest)
    return new_interest


def get_interests(db: Session):
    return db.query(models.Interest).all()


def get_interests_for_user(db: Session, user_id: UUID):
    return db.query(models.Interest).filter(models.Interest.user_id == user_id).all()


# SavedEvent CRUD
def get_saved_events_for_user(db: Session, user_id: UUID):
    return db.query(models.SavedEvent).filter(models.SavedEvent.user_id == user_id).all()


def create_saved_event(db: Session, saved_event_data: schemas.SavedEventCreate):
    existing = db.query(models.SavedEvent).filter_by(
        user_id=saved_event_data.user_id,
        event_id=saved_event_data.event_id
    ).first()

    if existing:
        return existing

    new_saved_event = models.SavedEvent(
        user_id=saved_event_data.user_id,
        event_id=saved_event_data.event_id
    )
    db.add(new_saved_event)
    db.commit()
    db.refresh(new_saved_event)
    return new_saved_event


def get_saved_events(db: Session):
    return db.query(models.SavedEvent).all()


def get_or_create_artist_by_ticketmaster_data(db: Session, artist_data: dict):
    """
    Check if artist exists in DB by Ticketmaster ID.
    If not, create and return it.
    """
    ticketmaster_id = artist_data.get("id")
    name = artist_data.get("name")

    if not ticketmaster_id or not name:
        return None

    existing = db.query(models.Artist).filter_by(ticketmaster_id=ticketmaster_id).first()
    if existing:
        return existing

    new_artist = models.Artist(
        id=uuid.uuid4(),
        name=name,
        ticketmaster_id=ticketmaster_id
    )
    db.add(new_artist)
    db.commit()
    db.refresh(new_artist)
    return new_artist

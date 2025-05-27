from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.models import User
from app.schemas.schemas import InterestCreate, InterestResponse, InterestUpdate
from app.database.database_handler import (
    create_interest,
    get_interests_for_user,
    get_interest_by_id,
    update_interest,
    delete_interest,
)
from app.database.database import get_db
from app.main import get_current_user

router = APIRouter(prefix="/interests", tags=["interests"])

@router.post("/", response_model=InterestResponse)
def create_interest_route(
    interest_in: InterestCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # link current user to artist
    interest_in.user_id = _current_user.id
    return create_interest(db, interest_in)

@router.get("/", response_model=list[InterestResponse])
def list_interests_route(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # return only my interests
    return get_interests_for_user(db, _current_user.id)

@router.get("/{interest_id}", response_model=InterestResponse)
def read_interest(
    interest_id: UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # get one interest
    interest = get_interest_by_id(db, interest_id)
    if not interest or interest.user_id != _current_user.id:
        raise HTTPException(status_code=404, detail="Interest not found")
    return interest

@router.patch("/{interest_id}", response_model=InterestResponse)
def update_interest_route(
    interest_id: UUID,
    interest_in: InterestUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # only update own interest
    interest = get_interest_by_id(db, interest_id)
    if not interest or interest.user_id != _current_user.id:
        raise HTTPException(status_code=404, detail="Interest not found")
    return update_interest(db, interest_id, interest_in)

@router.delete("/{interest_id}", response_model=InterestResponse)
def delete_interest_route(
    interest_id: UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),  # require login
):
    # only delete own interest
    interest = get_interest_by_id(db, interest_id)
    if not interest or interest.user_id != _current_user.id:
        raise HTTPException(status_code=404, detail="Interest not found")
    return delete_interest(db, interest_id)

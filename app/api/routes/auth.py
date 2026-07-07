from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas import AuthResponse, LoginRequest, SignupAdminRequest, SignupSupervisorRequest
from app.db.database import get_db
from app.db.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_response(user: User) -> Dict:
    return {
        "token": "jwt-token",
        "user": {
            "id": user.id,
            "role": user.role,
            "name": user.name,
            "employeeId": user.employee_id,
            "gender": user.gender,
            "phone": user.phone,
            "email": user.email,
            "mineName": "Jharia Coalfield",
            "companyName": "BharatMinerals Ltd.",
            "lastLogin": user.last_login.isoformat() if user.last_login else None,
            "sectorId": user.sector_id,
            "sectorName": None,
        },
    }


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.get("email")).first()
    if not user or user.password_hash != payload.get("password"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if payload.get("role") and user.role != payload.get("role"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role mismatch")
    user.last_login = datetime.utcnow()
    db.commit()
    return _user_response(user)


@router.post("/signup/admin", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup_admin(payload: SignupAdminRequest, db: Session = Depends(get_db)):
    user = User(
        role="admin",
        name=payload["name"],
        employee_id=payload["employeeId"],
        gender=payload["gender"],
        phone=payload["phone"],
        email=payload["email"],
        password_hash=payload["password"],
        mine_id="mine-1",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_response(user)


@router.post("/signup/supervisor", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup_supervisor(payload: SignupSupervisorRequest, db: Session = Depends(get_db)):
    user = User(
        role="supervisor",
        name=payload["name"],
        employee_id=payload["employeeId"],
        gender=payload["gender"],
        phone=payload["phone"],
        email=payload["email"],
        password_hash=payload["password"],
        mine_id="mine-1",
        sector_id=payload.get("sectorId"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_response(user)

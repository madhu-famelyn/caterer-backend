import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, security
from database import get_db
from routers.caterers import caterer_to_out

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=schemas.LoginResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    # Find caterer by email
    caterer = db.query(models.Caterer).filter(models.Caterer.email == payload.email).first()
    if not caterer or not security.verify_password(payload.password, caterer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password",
        )

    # Generate JWT token
    access_token = security.create_access_token(data={"sub": str(caterer.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "caterer": caterer_to_out(caterer),
    }


@router.post("/forgot-password", response_model=schemas.MessageResponse)
def forgot_password(payload: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    caterer = db.query(models.Caterer).filter(models.Caterer.email == payload.email).first()
    if not caterer:
        # Avoid user enumeration by returning a generic success message
        return {"message": "If this email is registered, a password reset link has been printed to the server logs."}

    # Generate reset token valid for 15 minutes
    token = uuid.uuid4().hex
    caterer.reset_token = token
    caterer.reset_token_expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    db.commit()

    # Log to server console (simulating sending an email reset link)
    reset_link = f"http://localhost:5173/reset-password?token={token}"
    print("\n" + "=" * 60)
    print("PASSWORD RESET LINK GENERATED (SIMULATED EMAIL)")
    print(f"Caterer: {caterer.business_name} (Owner: {caterer.owner_name})")
    print(f"Reset Link: {reset_link}")
    print("=" * 60 + "\n")

    return {"message": "If this email is registered, a password reset link has been printed to the server logs."}


@router.post("/reset-password", response_model=schemas.MessageResponse)
def reset_password(payload: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    caterer = db.query(models.Caterer).filter(models.Caterer.reset_token == payload.token).first()
    if not caterer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )

    expires = caterer.reset_token_expires
    if expires:
        # Ensure UTC timezone awareness for the database datetime object
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) > expires:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired.",
            )

    # Hash new password and clear reset columns
    caterer.hashed_password = security.hash_password(payload.new_password)
    caterer.reset_token = None
    caterer.reset_token_expires = None
    db.commit()

    return {"message": "Password reset successfully. You can now log in with your new password."}


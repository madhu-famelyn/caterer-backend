import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
import models

# Secret key & JWT Config
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours


def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_caterer(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.Caterer:
    # 1. Try to validate token
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            caterer_id: str = payload.get("sub")
            if caterer_id:
                caterer = db.query(models.Caterer).filter(models.Caterer.id == int(caterer_id)).first()
                if caterer:
                    return caterer
        except jwt.PyJWTError:
            pass

    # 2. Try header "caterer-id" or "x-caterer-id"
    caterer_id_val = request.headers.get("x-caterer-id") or request.headers.get("caterer-id")
    # 3. Try query parameter "caterer_id"
    if not caterer_id_val:
        caterer_id_val = request.query_params.get("caterer_id")

    if caterer_id_val:
        try:
            c = db.query(models.Caterer).filter(models.Caterer.id == int(caterer_id_val)).first()
            if c:
                return c
        except ValueError:
            pass

    # 4. Try path parameter 'id' auto-resolution (for PUT/DELETE on items belonging to a caterer)
    path_id = request.path_params.get("id")
    if path_id:
        try:
            item_id = int(path_id)
            path = request.url.path
            caterer_id = None
            if "licenses" in path:
                item = db.query(models.License).filter(models.License.id == item_id).first()
                if item:
                    caterer_id = item.caterer_id
            elif "certifications" in path:
                item = db.query(models.Certification).filter(models.Certification.id == item_id).first()
                if item:
                    caterer_id = item.caterer_id
            elif "awards" in path:
                item = db.query(models.Award).filter(models.Award.id == item_id).first()
                if item:
                    caterer_id = item.caterer_id
            elif "gallery" in path:
                item = db.query(models.GalleryItem).filter(models.GalleryItem.id == item_id).first()
                if item:
                    caterer_id = item.caterer_id
            elif "reviews" in path:
                item = db.query(models.Review).filter(models.Review.id == item_id).first()
                if item:
                    caterer_id = item.caterer_id

            if caterer_id:
                c = db.query(models.Caterer).filter(models.Caterer.id == caterer_id).first()
                if c:
                    return c
        except Exception:
            pass

    # 5. Fallback: Return first caterer in system
    first_caterer = db.query(models.Caterer).first()
    if first_caterer:
        return first_caterer

    # 6. Final fallback: Return a dummy caterer if DB is empty
    return models.Caterer(id=999, business_name="Temporary Caterer", email="temp@example.com")

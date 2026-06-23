from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ── Caterer ──────────────────────────────────────────────────────────────────

class CatererCreate(BaseModel):
    business_name: str
    owner_name: Optional[str] = None
    email: EmailStr
    mobile: Optional[str] = None
    password: str

    address: Optional[str] = None
    city: str
    state: str
    zip: Optional[str] = None

    cuisine_type: Optional[str] = None
    bio: Optional[str] = None
    price_per_guest: Optional[float] = None
    service_tags: Optional[List[str]] = []
    image_url: Optional[str] = None


class CatererUpdate(BaseModel):
    business_name: Optional[str] = None
    owner_name: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    cuisine_type: Optional[str] = None
    bio: Optional[str] = None
    price_per_guest: Optional[float] = None
    service_tags: Optional[List[str]] = None
    image_url: Optional[str] = None
    verified: Optional[bool] = None


class CatererOut(BaseModel):
    id: int
    business_name: str
    owner_name: Optional[str] = None
    email: str
    mobile: Optional[str] = None

    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None

    cuisine_type: Optional[str] = None
    bio: Optional[str] = None
    price_per_guest: Optional[float] = None
    tags: Optional[List[str]] = []

    image_url: Optional[str] = None
    rating: float = 0.0
    review_count: int = 0
    verified: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Auth ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    caterer: CatererOut


class MessageResponse(BaseModel):
    message: str


# ── Password Reset ────────────────────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# ── License Schemas ───────────────────────────────────────────────────────────

class LicenseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    document_url: Optional[str] = None
    expiry_date: Optional[datetime] = None


class LicenseOut(BaseModel):
    id: int
    caterer_id: int
    title: str
    description: Optional[str] = None
    document_url: Optional[str] = None
    expiry_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Certification Schemas ──────────────────────────────────────────────────────

class CertificationCreate(BaseModel):
    title: str
    issued_by: Optional[str] = None
    issue_date: Optional[datetime] = None
    certificate_url: Optional[str] = None


class CertificationOut(BaseModel):
    id: int
    caterer_id: int
    title: str
    issued_by: Optional[str] = None
    issue_date: Optional[datetime] = None
    certificate_url: Optional[str] = None

    class Config:
        from_attributes = True


# ── Award Schemas ──────────────────────────────────────────────────────────────

class AwardCreate(BaseModel):
    title: str
    year: Optional[int] = None
    image_url: Optional[str] = None
    description: Optional[str] = None


class AwardOut(BaseModel):
    id: int
    caterer_id: int
    title: str
    year: Optional[int] = None
    image_url: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


# ── Gallery Schemas ────────────────────────────────────────────────────────────

class GalleryItemCreate(BaseModel):
    type: str = "photo"
    file_url: str


class GalleryItemOut(BaseModel):
    id: int
    caterer_id: int
    type: str
    file_url: str

    class Config:
        from_attributes = True


# ── Review Schemas ─────────────────────────────────────────────────────────────

class ReviewCreate(BaseModel):
    caterer_id: int
    customer_name: str
    rating: float = 5.0
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    caterer_id: int
    customer_name: str
    rating: float
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Bulk Upload Schemas ────────────────────────────────────────────────────────

class BulkUploadError(BaseModel):
    email: str
    error: str


class BulkUploadResponse(BaseModel):
    created_count: int
    failed_count: int
    created: List[CatererOut]
    errors: List[BulkUploadError]




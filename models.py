from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Caterer(Base):
    __tablename__ = "caterers"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(200), nullable=False, index=True)
    owner_name = Column(String(200))
    email = Column(String(200), unique=True, nullable=False, index=True)
    mobile = Column(String(50))
    hashed_password = Column(String(255), nullable=False)

    # Location
    address = Column(String(300))
    city = Column(String(100), index=True)
    state = Column(String(100))
    zip = Column(String(20))

    # Business
    cuisine_type = Column(String(100))
    bio = Column(Text)
    price_per_guest = Column(Float, nullable=True)
    service_tags = Column(Text, default="")  # comma-separated

    # Public profile
    image_url = Column(String(500), nullable=True)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    verified = Column(Boolean, default=False)

    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    licenses = relationship("License", back_populates="caterer", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="caterer", cascade="all, delete-orphan")
    awards = relationship("Award", back_populates="caterer", cascade="all, delete-orphan")
    gallery_items = relationship("GalleryItem", back_populates="caterer", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="caterer", cascade="all, delete-orphan")


class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    caterer_id = Column(Integer, ForeignKey("caterers.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    document_url = Column(String(500), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)

    caterer = relationship("Caterer", back_populates="licenses")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    caterer_id = Column(Integer, ForeignKey("caterers.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    issued_by = Column(String(200), nullable=True)
    issue_date = Column(DateTime(timezone=True), nullable=True)
    certificate_url = Column(String(500), nullable=True)

    caterer = relationship("Caterer", back_populates="certifications")


class Award(Base):
    __tablename__ = "awards"

    id = Column(Integer, primary_key=True, index=True)
    caterer_id = Column(Integer, ForeignKey("caterers.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    year = Column(Integer, nullable=True)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)

    caterer = relationship("Caterer", back_populates="awards")


class GalleryItem(Base):
    __tablename__ = "gallery_items"

    id = Column(Integer, primary_key=True, index=True)
    caterer_id = Column(Integer, ForeignKey("caterers.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), default="photo")  # "photo" or "video"
    file_url = Column(String(500), nullable=False)

    caterer = relationship("Caterer", back_populates="gallery_items")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    caterer_id = Column(Integer, ForeignKey("caterers.id", ondelete="CASCADE"), nullable=False)
    customer_name = Column(String(200), nullable=False)
    rating = Column(Float, nullable=False, default=5.0)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    caterer = relationship("Caterer", back_populates="reviews")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models, security
from database import engine, SessionLocal
from routers import caterers, auth, licenses, certifications, awards, gallery, reviews

# Initialize Database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CaterHub API",
    description="Backend API for CaterHub Premium Catering Platform",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5178",
        "http://localhost:5179",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5178",
        "http://127.0.0.1:5179",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(caterers.router)
app.include_router(auth.router)
app.include_router(licenses.router)
app.include_router(certifications.router)
app.include_router(awards.router)
app.include_router(gallery.router)
app.include_router(reviews.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to CaterHub API! Go to /docs for Swagger documentation."}


# Database Seeding Function
def seed_data():
    db: Session = SessionLocal()
    try:
        count = db.query(models.Caterer).count()
        if count == 0:
            print("Seeding database with premium Indian mock caterers...")
            mock_caterers = [
                models.Caterer(
                    business_name="Royal Taj Catering",
                    owner_name="Aarav Sharma",
                    email="aarav@royaltaj.com",
                    mobile="+91 98765 43210",
                    hashed_password=security.hash_password("password123"),
                    address="45, Marine Drive",
                    city="Mumbai",
                    state="Maharashtra",
                    zip="400020",
                    cuisine_type="North Indian",
                    bio="Experience royal Mughlai and traditional North Indian culinary excellence. We bring the rich heritage of slow-cooked biryanis, tandoori masterpieces, and traditional desserts to weddings, corporate galas, and upscale events.",
                    price_per_guest=1200.0,
                    service_tags="Weddings,Royal,Biryani,Fine Dining,Cultural",
                    image_url="https://images.unsplash.com/photo-1555244162-803834f70033?w=800&q=85",
                    rating=4.9,
                    review_count=482,
                    verified=True
                ),
                models.Caterer(
                    business_name="Masala Bistro",
                    owner_name="Priya Patel",
                    email="priya@masalabistro.com",
                    mobile="+91 87654 32109",
                    hashed_password=security.hash_password("password123"),
                    address="12, Park Street",
                    city="Kolkata",
                    state="West Bengal",
                    zip="700016",
                    cuisine_type="Bengali & Fusion",
                    bio="Masala Bistro focuses on comforting, wholesome, and classic Indian favorites. From authentic Bengali delicacies to modern fusion street food, we prioritize robust flavors and warm hospitality for family gatherings, house parties, and corporate lunches.",
                    price_per_guest=450.0,
                    service_tags="Casual,Buffet,Street Food,Corporate,Family",
                    image_url="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=85",
                    rating=4.8,
                    review_count=311,
                    verified=True
                ),
                models.Caterer(
                    business_name="Saffron Table",
                    owner_name="Rohan Mehta",
                    email="rohan@saffrontable.in",
                    mobile="+91 76543 21098",
                    hashed_password=security.hash_password("password123"),
                    address="88, MG Road",
                    city="Bangalore",
                    state="Karnataka",
                    zip="560001",
                    cuisine_type="South Indian & Coastal",
                    bio="Saffron Table specializes in fragrant, spice-rich South Indian, coastal, and traditional vegetarian banquets. Our menus feature fresh ingredients, traditional filter coffee setups, and authentic recipes served with premium flair.",
                    price_per_guest=750.0,
                    service_tags="Cultural,Vegetarian,Traditional,Weddings,Organic",
                    image_url="https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=800&q=85",
                    rating=4.9,
                    review_count=624,
                    verified=True
                )
            ]
            db.bulk_save_objects(mock_caterers)
            db.commit()
            print("Successfully seeded premium mock caterers!")
        else:
            print(f"Database already has {count} caterers. Seeding skipped.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()



# Trigger seeding on startup (commented out to allow custom Swagger data)
# seed_data()

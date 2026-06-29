"""
Migration script: Clean up image_url values in the caterers table.

What it does:
  1. Extracts the first real URL from photo_folder:[...] values
  2. NULLs out expired Google Maps photo references (googleusercontent.com)
     which always return 404 and cannot be refreshed without the Places API
"""
import re
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./caterhub.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 30})
Session = sessionmaker(bind=engine)
db = Session()


def is_google_photo_url(url: str) -> bool:
    """Return True if this is an expired Google Maps / Places photo URL."""
    return any(x in url for x in [
        'lh5.googleusercontent.com',
        'lh3.googleusercontent.com',
        'lh4.googleusercontent.com',
        'googleusercontent.com/p/AF1Qip',
        'googleusercontent.com/p/AF1Qip',
    ])


def extract_first_url(image_url: str):
    """Extract the first https:// URL from a photo_folder:[...] string."""
    if not image_url:
        return None
    if not image_url.startswith("photo_folder:"):
        return image_url  # already a direct URL (handled separately below)
    match = re.search(r'https?://[^\s,\]\[\'\"]+', image_url)
    if match:
        url = match.group(0).rstrip("'\",][ ")
        # If the extracted URL itself is a Google photo, discard it
        if is_google_photo_url(url):
            return None
        return url
    return None


try:
    updated = 0
    nulled = 0

    # ── Step 1: Fix photo_folder:[...] values ──────────────────────────────
    rows = db.execute(
        text("SELECT id, image_url FROM caterers WHERE image_url LIKE 'photo_folder:%'")
    ).fetchall()
    print(f"Found {len(rows)} caterer(s) with photo_folder image URLs to migrate...")

    for row in rows:
        caterer_id, image_url = row
        clean_url = extract_first_url(image_url)
        if clean_url:
            db.execute(
                text("UPDATE caterers SET image_url = :url WHERE id = :id"),
                {"url": clean_url, "id": caterer_id}
            )
            print(f"  [FIXED]  ID {caterer_id}: {clean_url[:80]}")
            updated += 1
        else:
            # Couldn't extract a good URL — null it out
            db.execute(
                text("UPDATE caterers SET image_url = NULL WHERE id = :id"),
                {"id": caterer_id}
            )
            print(f"  [NULLED] ID {caterer_id}: no usable URL found in photo_folder string")
            nulled += 1

    # ── Step 2: NULL out direct Google photo URLs ──────────────────────────
    google_rows = db.execute(
        text("""
            SELECT id, image_url FROM caterers
            WHERE image_url IS NOT NULL
              AND image_url != ''
              AND (
                image_url LIKE '%googleusercontent.com%'
                OR image_url LIKE '%lh5.google%'
                OR image_url LIKE '%lh3.google%'
                OR image_url LIKE '%lh4.google%'
              )
        """)
    ).fetchall()
    print(f"\nFound {len(google_rows)} caterer(s) with expired Google photo URLs...")

    for row in google_rows:
        caterer_id, image_url = row
        db.execute(
            text("UPDATE caterers SET image_url = NULL WHERE id = :id"),
            {"id": caterer_id}
        )
        print(f"  [NULLED] ID {caterer_id}: {image_url[:80]}")
        nulled += 1

    db.commit()
    print(f"\nDone! Migration complete!")
    print(f"   Fixed (photo_folder -> real URL): {updated}")
    print(f"   Nulled (bad/expired URLs):        {nulled}")

except Exception as e:
    db.rollback()
    print(f"ERROR: {e}")
finally:
    db.close()

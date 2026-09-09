from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, WorkerProfile
import hashlib
import os
import uuid
import re

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return f"{salt}:{key}"

def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash or not password:
        return False
    if ":" not in stored_hash:
        return password == stored_hash
    try:
        salt, key = stored_hash.split(":", 1)
        check_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
        return check_key == key
    except Exception:
        return False

def validate_phone(phone: str) -> str:
    cleaned = re.sub(r"[^\d+]", "", phone.strip())
    if cleaned.startswith("+91"):
        cleaned = cleaned[3:]
    elif cleaned.startswith("91") and len(cleaned) == 12:
        cleaned = cleaned[2:]
    if not re.match(r"^[6-9]\d{9}$", cleaned):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Indian mobile phone number. Must be a valid 10-digit number."
        )
    return cleaned

# ================= CITIZEN CUSTOMER AUTH =================
@router.post("/customer/signup")
def customer_signup(payload: dict = Body(...), db: Session = Depends(get_db)):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")

    full_name = payload.get("full_name", "").strip()
    raw_phone = payload.get("phone", "").strip()
    password = payload.get("password", "").strip()
    email = payload.get("email", "").strip()
    address_text = payload.get("address_text", "Ghaziabad Sector").strip()
    locality = payload.get("locality", "Raj Nagar").strip()

    if not full_name or not raw_phone or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Full name, phone, and password are required")

    phone = validate_phone(raw_phone)

    try:
        existing_user = db.query(User).filter(User.phone == phone).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A citizen account with this mobile phone number already exists. Please log in."
            )

        new_user = User(
            id=uuid.uuid4(),
            phone=phone,
            full_name=full_name,
            role="customer",
            email=email or None,
            password_hash=hash_password(password),
            address_text=f"{address_text}, {locality}, Ghaziabad" if locality not in address_text else address_text,
            preferred_language=payload.get("preferred_language", "en")
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "status": "success",
            "message": "Citizen registration successful! Welcome to SahakarConnect.",
            "user": {
                "id": str(new_user.id),
                "full_name": new_user.full_name,
                "phone": new_user.phone,
                "email": new_user.email,
                "role": new_user.role,
                "address": new_user.address_text
            }
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error during registration: {str(e)}")

@router.post("/customer/login")
def customer_login(payload: dict = Body(...), db: Session = Depends(get_db)):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")

    raw_phone = payload.get("phone", "").strip()
    password = payload.get("password", "").strip()

    if not raw_phone or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number and password are required")

    phone = validate_phone(raw_phone)

    user = db.query(User).filter(User.phone == phone, User.role == "customer").first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Citizen account not found. Please register first.")

    if not verify_password(password, user.password_hash or ""):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password. Please try again.")

    return {
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": str(user.id),
            "full_name": user.full_name,
            "phone": user.phone,
            "email": user.email,
            "role": user.role,
            "address": user.address_text or "Ghaziabad, Uttar Pradesh"
        }
    }

# ================= ARTISAN WORKER AUTH =================
@router.post("/worker/login")
def worker_login(payload: dict = Body(...), db: Session = Depends(get_db)):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")

    raw_phone = payload.get("phone", "").strip()
    password = payload.get("password", "").strip()

    if not raw_phone or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number and password are required")

    phone = validate_phone(raw_phone)

    user = db.query(User).filter(User.phone == phone, User.role == "worker").first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Artisan account not found. Please register your profile first.")

    if not verify_password(password, user.password_hash or ""):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password. Please try again.")

    wp = db.query(WorkerProfile).filter(WorkerProfile.id == user.id).first()

    return {
        "status": "success",
        "message": "Artisan authentication successful",
        "worker": {
            "id": str(user.id),
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role,
            "society_name": wp.society_name if wp else "Ghaziabad Central Artisan Union",
            "specialization": wp.specialization if wp else "Trade Craftsman",
            "qualification": wp.qualification if wp else "Skill India Certified",
            "experience_years": wp.experience_years if wp else 5,
            "age": wp.age if wp else 34,
            "welfare_id": wp.welfare_id if wp else "COOP-WLF-GZB-01",
            "verification_status": wp.verification_status if wp else "verified",
            "rating_avg": float(wp.rating_avg or 4.9) if wp else 4.9
        }
    }

@router.get("/me")
def get_current_user_profile(phone: str = None, db: Session = Depends(get_db)):
    if phone:
        cleaned = re.sub(r"[^\d]", "", phone)
        user = db.query(User).filter(User.phone == cleaned).first()
        if user:
            return {
                "status": "success",
                "user": {
                    "id": str(user.id),
                    "full_name": user.full_name,
                    "phone": user.phone,
                    "email": user.email,
                    "role": user.role,
                    "address": user.address_text
                }
            }
    
    demo = db.query(User).filter(User.role == "customer").first()
    if demo:
        return {
            "status": "success",
            "user": {
                "id": str(demo.id),
                "full_name": demo.full_name,
                "phone": demo.phone,
                "email": demo.email,
                "role": demo.role,
                "address": demo.address_text
            }
        }

    return {"status": "error", "message": "No active user session"}

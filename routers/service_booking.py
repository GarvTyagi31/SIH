"""
Service Booking Module - Citizen-side service trade selection and artisan dispatch
Handles UI event processing and booking workflow management
Integrates with workers.py and bookings.py routers
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session
from database import get_db
from models import Booking, WorkerProfile, User, WageLedger
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/api/service", tags=["Service Booking"])

# ============= Constants =============

SERVICE_BASE_FARES = {
    "Electrician": 350.0,
    "Plumber": 400.0,
    "Carpenter": 450.0,
    "Appliance Repair": 499.0,
    "Construction Mistri": 750.0,
    "General Labour": 500.0,
    "Packers Movers": 2600.0,
    "Deep Cleaning": 350.0
}

DISTANCE_SURCHARGE_RATE = 15.0  # ₹/km beyond 10km
EMERGENCY_SURCHARGE = 150.0
MIN_DISTANCE_FOR_SURCHARGE = 10.0  # km

BOOKING_STATUS_FLOW = [
    "requested",
    "assigned",
    "en_route",
    "in_progress",
    "completed",
    "cancelled"
]

# ============= Utility Functions =============

def parse_uuid(id_str: str, param_name: str = "ID") -> uuid.UUID:
    """
    Safely parse UUID string, raise HTTPException on failure
    
    Args:
        id_str: UUID string to parse
        param_name: Parameter name for error message
        
    Returns:
        Parsed UUID object
        
    Raises:
        HTTPException: If UUID format is invalid
    """
    try:
        return uuid.UUID(str(id_str).strip())
    except (ValueError, AttributeError):
        logger.error(f"Invalid {param_name} format: {id_str}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {param_name} format. Must be a valid 36-character UUID."
        )


def calculate_base_fare(category: str) -> float:
    """
    Calculate base fare for service category
    
    Args:
        category: Service trade name (e.g., "Electrician", "Plumber")
        
    Returns:
        Base fare amount in rupees
    """
    return SERVICE_BASE_FARES.get(category, 350.0)


def calculate_distance_surcharge(distance_km: float) -> float:
    """
    Calculate distance surcharge for bookings >10km away
    Formula: (distance - 10) * ₹15/km
    
    Args:
        distance_km: Distance from citizen to worker in kilometers
        
    Returns:
        Distance surcharge amount in rupees
    """
    if distance_km <= MIN_DISTANCE_FOR_SURCHARGE:
        return 0.0
    
    surcharge = (distance_km - MIN_DISTANCE_FOR_SURCHARGE) * DISTANCE_SURCHARGE_RATE
    return round(surcharge, 2)


def calculate_total_fare(
    base_fare: float,
    tip_amount: float = 0.0,
    distance_km: float = 0.0,
    is_urgent: bool = False
) -> Dict[str, float]:
    """
    Calculate itemized total fare breakdown
    
    Args:
        base_fare: Base service fare
        tip_amount: Citizen tip for worker
        distance_km: Distance from citizen to worker
        is_urgent: Whether booking is emergency/SOS mode
        
    Returns:
        Dictionary with fare breakdown:
        {
            "base_fare": float,
            "distance_surcharge": float,
            "emergency_surcharge": float,
            "tip_amount": float,
            "total_fare": float
        }
    """
    distance_surcharge = calculate_distance_surcharge(distance_km)
    emergency_surcharge = EMERGENCY_SURCHARGE if is_urgent else 0.0
    tip_amount = max(0.0, float(tip_amount))
    
    total_fare = base_fare + distance_surcharge + emergency_surcharge + tip_amount
    
    return {
        "base_fare": round(base_fare, 2),
        "distance_surcharge": round(distance_surcharge, 2),
        "emergency_surcharge": round(emergency_surcharge, 2),
        "tip_amount": round(tip_amount, 2),
        "total_fare": round(total_fare, 2)
    }


# ============= API Endpoints =============

@router.get("/fare-estimate")
def estimate_service_fare(
    category: str = Query("Electrician", description="Service trade category"),
    distance_km: float = Query(2.5, ge=0.0, le=500.0, description="Distance in km"),
    tip_amount: float = Query(0.0, ge=0.0, le=10000.0, description="Tip amount"),
    is_urgent: bool = Query(False, description="Is emergency/SOS booking")
) -> Dict:
    """
    Calculate fare estimate for a service booking
    Used by frontend to show pricing before booking confirmation
    
    Args:
        category: Service trade (e.g., "Electrician", "Plumber")
        distance_km: Distance from citizen to worker
        tip_amount: Optional tip for worker
        is_urgent: Emergency/24x7 SOS mode flag
        
    Returns:
        Fare breakdown with total estimated cost
        
    Example Response:
        {
            "status": "success",
            "category": "Electrician",
            "distance_km": 15.0,
            "is_urgent": false,
            "base_fare": 350.0,
            "distance_surcharge": 75.0,
            "emergency_surcharge": 0.0,
            "tip_amount": 50.0,
            "total_fare": 475.0
        }
    """
    try:
        logger.info(f"📊 Calculating fare for {category} at {distance_km}km, urgent={is_urgent}")
        
        # Validate category
        if category not in SERVICE_BASE_FARES:
            logger.warning(f"⚠️ Unknown category: {category}")
            return {
                "status": "warning",
                "message": f"Category '{category}' not found, using default",
                "category": category,
                "distance_km": distance_km,
                "is_urgent": is_urgent,
                **calculate_total_fare(350.0, tip_amount, distance_km, is_urgent)
            }
        
        base_fare = calculate_base_fare(category)
        fare_breakdown = calculate_total_fare(base_fare, tip_amount, distance_km, is_urgent)
        
        return {
            "status": "success",
            "category": category,
            "distance_km": distance_km,
            "is_urgent": is_urgent,
            **fare_breakdown
        }
        
    except Exception as e:
        logger.error(f"❌ Fare estimation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fare calculation failed: {str(e)}"
        )


@router.post("/book-artisan")
def book_artisan_service(
    payload: dict = Body(...),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Create a service booking after citizen clicks "Book" button on worker card
    
    Workflow:
    1. Validate input payload
    2. Parse and verify worker UUID
    3. Calculate total fare with all surcharges
    4. Create Booking record in database
    5. Update worker status to "assigned"
    6. Trigger worker notification (if implemented)
    
    Args:
        payload: Booking request body containing:
            {
                "worker_id": "string (UUID)",
                "customer_id": "string (UUID, optional)",
                "category": "string (service trade)",
                "distance_km": float,
                "tip_amount": float,
                "is_urgent": boolean,
                "booking_type": "string (on_demand|scheduled|emergency_sos)",
                "scheduled_time": "ISO8601 datetime or null",
                "service_lat": float,
                "service_lng": float,
                "address_text": "string"
            }
        db: Database session
        
    Returns:
        Booking confirmation with:
            - booking_id (UUID)
            - booking_status (currently "assigned")
            - eta_minutes (estimated arrival time)
            - fare breakdown
            - warranty guarantee
            
    Raises:
        HTTPException: 400 if validation fails, 404 if worker not found, 500 if DB error
        
    Example Request:
        {
            "worker_id": "123e4567-e89b-12d3-a456-426614174000",
            "customer_id": "223e4567-e89b-12d3-a456-426614174000",
            "category": "Electrician",
            "distance_km": 12.5,
            "tip_amount": 50.0,
            "is_urgent": false,
            "booking_type": "on_demand",
            "service_lat": 28.6380,
            "service_lng": 77.3685,
            "address_text": "Flat 402, Shipra Sun City, Indirapuram"
        }
    """
    try:
        logger.info("🚀 Processing artisan booking...")
        
        # ===== Input Validation =====
        if not isinstance(payload, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payload must be a JSON object"
            )
        
        # Extract and validate required fields
        worker_id_str = payload.get("worker_id")
        if not worker_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="worker_id is required"
            )
        
        # Parse UUIDs safely
        worker_uuid = parse_uuid(worker_id_str, "worker_id")
        
        customer_id_str = payload.get("customer_id")
        if customer_id_str:
            customer_uuid = parse_uuid(customer_id_str, "customer_id")
        else:
            # Fallback to first registered customer
            customer = db.query(User).filter(User.role == "customer").first()
            customer_uuid = customer.id if customer else uuid.uuid4()
            logger.warning(f"⚠️ No customer_id provided, using fallback: {customer_uuid}")
        
        # ===== Worker Verification =====
        worker_user = db.query(User).filter(User.id == worker_uuid).first()
        if not worker_user:
            logger.error(f"❌ Worker not found: {worker_uuid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selected worker not found in system"
            )
        
        worker_profile = db.query(WorkerProfile).filter(WorkerProfile.id == worker_uuid).first()
        if not worker_profile:
            logger.error(f"❌ Worker profile not found: {worker_uuid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Worker profile information not available"
            )
        
        # ===== Fare Calculation =====
        category = payload.get("category", "Electrician")
        distance_km = max(0.0, float(payload.get("distance_km", 2.5)))
        tip_amount = max(0.0, float(payload.get("tip_amount", 0.0)))
        is_urgent = bool(payload.get("is_urgent", False))
        
        base_fare = calculate_base_fare(category)
        fare_breakdown = calculate_total_fare(base_fare, tip_amount, distance_km, is_urgent)
        
        logger.info(f"💰 Fare breakdown: {fare_breakdown}")
        
        # ===== Booking Creation =====
        booking = Booking(
            id=uuid.uuid4(),
            customer_id=customer_uuid,
            worker_id=worker_uuid,
            category=category,
            status="assigned",  # Directly assigned (citizen booking)
            booking_type=payload.get("booking_type", "emergency_sos" if is_urgent else "on_demand"),
            scheduled_time=payload.get("scheduled_time"),
            is_urgent=is_urgent,
            urgent_surcharge=fare_breakdown["emergency_surcharge"],
            distance_km=distance_km,
            distance_surcharge=fare_breakdown["distance_surcharge"],
            tip_amount=fare_breakdown["tip_amount"],
            fare_amount=fare_breakdown["total_fare"],
            service_lat=float(payload.get("service_lat", 28.6380)),
            service_lng=float(payload.get("service_lng", 77.3685)),
            address_text=payload.get("address_text", "Ghaziabad")
        )
        
        db.add(booking)
        db.commit()
        db.refresh(booking)
        
        logger.info(f"✅ Booking created: {booking.id}")
        
        # ===== Response Construction =====
        return {
            "status": "success",
            "message": f"Artisan {worker_user.full_name} has accepted your service booking!",
            "booking_id": str(booking.id),
            "booking_status": booking.status,
            "worker_name": worker_user.full_name,
            "worker_phone": worker_user.phone,
            "worker_society": worker_profile.society_name,
            "eta_minutes": "12-15 min" if not booking.scheduled_time else "Scheduled for slot",
            "fare_breakdown": {
                "base_fare": fare_breakdown["base_fare"],
                "distance_surcharge": fare_breakdown["distance_surcharge"],
                "emergency_surcharge": fare_breakdown["emergency_surcharge"],
                "tip_amount": fare_breakdown["tip_amount"],
                "total_fare": fare_breakdown["total_fare"]
            },
            "warranty_guarantee": "30-Day Cooperative Escrow Warranty Active"
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Booking creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Booking failed: {str(e)}"
        )


@router.get("/booking-status/{booking_id}")
def get_booking_status(
    booking_id: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Poll for current booking status (used for Service Status Tracker updates)
    
    Workflow:
    1. Fetch booking record by ID
    2. Retrieve worker and customer details
    3. Calculate ETA based on status
    4. Return timeline state
    
    Args:
        booking_id: UUID of booking to track
        db: Database session
        
    Returns:
        Current booking status with timeline state
        
    Raises:
        HTTPException: 404 if booking not found
    """
    try:
        b_uuid = parse_uuid(booking_id, "booking_id")
        booking = db.query(Booking).filter(Booking.id == b_uuid).first()
        
        if not booking:
            logger.warning(f"⚠️ Booking not found: {booking_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        worker = db.query(User).filter(User.id == booking.worker_id).first()
        worker_profile = db.query(WorkerProfile).filter(WorkerProfile.id == booking.worker_id).first()
        
        # Calculate ETA based on status
        eta_map = {
            "requested": "Waiting for confirmation",
            "assigned": "12-15 mins",
            "en_route": "5-8 mins",
            "in_progress": "Service in progress",
            "completed": "Completed",
            "cancelled": "Cancelled"
        }
        
        logger.info(f"📍 Status poll - Booking {booking_id}: {booking.status}")
        
        return {
            "status": "success",
            "booking_id": str(booking.id),
            "booking_status": booking.status,
            "timeline_state": booking.status,
            "eta": eta_map.get(booking.status, "Unknown"),
            "worker_name": worker.full_name if worker else "Artisan",
            "worker_society": worker_profile.society_name if worker_profile else "Guild",
            "fare_amount": float(booking.fare_amount),
            "created_at": booking.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Status fetch error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status fetch failed: {str(e)}"
        )


@router.patch("/booking-status/{booking_id}")
def update_booking_timeline(
    booking_id: str,
    payload: dict = Body(...),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Admin/system endpoint to manually update booking timeline state
    Transitions: requested → assigned → en_route → in_progress → completed
    
    Args:
        booking_id: UUID of booking
        payload: {"status": "string"} where status is one of BOOKING_STATUS_FLOW
        db: Database session
        
    Returns:
        Updated booking with new status
    """
    try:
        b_uuid = parse_uuid(booking_id, "booking_id")
        booking = db.query(Booking).filter(Booking.id == b_uuid).first()
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        new_status = payload.get("status")
        if new_status not in BOOKING_STATUS_FLOW:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(BOOKING_STATUS_FLOW)}"
            )
        
        logger.info(f"🔄 Updating booking {booking_id}: {booking.status} → {new_status}")
        
        booking.status = new_status
        db.commit()
        db.refresh(booking)
        
        return {
            "status": "success",
            "booking_id": str(booking.id),
            "previous_status": booking.status,
            "new_status": new_status,
            "message": f"Booking transitioned to '{new_status}'"
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Status update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status update failed: {str(e)}"
        )


@router.get("/service-categories")
def list_service_categories() -> Dict:
    """
    Return list of all available service trades
    Used for populating category selection UI
    
    Returns:
        List of categories with base fares
    """
    categories = [
        {
            "id": cat,
            "name": cat,
            "base_fare": fare,
            "emoji": get_category_emoji(cat)
        }
        for cat, fare in SERVICE_BASE_FARES.items()
    ]
    
    return {
        "status": "success",
        "count": len(categories),
        "categories": categories
    }


def get_category_emoji(category: str) -> str:
    """Map category to emoji for UI display"""
    emoji_map = {
        "Electrician": "⚡",
        "Plumber": "🔧",
        "Carpenter": "🪚",
        "Appliance Repair": "🔌",
        "Construction Mistri": "🏗️",
        "General Labour": "💪",
        "Packers Movers": "📦",
        "Deep Cleaning": "🧹"
    }
    return emoji_map.get(category, "🛠️")


@router.get("/booking-history/{customer_id}")
def get_customer_booking_history(
    customer_id: str,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Fetch booking history for a customer
    
    Args:
        customer_id: Customer UUID
        limit: Max number of bookings to return
        db: Database session
        
    Returns:
        List of recent bookings
    """
    try:
        c_uuid = parse_uuid(customer_id, "customer_id")
        
        bookings = db.query(Booking).filter(
            Booking.customer_id == c_uuid
        ).order_by(Booking.created_at.desc()).limit(limit).all()
        
        booking_list = []
        for b in bookings:
            worker = db.query(User).filter(User.id == b.worker_id).first()
            booking_list.append({
                "booking_id": str(b.id),
                "category": b.category,
                "status": b.status,
                "worker_name": worker.full_name if worker else "Unknown",
                "fare_amount": float(b.fare_amount),
                "created_at": b.created_at.isoformat()
            })
        
        return {
            "status": "success",
            "customer_id": str(c_uuid),
            "count": len(booking_list),
            "bookings": booking_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Booking history error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}"
        )

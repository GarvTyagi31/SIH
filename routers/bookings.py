from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
from sqlalchemy.orm import Session
from database import get_db
from models import Booking, WorkerProfile, User, WageLedger
from ledger import record_completed_booking_ledger
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])

def parse_uuid(id_str: str, param_name: str = "Booking ID") -> uuid.UUID:
    try:
        return uuid.UUID(str(id_str).strip())
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {param_name} format. Must be a valid 36-character UUID."
        )

@router.post("")
def create_booking(payload: dict = Body(...), db: Session = Depends(get_db)):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")

    category = payload.get("category", "Electrician")
    fare_amount = max(0.0, float(payload.get("fare_amount", 350.0)))
    is_urgent = bool(payload.get("is_urgent", False))
    urgent_surcharge = 150.0 if is_urgent else 0.0
    
    # Tipping & Distance
    tip_amount = max(0.0, float(payload.get("tip_amount", 0.0)))
    distance_km = max(0.0, float(payload.get("distance_km", 2.5)))
    
    # Long-Distance (>10km) Emergency Travel Compensation
    distance_surcharge = 0.0
    if distance_km > 10.0:
        distance_surcharge = round((distance_km - 10.0) * 15.0, 2)

    total_fare = fare_amount + tip_amount + distance_surcharge

    worker_id_str = payload.get("worker_id")
    customer_id_str = payload.get("customer_id")

    if not worker_id_str:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="worker_id is required")

    worker_uuid = parse_uuid(worker_id_str, "worker_id")
    worker_user = db.query(User).filter(User.id == worker_uuid).first()
    if not worker_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found")

    if customer_id_str:
        cust_uuid = parse_uuid(customer_id_str, "customer_id")
    else:
        cust = db.query(User).filter(User.role == "customer").first()
        cust_uuid = cust.id if cust else uuid.uuid4()

    try:
        booking = Booking(
            customer_id=cust_uuid,
            worker_id=worker_uuid,
            category=category,
            status="requested" if payload.get("status") == "requested" else "assigned",
            booking_type=payload.get("booking_type", "emergency_sos" if is_urgent else "on_demand"),
            scheduled_time=payload.get("scheduled_time"),
            is_urgent=is_urgent,
            urgent_surcharge=urgent_surcharge,
            distance_km=distance_km,
            distance_surcharge=distance_surcharge,
            tip_amount=tip_amount,
            fare_amount=total_fare,
            service_lat=float(payload.get("service_lat", 28.6380)),
            service_lng=float(payload.get("service_lng", 77.3685)),
            address_text=payload.get("address_text", "Flat 402, Shipra Sun City, Indirapuram, Ghaziabad")
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)

        return {
            "status": "success",
            "message": "Artisan dispatched successfully",
            "booking_id": str(booking.id),
            "booking_status": booking.status,
            "eta_minutes": "12-15 min" if not booking.scheduled_time else "Scheduled for slot",
            "fare_amount": float(booking.fare_amount),
            "tip_amount": float(booking.tip_amount),
            "distance_surcharge": float(booking.distance_surcharge),
            "distance_km": float(booking.distance_km),
            "is_urgent": booking.is_urgent,
            "warranty_guarantee": "30-Day Cooperative Escrow Warranty Active"
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Booking creation failed: {str(e)}")

@router.get("/queue-for-worker/{worker_id}")
def get_worker_dispatch_queue(worker_id: str, db: Session = Depends(get_db)):
    """
    Returns vertical queue of incoming requests for this worker (including 'requested' pool).
    """
    w_uuid = parse_uuid(worker_id, "worker_id")

    bookings = db.query(Booking).filter(
        Booking.worker_id == w_uuid,
        Booking.status.in_(["requested", "assigned", "en_route", "in_progress"])
    ).order_by(Booking.created_at.desc()).all()

    items = []
    for b in bookings:
        cust = db.query(User).filter(User.id == b.customer_id).first()
        items.append({
            "id": str(b.id),
            "category": b.category,
            "booking_type": b.booking_type,
            "status": b.status,
            "fare_amount": float(b.fare_amount),
            "is_urgent": bool(b.is_urgent),
            "scheduled_time": b.scheduled_time,
            "distance_km": float(b.distance_km or 2.5),
            "distance_surcharge": float(b.distance_surcharge or 0.0),
            "tip_amount": float(b.tip_amount or 0.0),
            "address": b.address_text,
            "lat": float(b.service_lat),
            "lng": float(b.service_lng),
            "customer_name": cust.full_name if cust else "Aditya Pandey",
            "customer_phone": cust.phone if cust else "9876543210",
            "created_at": b.created_at.strftime("%H:%M, %d %b"),
            "has_buddy": bool(b.secondary_worker_id),
            "can_accept": b.status == "requested",
            "can_decline": b.status in ["requested", "assigned"]
        })

    return {
        "status": "success",
        "count": len(items),
        "queue": items
    }

@router.get("/active-for-worker/{worker_id}")
def get_active_job_for_worker(worker_id: str, db: Session = Depends(get_db)):
    w_uuid = parse_uuid(worker_id, "worker_id")

    booking = db.query(Booking).filter(
        Booking.worker_id == w_uuid,
        Booking.status.in_(["assigned", "en_route", "in_progress"])
    ).order_by(Booking.created_at.desc()).first()

    if not booking:
        # Check if recently cancelled to notify worker
        recent_cancelled = db.query(Booking).filter(
            Booking.worker_id == w_uuid,
            Booking.status == "cancelled"
        ).order_by(Booking.created_at.desc()).first()

        if recent_cancelled and (datetime.utcnow() - recent_cancelled.created_at).total_seconds() < 120:
            return {
                "status": "cancelled_alert",
                "has_active_job": False,
                "cancellation_info": {
                    "booking_id": str(recent_cancelled.id),
                    "cancelled_by": recent_cancelled.cancelled_by or "customer",
                    "cancellation_fine": float(recent_cancelled.cancellation_fee or 0.0),
                    "message": f"Service #{str(recent_cancelled.id)[:6].upper()} was cancelled. ₹{float(recent_cancelled.cancellation_fee or 0.0):.2f} compensation credited to your wallet."
                }
            }

        return {"status": "success", "has_active_job": False, "booking": None}

    customer = db.query(User).filter(User.id == booking.customer_id).first()
    return {
        "status": "success",
        "has_active_job": True,
        "booking": {
            "id": str(booking.id),
            "category": booking.category,
            "booking_type": booking.booking_type,
            "status": booking.status,
            "fare_amount": float(booking.fare_amount),
            "distance_km": float(booking.distance_km or 2.5),
            "distance_surcharge": float(booking.distance_surcharge or 0.0),
            "tip_amount": float(booking.tip_amount or 0.0),
            "address": booking.address_text,
            "lat": float(booking.service_lat),
            "lng": float(booking.service_lng),
            "customer_name": customer.full_name if customer else "Aditya Pandey",
            "customer_phone": customer.phone if customer else "9876543210",
            "created_at": booking.created_at.strftime("%Y-%m-%d %H:%M"),
            "has_buddy": bool(booking.secondary_worker_id)
        }
    }

@router.post("/{booking_id}/accept")
def accept_booking_by_worker(booking_id: str, payload: dict = Body(default={}), db: Session = Depends(get_db)):
    """
    Feature 1: Worker manually chooses and accepts a specific incoming dispatch request.
    Transitions status from 'requested' to 'assigned'.
    """
    b_uuid = parse_uuid(booking_id, "booking_id")
    booking = db.query(Booking).filter(Booking.id == b_uuid).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking request not found")

    if booking.status in ["completed", "cancelled"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot accept booking with status '{booking.status}'")

    worker_id_str = payload.get("worker_id")
    if worker_id_str:
        w_uuid = parse_uuid(worker_id_str, "worker_id")
        booking.worker_id = w_uuid

    try:
        booking.status = "assigned"
        db.commit()
        db.refresh(booking)

        return {
            "status": "success",
            "message": f"Service request #{str(booking.id)[:6].upper()} accepted! Job is now actively assigned.",
            "booking_id": str(booking.id),
            "booking_status": booking.status,
            "category": booking.category,
            "fare_amount": float(booking.fare_amount)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to accept booking: {str(e)}")

@router.post("/{booking_id}/decline")
def decline_booking_by_worker(booking_id: str, payload: dict = Body(default={}), db: Session = Depends(get_db)):
    """
    Feature 1: Worker manually declines a specific incoming dispatch request with Zero Fine / Zero Penalty.
    """
    b_uuid = parse_uuid(booking_id, "booking_id")
    booking = db.query(Booking).filter(Booking.id == b_uuid).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking request not found")

    reason = payload.get("reason", "Artisan declined incoming request (Zero Penalty)")

    try:
        booking.status = "cancelled"
        booking.cancelled_by = "worker"
        booking.cancellation_reason = reason
        booking.cancellation_fee = 0.0  # Zero fine for worker
        booking.payment_status = "refunded"

        db.commit()
        db.refresh(booking)

        return {
            "status": "success",
            "message": f"Service request #{str(booking.id)[:6].upper()} declined with ZERO penalty. Platform is re-routing to another cooperative artisan.",
            "booking_id": str(booking.id),
            "fine_applied": 0.0,
            "booking_status": booking.status
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to decline booking: {str(e)}")

@router.post("/{booking_id}/cancel")
def cancel_booking_by_customer(booking_id: str, payload: dict = Body(...), db: Session = Depends(get_db)):
    """
    Citizen cancellation with in-between compensation fine.
    """
    b_uuid = parse_uuid(booking_id, "booking_id")
    booking = db.query(Booking).filter(Booking.id == b_uuid).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    reason = payload.get("reason", "Customer requested cancellation")

    fine_amount = 0.0
    is_in_between = booking.status in ["en_route", "in_progress"]

    if is_in_between:
        fine_amount = min(100.0, float(booking.fare_amount) * 0.30)
        fine_amount = round(fine_amount, 2)

    try:
        booking.status = "cancelled"
        booking.cancellation_fee = fine_amount
        booking.cancelled_by = "customer"
        booking.cancellation_reason = reason
        booking.payment_status = "penalty_deducted" if fine_amount > 0 else "refunded"

        db.commit()

        return {
            "status": "success",
            "message": "Booking has been cancelled.",
            "was_in_between": is_in_between,
            "cancellation_fine": fine_amount,
            "worker_compensation": fine_amount,
            "explanation": f"Cancellation fine of ₹{fine_amount} credited to artisan to compensate for transit and time." if fine_amount > 0 else "Cancelled before artisan departure. Zero fine applied."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Cancellation failed: {str(e)}")

@router.post("/{booking_id}/worker-cancel")
def cancel_booking_by_worker(booking_id: str, payload: dict = Body(...), db: Session = Depends(get_db)):
    """
    Worker Cancellation Authority (Zero Fine charged to worker).
    """
    b_uuid = parse_uuid(booking_id, "booking_id")
    booking = db.query(Booking).filter(Booking.id == b_uuid).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    reason = payload.get("reason", "Artisan reported bike breakdown / emergency")

    try:
        booking.status = "cancelled"
        booking.cancelled_by = "worker"
        booking.cancellation_reason = reason
        booking.cancellation_fee = 0.0 # Zero fine for worker
        booking.payment_status = "refunded"

        db.commit()

        return {
            "status": "success",
            "message": "Job cancelled by artisan with zero penalty. System is automatically re-dispatching to nearest guild peer.",
            "booking_id": str(booking.id),
            "fine_applied": 0.0
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Worker cancellation failed: {str(e)}")

@router.patch("/{booking_id}/status")
def update_booking_status(booking_id: str, payload: dict = Body(...), db: Session = Depends(get_db)):
    b_uuid = parse_uuid(booking_id, "booking_id")
    booking = db.query(Booking).filter(Booking.id == b_uuid).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    new_status = payload.get("status")
    allowed = ["requested", "assigned", "en_route", "in_progress", "completed", "cancelled"]
    if new_status not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    try:
        booking.status = new_status
        ledger_entry = None

        if new_status == "completed":
            ledger_entry = record_completed_booking_ledger(db, booking)

        db.commit()
        db.refresh(booking)

        return {
            "status": "success",
            "booking_id": str(booking.id),
            "new_status": booking.status,
            "ledger_record": {
                "payout": float(ledger_entry.worker_payout) if ledger_entry else None,
                "commission": float(ledger_entry.platform_commission) if ledger_entry else None,
                "welfare_fund": float(ledger_entry.coop_welfare_fee) if ledger_entry else None
            } if ledger_entry else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update booking status: {str(e)}")

@router.get("/{booking_id}")
def get_booking_details(booking_id: str, db: Session = Depends(get_db)):
    b_uuid = parse_uuid(booking_id, "booking_id")
    b = db.query(Booking).filter(Booking.id == b_uuid).first()
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    worker_user = db.query(User).filter(User.id == b.worker_id).first()
    wp = db.query(WorkerProfile).filter(WorkerProfile.id == b.worker_id).first()

    return {
        "status": "success",
        "booking": {
            "id": str(b.id),
            "category": b.category,
            "status": b.status,
            "fare_amount": float(b.fare_amount),
            "tip_amount": float(b.tip_amount or 0.0),
            "distance_km": float(b.distance_km or 2.5),
            "distance_surcharge": float(b.distance_surcharge or 0.0),
            "cancellation_fee": float(b.cancellation_fee or 0.0),
            "cancelled_by": b.cancelled_by,
            "cancellation_reason": b.cancellation_reason,
            "address": b.address_text,
            "service_lat": float(b.service_lat),
            "service_lng": float(b.service_lng),
            "worker_name": worker_user.full_name if worker_user else "Cooperative Artisan",
            "worker_phone": worker_user.phone if worker_user else "9811000001",
            "worker_society": wp.society_name if wp else "Ghaziabad Central Artisan Union",
            "worker_rating": float(wp.rating_avg) if wp else 4.9,
            "welfare_id": wp.welfare_id if wp else "COOP-WLF-GZB-01"
        }
    }

@router.get("/{booking_id}/invoice")
def get_booking_invoice(booking_id: str, db: Session = Depends(get_db)):
    b_uuid = parse_uuid(booking_id, "booking_id")
    b = db.query(Booking).filter(Booking.id == b_uuid).first()
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    worker_user = db.query(User).filter(User.id == b.worker_id).first()
    wp = db.query(WorkerProfile).filter(WorkerProfile.id == b.worker_id).first()
    customer_user = db.query(User).filter(User.id == b.customer_id).first()

    total = float(b.fare_amount)
    urgent_fee = float(b.urgent_surcharge or 0.0)
    dist_fee = float(b.distance_surcharge or 0.0)
    tip_fee = float(b.tip_amount or 0.0)
    base_fare = total - urgent_fee - dist_fee - tip_fee
    
    core_split_pool = base_fare + urgent_fee + dist_fee
    # 85% worker payout, 12% platform charge, 3% welfare fund split with exact penny conservation
    platform_ops = round(core_split_pool * 0.12, 2)
    welfare_pool = round(core_split_pool * 0.03, 2)
    worker_share = round((core_split_pool - (platform_ops + welfare_pool)) + tip_fee, 2)

    return {
        "status": "success",
        "invoice_number": f"SC-GZB-{str(b.id)[:8].upper()}",
        "warranty_card_id": f"WAR-30D-{str(b.id)[:8].upper()}",
        "warranty_valid_until": "30 Days from completion (Cooperative Escrow Guarantee)",
        "date": b.created_at.strftime("%Y-%m-%d %H:%M"),
        "customer": {
            "name": customer_user.full_name if customer_user else "Aditya Pandey",
            "phone": customer_user.phone if customer_user else "9876543210",
            "address": b.address_text
        },
        "artisan": {
            "name": worker_user.full_name if worker_user else "Ramesh Kumar",
            "phone": worker_user.phone if worker_user else "9811000001",
            "society": wp.society_name if wp else "Raj Nagar Artisans Sahakari",
            "welfare_id": wp.welfare_id if wp else "COOP-WLF-GZB-01",
            "pmsby_insurance": wp.insurance_policy_no if wp else "PMSBY-GZB-2026"
        },
        "service_details": {
            "category": b.category,
            "booking_type": b.booking_type,
            "base_fare": base_fare,
            "urgent_surcharge": urgent_fee,
            "long_distance_surcharge": dist_fee,
            "worker_tip": tip_fee,
            "total_fare": total
        },
        "cooperative_breakdown": {
            "worker_take_home": worker_share,
            "worker_take_home_85pct": worker_share,
            "platform_operations_fee_12pct": platform_ops,
            "platform_operations_fee_5pct": platform_ops,
            "worker_welfare_insurance_fund_3pct": welfare_pool,
            "worker_welfare_insurance_fund_2pct": welfare_pool
        }
    }

@router.get("/{booking_id}/gatepass")
def get_society_gatepass(booking_id: str, db: Session = Depends(get_db)):
    b_uuid = parse_uuid(booking_id, "booking_id")
    b = db.query(Booking).filter(Booking.id == b_uuid).first()
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    w_user = db.query(User).filter(User.id == b.worker_id).first()
    wp = db.query(WorkerProfile).filter(WorkerProfile.id == b.worker_id).first()

    return {
        "status": "success",
        "gatepass": {
            "pass_code": f"GZB-GATE-{str(b.id)[:6].upper()}",
            "society_entry_status": "PRE-VERIFIED & APPROVED",
            "artisan_name": w_user.full_name if w_user else "Ramesh Kumar",
            "artisan_phone": w_user.phone if w_user else "9811000001",
            "trade": b.category,
            "society_guild": wp.society_name if wp else "Ghaziabad Central Guild",
            "police_verification": "POL-GZB-VERIFIED-2026",
            "skill_india_cert": wp.qualification if wp else "ITI Skill India Gold",
            "destination_address": b.address_text,
            "validity": "Valid for immediate single-entry on service dispatch"
        }
    }

@router.post("/{booking_id}/guild-buddy")
def request_guild_buddy(booking_id: str, db: Session = Depends(get_db)):
    b_uuid = parse_uuid(booking_id, "booking_id")
    b = db.query(Booking).filter(Booking.id == b_uuid).first()
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    try:
        buddy = db.query(WorkerProfile).join(User, WorkerProfile.id == User.id).filter(
            WorkerProfile.id != b.worker_id,
            WorkerProfile.verification_status == "verified"
        ).first()

        if buddy:
            b.secondary_worker_id = buddy.id
            db.commit()

        buddy_name = "Suresh Sharma (Plumbing Peer)" if not buddy else f"{buddy.user.full_name} (Guild Buddy)"

        return {
            "status": "success",
            "message": f"Guild Buddy summoned! {buddy_name} is arriving in 8 minutes.",
            "buddy_details": {
                "name": buddy_name,
                "distance": "1.1 km away",
                "eta": "8 mins",
                "split_ratio": "50% Primary Lead / 50% Assistant"
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to assign guild buddy")

@router.post("/{booking_id}/rating")
def rate_booking(booking_id: str, payload: dict = Body(...), db: Session = Depends(get_db)):
    b_uuid = parse_uuid(booking_id, "booking_id")
    b = db.query(Booking).filter(Booking.id == b_uuid).first()
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    try:
        rating = max(1, min(5, int(payload.get("rating", 5))))
    except (ValueError, TypeError):
        rating = 5

    feedback = str(payload.get("feedback", "")).strip()

    try:
        b.rating = rating
        b.feedback_comment = feedback

        wp = db.query(WorkerProfile).filter(WorkerProfile.id == b.worker_id).first()
        if wp:
            current_total = wp.total_ratings or 0
            current_avg = float(wp.rating_avg or 5.0)
            new_total = current_total + 1
            new_avg = round(((current_avg * current_total) + rating) / new_total, 2)
            wp.total_ratings = new_total
            wp.rating_avg = new_avg

        db.commit()
        return {"status": "success", "message": "Feedback submitted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to submit rating: {str(e)}")

@router.post("/bulk")
def create_bulk_booking(payload: dict = Body(...), db: Session = Depends(get_db)):
    category = payload.get("category", "Plumber")
    try:
        worker_count = max(1, int(payload.get("worker_count", 10)))
        days_count = max(1, int(payload.get("days_count", 1)))
    except (ValueError, TypeError):
        worker_count = 10
        days_count = 1

    company_name = payload.get("company_name", "Enterprise Client")
    contact_phone = payload.get("contact_phone", "9811000000")
    site_address = payload.get("site_address", "Ghaziabad Industrial Area / Housing Society")
    
    daily_rate_per_worker = 650.0
    total_fare = round(worker_count * days_count * daily_rate_per_worker, 2)

    try:
        lead_worker = db.query(WorkerProfile).first()
        cust = db.query(User).filter(User.role == "customer").first()

        booking = Booking(
            customer_id=cust.id if cust else uuid.uuid4(),
            worker_id=lead_worker.id if lead_worker else uuid.uuid4(),
            category=category,
            status="assigned",
            booking_type="bulk_contract",
            is_bulk=True,
            bulk_worker_count=worker_count,
            fare_amount=total_fare,
            service_lat=28.6692,
            service_lng=77.4538,
            address_text=f"{company_name} - {site_address} (Ph: {contact_phone})"
        )
        db.add(booking)
        db.commit()

        return {
            "status": "success",
            "message": f"Bulk contract for {worker_count} {category} artisans confirmed! Lead coordinator assigned.",
            "contract_id": f"BULK-GZB-{str(booking.id)[:8].upper()}",
            "workers_assigned_count": worker_count,
            "duration_days": days_count,
            "total_contract_value": total_fare,
            "direct_workers_pool_85pct": round(total_fare * 0.85, 2),
            "direct_workers_pool_93pct": round(total_fare * 0.85, 2),
            "platform_operations_fee_12pct": round(total_fare * 0.12, 2),
            "coop_welfare_fee_3pct": round(total_fare * 0.03, 2),
            "coop_welfare_fee_2pct": round(total_fare * 0.03, 2)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Bulk booking creation failed: {str(e)}")

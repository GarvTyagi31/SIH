from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, WorkerProfile, Booking, WageLedger, Complaint
from forecast import generate_7day_demand_forecast
from ledger import verify_ledger_integrity
import uuid

router = APIRouter(prefix="/api/admin", tags=["Admin"])

def parse_uuid(id_str: str, param_name: str = "ID") -> uuid.UUID:
    try:
        return uuid.UUID(str(id_str).strip())
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {param_name} format. Must be a valid 36-character UUID."
        )

@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    try:
        active_workers = db.query(WorkerProfile).filter(
            WorkerProfile.verification_status == "verified",
            WorkerProfile.is_available == True
        ).count()
        total_verified = db.query(WorkerProfile).filter(
            WorkerProfile.verification_status == "verified"
        ).count()
        pending_verifications = db.query(WorkerProfile).filter(
            WorkerProfile.verification_status == "pending"
        ).count()
        total_dispatched = db.query(Booking).count()
        completed_bookings = db.query(Booking).filter(Booking.status == "completed").count()
        emergency_bookings = db.query(Booking).filter(Booking.is_urgent == True).count()
        
        welfare_pool = db.query(WageLedger).all()
        total_welfare = sum([float(entry.coop_welfare_fee) for entry in welfare_pool])
        total_commission = sum([float(entry.platform_commission) for entry in welfare_pool])
        total_worker_payout = sum([float(entry.worker_payout) for entry in welfare_pool])
        is_ledger_valid = verify_ledger_integrity(db)

        return {
            "active_verified_workers": active_workers,
            "total_verified_workers": total_verified,
            "pending_verifications": pending_verifications,
            "total_dispatches": total_dispatched,
            "completed_bookings": completed_bookings,
            "emergency_sos_bookings": emergency_bookings,
            "welfare_balance_inr": round(total_welfare, 2),
            "commission_earned_inr": round(total_commission, 2),
            "total_worker_payout_inr": round(total_worker_payout, 2),
            "ledger_integrity_passed": is_ledger_valid,
            "average_worker_wage_share": "85.0%"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Metrics computation error: {str(e)}")

@router.get("/verification-queue")
def get_verification_queue(db: Session = Depends(get_db)):
    pending = db.query(WorkerProfile, User).join(User, WorkerProfile.id == User.id).filter(
        WorkerProfile.verification_status == "pending"
    ).all()

    queue = []
    for wp, u in pending:
        queue.append({
            "worker_id": str(u.id),
            "full_name": u.full_name,
            "phone": u.phone,
            "society_name": wp.society_name,
            "categories": wp.service_categories,
            "specialization": wp.specialization or "Trade Specialist",
            "qualification": wp.qualification or "ITI Skill India Certified",
            "experience_years": wp.experience_years,
            "id_doc_url": wp.id_doc_url or "https://via.placeholder.com/400x250.png?text=Skill+India+Certificate",
            "registered_on": wp.created_at.strftime("%Y-%m-%d")
        })
    return {"queue": queue}

@router.post("/verify-worker/{worker_id}")
def verify_worker(worker_id: str, payload: dict = Body(...), db: Session = Depends(get_db)):
    action = payload.get("action")
    if action not in ["approve", "reject"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Action must be 'approve' or 'reject'")

    w_uuid = parse_uuid(worker_id, "worker_id")
    worker = db.query(WorkerProfile).filter(WorkerProfile.id == w_uuid).first()
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker profile not found")

    try:
        worker.verification_status = "verified" if action == "approve" else "rejected"
        db.commit()
        return {"status": "success", "worker_id": str(worker.id), "new_status": worker.verification_status}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Worker verification update failed: {str(e)}")

@router.get("/live-map-data")
def get_live_map_data(db: Session = Depends(get_db)):
    workers = db.query(WorkerProfile, User).join(User, WorkerProfile.id == User.id).filter(
        WorkerProfile.verification_status == "verified"
    ).all()

    worker_pins = []
    for wp, u in workers:
        worker_pins.append({
            "id": str(u.id),
            "name": u.full_name,
            "phone": u.phone,
            "society": wp.society_name,
            "categories": wp.service_categories,
            "specialization": wp.specialization or "General Specialist",
            "rating": float(wp.rating_avg),
            "lat": wp.latitude,
            "lng": wp.longitude,
            "is_available": wp.is_available
        })

    active_bookings = db.query(Booking).filter(
        Booking.status.in_(["requested", "assigned", "en_route", "in_progress"])
    ).all()

    booking_pins = []
    for b in active_bookings:
        booking_pins.append({
            "id": str(b.id),
            "category": b.category,
            "status": b.status,
            "is_urgent": b.is_urgent,
            "lat": b.service_lat,
            "lng": b.service_lng,
            "fare": float(b.fare_amount),
            "address": b.address_text or "Ghaziabad Hub"
        })

    return {"workers": worker_pins, "active_bookings": booking_pins}

@router.get("/forecast/demand")
def get_demand_forecast():
    return generate_7day_demand_forecast()

@router.get("/audit-ledger")
def get_audit_ledger(db: Session = Depends(get_db)):
    entries = db.query(WageLedger).order_by(WageLedger.timestamp.desc()).limit(40).all()
    results = []
    for e in entries:
        results.append({
            "booking_id": str(e.booking_id),
            "worker_payout": float(e.worker_payout),
            "platform_commission": float(e.platform_commission),
            "coop_welfare_fee": float(e.coop_welfare_fee),
            "prev_hash": e.prev_hash,
            "current_hash": e.current_hash,
            "timestamp": e.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    return {"ledger_entries": results, "is_verified": verify_ledger_integrity(db)}

@router.get("/workers")
def get_all_workers(db: Session = Depends(get_db)):
    workers = db.query(WorkerProfile, User).join(User, WorkerProfile.id == User.id).all()
    results = []
    for wp, u in workers:
        results.append({
            "worker_id": str(u.id),
            "full_name": u.full_name,
            "phone": u.phone,
            "society_name": wp.society_name,
            "categories": wp.service_categories,
            "specialization": wp.specialization,
            "qualification": wp.qualification,
            "experience_years": wp.experience_years,
            "rating_avg": float(wp.rating_avg),
            "total_ratings": wp.total_ratings,
            "verification_status": wp.verification_status,
            "is_available": wp.is_available,
            "welfare_id": wp.welfare_id,
            "insurance_policy_no": wp.insurance_policy_no
        })
    return {"workers": results}

@router.get("/complaints")
def get_complaints(db: Session = Depends(get_db)):
    complaints = db.query(Complaint).order_by(Complaint.created_at.desc()).all()
    results = []
    for c in complaints:
        customer = db.query(User).filter(User.id == c.customer_id).first()
        worker = db.query(User).filter(User.id == c.worker_id).first() if c.worker_id else None
        results.append({
            "id": str(c.id),
            "booking_id": str(c.booking_id) if c.booking_id else None,
            "subject": c.subject,
            "description": c.description,
            "status": c.status,
            "admin_notes": c.admin_notes,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M"),
            "customer_name": customer.full_name if customer else "Resident",
            "worker_name": worker.full_name if worker else "N/A"
        })
    return {"complaints": results}

@router.patch("/complaints/{complaint_id}/resolve")
def resolve_complaint(complaint_id: str, payload: dict = Body(...), db: Session = Depends(get_db)):
    c_uuid = parse_uuid(complaint_id, "complaint_id")
    complaint = db.query(Complaint).filter(Complaint.id == c_uuid).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    
    try:
        complaint.status = payload.get("status", "resolved")
        complaint.admin_notes = payload.get("admin_notes", "Resolved by Federation Grievance Cell")
        db.commit()
        return {"status": "success", "message": "Complaint updated", "complaint_id": str(complaint.id)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to resolve complaint: {str(e)}")

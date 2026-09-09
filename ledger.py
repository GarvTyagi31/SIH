import hashlib
from sqlalchemy.orm import Session
from models import WageLedger, Booking

GENESIS_HASH = "0" * 64

def calculate_hash(booking_id: str, worker_payout: float, platform_commission: float, coop_welfare_fee: float, prev_hash: str) -> str:
    payload = f"{booking_id}-{worker_payout:.2f}-{platform_commission:.2f}-{coop_welfare_fee:.2f}-{prev_hash}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def record_completed_booking_ledger(db: Session, booking: Booking) -> WageLedger:
    existing = db.query(WageLedger).filter(WageLedger.booking_id == booking.id).first()
    if existing:
        return existing

    fare = float(booking.fare_amount)
    # New cooperative wage split ratio: 85% worker payout, 12% platform operations, 3% worker welfare fund
    commission = round(fare * 0.12, 2)
    welfare = round(fare * 0.03, 2)
    payout = round(fare - (commission + welfare), 2)

    last_entry = db.query(WageLedger).order_by(WageLedger.timestamp.desc()).first()
    prev_hash = last_entry.current_hash if last_entry else GENESIS_HASH

    curr_hash = calculate_hash(str(booking.id), payout, commission, welfare, prev_hash)

    ledger_entry = WageLedger(
        booking_id=booking.id,
        worker_payout=payout,
        platform_commission=commission,
        coop_welfare_fee=welfare,
        prev_hash=prev_hash,
        current_hash=curr_hash
    )
    db.add(ledger_entry)
    db.commit()
    db.refresh(ledger_entry)
    return ledger_entry

def verify_ledger_integrity(db: Session) -> bool:
    entries = db.query(WageLedger).order_by(WageLedger.timestamp.asc()).all()
    expected_prev = GENESIS_HASH
    for entry in entries:
        if entry.prev_hash != expected_prev:
            return False
        expected_curr = calculate_hash(
            str(entry.booking_id),
            float(entry.worker_payout),
            float(entry.platform_commission),
            float(entry.coop_welfare_fee),
            entry.prev_hash
        )
        if entry.current_hash != expected_curr:
            return False
        expected_prev = entry.current_hash
    return True

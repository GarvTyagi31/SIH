import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Numeric, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    role = Column(String(30), nullable=False)  # 'customer', 'worker', 'federation_admin'
    password_hash = Column(String(255), nullable=True)
    email = Column(String(150), nullable=True)
    preferred_language = Column(String(10), default="en")
    address_text = Column(String(255), nullable=True)
    address_lat = Column(Float, nullable=True)
    address_lng = Column(Float, nullable=True)
    
    # Subscription status
    subscription_plan = Column(String(50), default="free")  # 'free', 'sahakar_gold_citizen', 'sahakar_pro_artisan'
    subscription_expires_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkerProfile(Base):
    __tablename__ = "worker_profiles"

    id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    society_name = Column(String(150), nullable=False)
    service_categories = Column(Text, nullable=False)  # e.g. "Electrician,Plumber,Construction Mistri,Packers Movers"
    specialization = Column(String(150), nullable=True)
    qualification = Column(String(150), nullable=True)
    experience_years = Column(Integer, default=0)
    age = Column(Integer, default=32)
    verification_status = Column(String(20), default="pending")  # 'pending', 'verified', 'rejected'
    id_doc_url = Column(String(255), nullable=True)
    photo_url = Column(String(255), nullable=True)
    rating_avg = Column(Float, default=5.0)
    total_ratings = Column(Integer, default=1)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    welfare_id = Column(String(50), nullable=True)
    insurance_policy_no = Column(String(50), nullable=True)
    
    # Upgraded skills & certification history (JSON / comma-separated)
    passed_certifications = Column(Text, default="Skill India Certified Artisan")
    is_pro_subscriber = Column(Boolean, default=False)
    priority_ranking_boost = Column(Float, default=1.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    secondary_worker_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # Guild Buddy 2-person jobs
    category = Column(String(50), nullable=False)
    status = Column(String(30), default="requested")  # 'requested', 'assigned', 'en_route', 'in_progress', 'completed', 'cancelled'
    booking_type = Column(String(30), default="on_demand")  # 'on_demand', 'scheduled', 'emergency_sos', 'bulk_contract', 'relocation'
    scheduled_time = Column(String(100), nullable=True)
    is_urgent = Column(Boolean, default=False)
    urgent_surcharge = Column(Numeric(10, 2), default=0)
    
    # Distance & Long distance emergency surcharge (>10km)
    distance_km = Column(Float, default=0.0)
    distance_surcharge = Column(Numeric(10, 2), default=0)
    
    # Tipping system
    tip_amount = Column(Numeric(10, 2), default=0)
    
    # Cancellation & Penalties
    cancellation_fee = Column(Numeric(10, 2), default=0)
    cancelled_by = Column(String(20), nullable=True)  # 'customer', 'worker', 'admin'
    cancellation_reason = Column(String(255), nullable=True)

    # Bulk & Movers specs
    is_bulk = Column(Boolean, default=False)
    bulk_worker_count = Column(Integer, default=1)
    movers_count = Column(Integer, default=1)
    truck_type = Column(String(100), nullable=True)
    
    fare_amount = Column(Numeric(10, 2), nullable=False)
    service_lat = Column(Float, nullable=False)
    service_lng = Column(Float, nullable=False)
    address_text = Column(String(255), nullable=True)
    payment_status = Column(String(30), default="paid")
    payment_method = Column(String(50), default="razorpay_upi")
    payment_transaction_id = Column(String(100), nullable=True)
    rating = Column(Integer, nullable=True)
    feedback_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class WageLedger(Base):
    __tablename__ = "wage_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), unique=True, nullable=False)
    worker_payout = Column(Numeric(10, 2), nullable=False)
    platform_commission = Column(Numeric(10, 2), nullable=False)  # 5%
    coop_welfare_fee = Column(Numeric(10, 2), nullable=False)     # 2%
    prev_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    subject = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    attachment_urls = Column(Text, nullable=True)
    status = Column(String(20), default="open")
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

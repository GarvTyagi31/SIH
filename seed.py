import uuid
import models
from database import SessionLocal, init_db
from models import User, WorkerProfile, Booking, Complaint
from ledger import record_completed_booking_ledger
from routers.auth import hash_password

GHAZIABAD_LOCALITIES = [
    {"name": "Raj Nagar Sector 10", "lat": 28.6852, "lng": 77.4421, "society": "Raj Nagar Artisans Sahakari Samiti"},
    {"name": "Shipra Sun City, Indirapuram", "lat": 28.6380, "lng": 77.3685, "society": "Trans-Hindon Shramik Cooperative"},
    {"name": "Sector 4, Vaishali", "lat": 28.6483, "lng": 77.3392, "society": "Vaishali Skill Workers Federation"},
    {"name": "Sector 14, Vasundhara", "lat": 28.6612, "lng": 77.3670, "society": "Vasundhara Cooperative Guild"},
    {"name": "Kavi Nagar Block C", "lat": 28.6710, "lng": 77.4520, "society": "Ghaziabad Central Artisan Union"},
    {"name": "Crossings Republik", "lat": 28.6315, "lng": 77.4320, "society": "Crossings Technical Workers Sahakari"},
    {"name": "Raj Nagar Extension", "lat": 28.7012, "lng": 77.4250, "society": "North Ghaziabad Shramik Federation"},
    {"name": "Kaushambi Sector 1", "lat": 28.6430, "lng": 77.3230, "society": "Kaushambi Household Services Guild"}
]

DEMO_WORKER_PHONE = "9811000001"
DEMO_CUSTOMER_PHONE = "9876543210"

def seed_demo_data():
    print("Recreating database tables with updated schema...")
    init_db(drop_first=True)
    db = SessionLocal()

    print("Seeding Ghaziabad Cooperative Users, Workers, and Ledger entries...")

    # 1. Federation Admin
    admin_user = User(
        id=uuid.uuid4(),
        phone="9999000001",
        full_name="Ghaziabad Cooperative Federation Admin",
        role="federation_admin",
        password_hash=hash_password("admin123"),
        email="admin@sahakarghaziabad.in",
        preferred_language="en"
    )
    db.add(admin_user)

    # 2. Customer
    customer_user = User(
        id=uuid.uuid4(),
        phone=DEMO_CUSTOMER_PHONE,
        full_name="Aditya Pandey",
        role="customer",
        password_hash=hash_password("customer123"),
        email="aditya@example.com",
        address_text="Flat 402, Shipra Sun City, Indirapuram, Ghaziabad",
        address_lat=28.6380,
        address_lng=77.3685,
        preferred_language="en"
    )
    db.add(customer_user)
    db.commit()

    # 3. Verified & Pending Workers across Ghaziabad
    workers_seed = [
        # (name, phone, cats, spec, qual, exp, age, rating, loc_idx, status, fixed_id, wlf_id, ins_no)
        ("Ramesh Kumar", "9811000001", "Electrician,Appliance Repair", "Residential Wiring, Inverter & MCB Repair", "ITI Electrician (NCVT), Skill India Gold", 8, 34, 4.92, 0, "verified", "11111111-1111-1111-1111-111111111111", "COOP-WLF-GZB-01", "PMSBY-GZB-2026-01"),
        ("Suresh Sharma", "9811000002", "Plumber", "Pipe Leakage, Sanitary Fittings & Water Tank Maintenance", "ITI Plumbing, 2 yr Apprenticeship", 6, 31, 4.85, 1, "verified", None, "COOP-WLF-GZB-02", "PMSBY-GZB-2026-02"),
        ("Mohan Lal", "9811000003", "Carpenter", "Modular Kitchen, Door Locks & Custom Wood Restoration", "Diploma in Carpentry & Woodcraft", 10, 42, 4.78, 2, "verified", None, "COOP-WLF-GZB-03", "PMSBY-GZB-2026-03"),
        ("Dinesh Verma", "9811000004", "Electrician", "Industrial & Residential Wiring, AC Circuitry", "B.Voc Electrical Technology, Skill India", 12, 38, 5.0, 3, "verified", None, "COOP-WLF-GZB-04", "PMSBY-GZB-2026-04"),
        ("Kailash Mistri", "9811000010", "Construction Mistri,Home Renovation", "Master Masonry, Wall Plaster, Tiling & Structural Renovation", "Certified Master Craftsman (Raj Mistry)", 14, 45, 4.95, 0, "verified", None, "COOP-WLF-GZB-10", "PMSBY-GZB-2026-10"),
        ("Raju Beldar", "9811000011", "General Labour,Home Renovation", "Construction Assistance, Material Shifting, Concrete Mixing", "Skilled Shramik Guild Card", 5, 27, 4.70, 1, "verified", None, "COOP-WLF-GZB-11", "PMSBY-GZB-2026-11"),
        ("Mukesh Yadav", "9811000012", "Packers Movers", "Home Relocation, Furniture Packing, Heavy Appliance Shifting", "Professional Transport Guild Certified", 9, 36, 4.88, 2, "verified", None, "COOP-WLF-GZB-12", "PMSBY-GZB-2026-12"),
        ("Vipin Chauhan", "9811000005", "Plumber,Appliance Repair", "AC/RO Repair & Modern Sanitary Fitting", "ITI Refrigeration & Plumbing", 5, 29, 4.68, 4, "verified", None, "COOP-WLF-GZB-05", "PMSBY-GZB-2026-05"),
        ("Manoj Saini", "9811000007", "Appliance Repair", "Split AC Gas Charging, Refrigerator & Washing Machine", "Advanced Skill India HVAC Certified", 7, 33, 4.88, 5, "verified", None, "COOP-WLF-GZB-06", "PMSBY-GZB-2026-06"),
        ("Sunil Prajapati", "9811000008", "Carpenter", "Furniture Assembly, Door Fitting & Locksmith Services", "Certified Wood Artisan Guild", 9, 39, 4.75, 6, "verified", None, "COOP-WLF-GZB-07", "PMSBY-GZB-2026-07"),
        ("Anil Yadav", "9811000006", "Electrician", "Home Wiring & Switchboards", "ITI Electrician (Verification Pending)", 3, 26, 4.5, 7, "pending", None, "COOP-WLF-GZB-08", "PMSBY-GZB-2026-08"),
        ("Deepak Tiwari", "9811000009", "Plumber", "Commercial Drainage & Solar Water Heater Fitting", "ITI Mechanical Fitting", 4, 28, 4.6, 0, "pending", None, "COOP-WLF-GZB-09", "PMSBY-GZB-2026-09"),
    ]

    worker_entities = []
    for name, phone, cats, spec, qual, exp, age, rating, loc_idx, status, fixed_id, wlf, ins in workers_seed:
        uid = uuid.UUID(fixed_id) if fixed_id else uuid.uuid4()
        user = User(id=uid, phone=phone, full_name=name, role="worker", password_hash=hash_password("worker123"), preferred_language="hi")
        db.add(user)
        db.flush()

        loc = GHAZIABAD_LOCALITIES[loc_idx]

        wp = WorkerProfile(
            id=user.id,
            society_name=loc["society"],
            service_categories=cats,
            specialization=spec,
            qualification=qual,
            experience_years=exp,
            age=age,
            verification_status=status,
            photo_url=None,
            rating_avg=rating,
            total_ratings=18 if status == "verified" else 0,
            latitude=loc["lat"],
            longitude=loc["lng"],
            is_available=True,
            welfare_id=wlf,
            insurance_policy_no=ins
        )
        db.add(wp)
        worker_entities.append(wp)

    db.commit()

    # 4. Completed Bookings + Chained Wage Ledger (85/12/3 ratio)
    active_worker = worker_entities[0]
    demo_booking = Booking(
        id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        customer_id=customer_user.id,
        worker_id=active_worker.id,
        category="Electrician",
        status="completed",
        booking_type="on_demand",
        is_urgent=False,
        urgent_surcharge=0,
        fare_amount=350.00,
        service_lat=28.6380,
        service_lng=77.3685,
        address_text="Flat 402, Shipra Sun City, Indirapuram, Ghaziabad",
        rating=5,
        feedback_comment="Arrived in 15 mins, fixed the short circuit cleanly with genuine Havells MCB switch. Very polite!"
    )
    db.add(demo_booking)
    db.commit()
    record_completed_booking_ledger(db, demo_booking)

    plumber_worker = worker_entities[1]
    demo_booking2 = Booking(
        id=uuid.uuid4(),
        customer_id=customer_user.id,
        worker_id=plumber_worker.id,
        category="Plumber",
        status="completed",
        booking_type="scheduled",
        scheduled_time="Yesterday 2:00 PM",
        is_urgent=False,
        urgent_surcharge=0,
        fare_amount=400.00,
        service_lat=28.6483,
        service_lng=77.3392,
        address_text="Sector 4, Vaishali, Ghaziabad",
        rating=5,
        feedback_comment="Clean work with proper genuine parts invoice and 30-day warranty card."
    )
    db.add(demo_booking2)
    db.commit()
    record_completed_booking_ledger(db, demo_booking2)

    # 5. Seed 3 Incoming Demo Requests (status: 'requested') for Worker Ramesh Kumar to Choose or Decline
    req1 = Booking(
        id=uuid.UUID("33333333-3333-3333-3333-333333333331"),
        customer_id=customer_user.id,
        worker_id=active_worker.id,
        category="Electrician",
        status="requested",
        booking_type="emergency_sos",
        is_urgent=True,
        urgent_surcharge=150.00,
        distance_km=2.1,
        fare_amount=450.00,
        service_lat=28.6380,
        service_lng=77.3685,
        address_text="Flat 302, Tower B, ATS Advantage, Ahinsa Khand 1, Indirapuram, Ghaziabad"
    )
    db.add(req1)

    req2 = Booking(
        id=uuid.UUID("33333333-3333-3333-3333-333333333332"),
        customer_id=customer_user.id,
        worker_id=active_worker.id,
        category="Electrician",
        status="requested",
        booking_type="on_demand",
        is_urgent=False,
        urgent_surcharge=0.00,
        distance_km=3.4,
        fare_amount=380.00,
        service_lat=28.6483,
        service_lng=77.3392,
        address_text="Plot 45, Sector 4, Vaishali, Ghaziabad"
    )
    db.add(req2)

    req3 = Booking(
        id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
        customer_id=customer_user.id,
        worker_id=active_worker.id,
        category="Electrician",
        status="requested",
        booking_type="scheduled",
        scheduled_time="Today 4:30 PM",
        is_urgent=False,
        urgent_surcharge=0.00,
        distance_km=1.8,
        fare_amount=520.00,
        service_lat=28.6852,
        service_lng=77.4421,
        address_text="B-14, Raj Nagar Sector 10, Ghaziabad"
    )
    db.add(req3)

    sample_complaint = Complaint(
        booking_id=demo_booking.id,
        customer_id=customer_user.id,
        worker_id=active_worker.id,
        subject="Scheduling slot clarification",
        description="Needed follow-up warranty receipt for newly installed MCB switch.",
        status="open",
        admin_notes="Assigned to Ghaziabad Artisan Federation helpdesk"
    )
    db.add(sample_complaint)
    db.commit()

    print("Seed complete: Standard database schema & 3 demo requests ready for manual worker choice!")
    print("\n=== DEMO LOGIN CREDENTIALS ===")
    print(f"Citizen Customer -> Phone: {DEMO_CUSTOMER_PHONE}  Password: customer123")
    print(f"Verified Worker  -> Phone: {DEMO_WORKER_PHONE}  Password: worker123")
    print("Federation Admin -> Direct access at /admin")
    db.close()

if __name__ == "__main__":
    seed_demo_data()

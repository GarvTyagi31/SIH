# 🤝 SahakarConnect — Ghaziabad Cooperative Artisan & Gig Marketplace
> **Decentralized, Cooperative-Owned Home & Artisan Services Platform with Fair Wages (93% Retention), PostGIS Geospatial Dispatch, and SHA-256 Tamper-Evident Wage Ledgers.**

---

## 🌟 Overview & Welcoming Platform

SahakarConnect provides an equitable, high-tech alternative to commercial corporate aggregators. Tailored for **Ghaziabad, Uttar Pradesh**, the platform directly connects households in **Indirapuram, Vaishali, Vasundhara, Raj Nagar, Kavi Nagar, Crossings Republik, Kaushambi, Sahibabad, and Govindpuram** with certified local artisans (Electricians, Plumbers, Carpenters, AC & Appliance Technicians, and Deep Cleaning specialists).

### Core Highlights:
- **Welcoming Homepage (`/`)**: Comprehensive landing page featuring service highlights, live worker radar map, multilingual support (English/हिन्दी), locality coverage, and instant booking shortcuts.
- **Fair Cooperative Wages**: 93% direct worker take-home, 5% platform maintenance, and 2% allocated to the Worker Welfare & Insurance Fund.
- **Sub-Second Spatial Dispatch**: Powered by **PostgreSQL + PostGIS** for accurate nearest-neighbor worker matching.
- **Cryptographic Transparency**: Chained SHA-256 tamper-evident wage ledgers proving zero wage skimming.

---

## 🚀 Key Functional Capabilities

1. **Service Provider Registration & Verification**:
   - Structured onboarding with Aadhaar KYC validation, Skill India / NCVT certification checks, and cooperative guild badges.
2. **Worker Skill Profiling & Certification**:
   - Granular skill matrices, ITI diplomas, years of trade experience, customer endorsements, and specialized tooling credentials.
3. **Customer Booking & Scheduling System**:
   - Instant on-demand dispatch (15–30 min arrival) or scheduled future service slots (8:00 AM – 8:00 PM).
4. **Geo-Location Based Service Matching (PostGIS)**:
   - Real-time `ST_DWithin` spatial radar queries querying available verified workers within 5–25 km radius across Ghaziabad sectors.
5. **Digital Payments & Invoicing**:
   - Seamless Razorpay UPI / Card payment checkout with itemized GST invoices detailing base fare, worker payout, and welfare contribution.
6. **Rating & Feedback Mechanism**:
   - Resident-verified 5-star rating system with qualitative comments and dynamic score updates for artisans.
7. **Worker Welfare & Insurance Integration**:
   - Automated 2% cooperative fund allocation providing accident cover (PMSBY), medical assistance, and artisan pension pools.
8. **Emergency & On-Demand Service Booking (24x7 SOS)**:
   - High-priority crisis booking with 15-minute response SLA for power outages, water bursts, and urgent lockouts.
9. **Cooperative Federation Administration Dashboard**:
   - Central control hub featuring live GIS heatmaps, worker verification queues, dispute desks, and financial metrics.
10. **Multilingual Accessibility**:
    - Real-time dynamic language toggling between English (EN) and Hindi (हिन्दी).
11. **AI-Based Demand Forecasting & Workforce Allocation**:
    - Predictive polynomial trend estimators forecasting 7-day demand spikes and weekend surges across Ghaziabad localities.

---

## 🏗️ 5 Technological Pillars

| Pillar | Technology Implementation |
|---|---|
| 🧠 **Artificial Intelligence (AI)** | 7-Day demand forecasting, locality surge multipliers, smart matching score, NLP review moderation |
| 📍 **Geo-Spatial Technology** | PostgreSQL + PostGIS (`SRID 4326 POINT`), `ST_DWithin`, `ST_Distance`, Leaflet.js interactive maps |
| 💳 **Digital Payment Systems** | Razorpay UPI integration, instant split settlements, cryptographic SHA-256 chained wage ledger |
| ☁️ **Cloud Computing** | High-performance FastAPI asynchronous microservices, Docker containerization, cloud PostgreSQL clustering |
| 🏛️ **Proposed Mode Software** | Democratic cooperative governance, worker wage protection (93% retention), elimination of middleman rent extraction |

---

## 🛠️ Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- PostgreSQL with PostGIS extension (or Docker)

### 2. Database Setup (Docker)
```bash
docker run --name sahakar-postgis -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=sahakarconnect -p 5432:5432 -d postgis/postgis:15-3.3
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Seed Ghaziabad Cooperative Data
```bash
python seed.py
```

### 5. Launch FastAPI Server
```bash
uvicorn main:app --reload --port 8000
```

### 6. Access Portals in Browser
- **Welcoming Homepage**: [http://localhost:8000/](http://localhost:8000/)
- **Customer Booking Portal**: [http://localhost:8000/customer](http://localhost:8000/customer)
- **Worker / Artisan Portal**: [http://localhost:8000/worker](http://localhost:8000/worker)
- **Federation Admin Dashboard**: [http://localhost:8000/admin](http://localhost:8000/admin)
- **Interactive Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

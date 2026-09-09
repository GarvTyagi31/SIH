import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import workers, bookings, admin, ai_bot, auth

app = FastAPI(
    title="SahakarConnect - Official Ghaziabad Cooperative Artisan & Citizen Service Portal",
    description="Decentralized Cooperative Home & Artisan Services Platform with Fair Wages, District GPS Matching & Verified Wage Registry",
    version="2.4.0"
)

# Secure CORS Middleware Configuration
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def render_template(request: Request, template_name: str, context: dict = None):
    ctx = context.copy() if context else {}
    ctx["request"] = request
    try:
        return templates.TemplateResponse(request=request, name=template_name, context=ctx)
    except TypeError:
        try:
            return templates.TemplateResponse(template_name, ctx)
        except TypeError:
            return templates.TemplateResponse(request, template_name, ctx)

app.include_router(auth.router)
app.include_router(workers.router)
app.include_router(bookings.router)
app.include_router(admin.router)
app.include_router(ai_bot.router)

@app.on_event("startup")
def on_startup():
    try:
        init_db()
    except Exception as e:
        print("Database startup init notice:", e)

@app.get("/")
def render_landing_page(request: Request):
    return render_template(request, "landing.html")

@app.get("/customer")
def render_customer_portal(request: Request):
    return render_template(request, "customer.html")

@app.get("/customer/login")
def render_customer_login(request: Request):
    return render_template(request, "customer_login.html")

@app.get("/customer/signup")
def render_customer_signup(request: Request):
    return render_template(request, "customer_signup.html")

@app.get("/worker")
def render_worker_portal(request: Request):
    return render_template(request, "worker.html")

@app.get("/worker/login")
def render_worker_login(request: Request):
    return render_template(request, "worker_login.html")

@app.get("/admin")
def render_admin_dashboard(request: Request):
    return render_template(request, "admin.html")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SahakarConnect Ghaziabad Hub",
        "cooperative": "Ghaziabad District Artisans & Household Workers Cooperative Federation Ltd.",
        "department": "Department of Cooperatives, Government of Uttar Pradesh",
        "version": "2.4.0"
    }

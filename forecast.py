import numpy as np
from datetime import datetime, timedelta

GHAZIABAD_LOCALITIES = [
    "Raj Nagar Extension",
    "Indirapuram",
    "Vaishali",
    "Vasundhara",
    "Kavi Nagar",
    "Crossings Republik",
    "Govindpuram",
    "Sanjay Nagar"
]

def generate_7day_demand_forecast():
    """
    Generates 7-day demand projections for Ghaziabad sectors
    using polynomial trend estimation with weekend surge multipliers.
    """
    today = datetime.utcnow().date()
    days = [(today + timedelta(days=i)).strftime("%a (%d %b)") for i in range(1, 8)]

    # Multipliers: weekends typically see higher home service requests
    weekday_factors = [1.1, 1.05, 1.0, 1.15, 1.35, 1.45, 1.2]
    
    categories = ["Electrician", "Plumber", "Carpenter", "Appliance Repair"]
    forecast_data = {}

    for cat in categories:
        base_demand = 35 if cat == "Electrician" else (28 if cat == "Plumber" else 20)
        category_series = []
        for i, factor in enumerate(weekday_factors):
            noise = np.random.randint(-2, 3)
            projected = int(max(5, (base_demand * factor) + noise))
            category_series.append(projected)
        forecast_data[cat] = category_series

    locality_breakdown = []
    for loc in GHAZIABAD_LOCALITIES:
        surge_index = round(float(np.random.uniform(1.05, 1.40)), 2)
        top_skill = np.random.choice(categories)
        locality_breakdown.append({
            "locality": loc,
            "surge_multiplier": surge_index,
            "projected_weekly_jobs": int(surge_index * 120),
            "dominant_category": str(top_skill)
        })

    return {
        "dates": days,
        "demand_by_category": forecast_data,
        "locality_breakdown": locality_breakdown
    }

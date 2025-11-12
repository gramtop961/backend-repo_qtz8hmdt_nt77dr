import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
import random

from database import db, create_document, get_documents
from schemas import Car

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Car Comparator API is running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# ---------------------- Car Data & Endpoints ----------------------

def serialize_car(doc: Dict[str, Any]) -> Dict[str, Any]:
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


def ensure_seed_cars():
    if db is None:
        return
    count = db["car"].count_documents({})
    if count >= 100:
        return

    brands = [
        ("Toyota", ["Corolla", "Camry", "RAV4", "Prius", "Highlander"]),
        ("Honda", ["Civic", "Accord", "CR-V", "Fit", "Pilot"]),
        ("Ford", ["Focus", "Fusion", "Escape", "Mustang", "Explorer"]),
        ("Chevrolet", ["Malibu", "Impala", "Equinox", "Camaro", "Traverse"]),
        ("BMW", ["3 Series", "5 Series", "X3", "X5", "2 Series"]),
        ("Mercedes", ["C-Class", "E-Class", "GLC", "GLA", "S-Class"]),
        ("Audi", ["A3", "A4", "A6", "Q3", "Q5"]),
        ("Tesla", ["Model 3", "Model Y", "Model S", "Model X", "Roadster"]),
        ("Nissan", ["Sentra", "Altima", "Rogue", "Leaf", "Pathfinder"]),
        ("Hyundai", ["Elantra", "Sonata", "Tucson", "Kona", "Santa Fe"]),
        ("Kia", ["Forte", "Optima", "Sportage", "Sorento", "Soul"]),
        ("Volkswagen", ["Golf", "Jetta", "Passat", "Tiguan", "ID.4"]),
        ("Subaru", ["Impreza", "Legacy", "Forester", "Outback", "Crosstrek"]),
        ("Mazda", ["Mazda3", "Mazda6", "CX-5", "CX-30", "MX-5"]),
        ("Lexus", ["IS", "ES", "RX", "NX", "UX"]),
        ("Volvo", ["S60", "S90", "XC40", "XC60", "XC90"]),
        ("Porsche", ["911", "Cayman", "Macan", "Cayenne", "Panamera"]),
        ("Jaguar", ["XE", "XF", "F-Pace", "E-Pace", "I-Pace"]),
        ("Jeep", ["Wrangler", "Cherokee", "Grand Cherokee", "Compass", "Renegade"]),
        ("Toyota", ["GR Supra", "C-HR", "Venza", "Sequoia", "Tacoma"]) # extra to reach 100+
    ]

    random.seed(42)
    inserted = 0
    for brand, models in brands:
        for m in models:
            year = random.randint(2016, 2024)
            base_price = {
                "Toyota": 24000, "Honda": 24000, "Ford": 25000, "Chevrolet": 25000,
                "BMW": 45000, "Mercedes": 50000, "Audi": 42000, "Tesla": 48000,
                "Nissan": 23000, "Hyundai": 22000, "Kia": 21000, "Volkswagen": 26000,
                "Subaru": 26000, "Mazda": 25000, "Lexus": 46000, "Volvo": 47000,
                "Porsche": 90000, "Jaguar": 65000, "Jeep": 35000
            }.get(brand, 30000)
            # Adjust price by model type and year
            factor = 1 + (2024 - year) * (-0.02)
            price = max(18000, base_price * factor + random.randint(-3000, 3000))

            # body types and drivetrains
            body_types = ["Sedan", "SUV", "Hatchback", "Coupe", "Truck"]
            drivetrains = ["FWD", "RWD", "AWD", "4WD"]

            perf_bias = 1.0
            if brand in ["Porsche", "BMW", "Mercedes", "Jaguar"] or "Mustang" in m or "Camaro" in m:
                perf_bias = 1.3
            if brand in ["Tesla"]:
                perf_bias = 1.4

            horsepower = int(random.randint(120, 220) * perf_bias + random.randint(-10, 40))
            if brand in ["Porsche", "Jaguar"] or "GR" in m or "911" in m:
                horsepower = int(random.randint(300, 500))

            mpg = round(max(15, 55 - horsepower / 20 + random.uniform(-2, 3)), 1)
            if brand == "Tesla":
                mpg = round(random.uniform(90, 120), 1)  # MPGe approximation

            safety = round(min(5.0, max(3.0, 4.0 + random.uniform(-0.6, 0.8))), 1)
            seating = 2 if m in ["911", "Cayman", "MX-5", "Roadster"] else random.choice([4, 5, 7])
            drivetrain = random.choice(drivetrains)
            body_type = random.choice(body_types)

            car = Car(
                brand=brand,
                model=m,
                year=year,
                price=float(price),
                horsepower=horsepower,
                mpg=mpg,
                safety_rating=safety,
                seating=seating,
                drivetrain=drivetrain,
                body_type=body_type,
            )
            try:
                create_document("car", car)
                inserted += 1
            except Exception:
                pass

    # Ensure we have at least 100. If not, duplicate varied years
    current = db["car"].count_documents({}) if db else 0
    while current < 100 and db is not None:
        sample = db["car"].find_one({})
        if not sample:
            break
        sample.pop("_id", None)
        sample["year"] = min(2024, sample.get("year", 2020) + 1)
        sample["price"] = float(sample.get("price", 30000)) * 1.01
        db["car"].insert_one(sample)
        current += 1


@app.on_event("startup")
def on_startup():
    try:
        ensure_seed_cars()
    except Exception:
        # Seeding is best-effort; don't block startup
        pass


class CompareRequest(BaseModel):
    ids: List[str]


def score_car(car: Dict[str, Any]) -> float:
    # Higher is better; price is treated inversely
    hp = float(car.get("horsepower", 0))
    mpg = float(car.get("mpg", 0))
    safety = float(car.get("safety_rating", 0))
    price = float(car.get("price", 1))
    year = int(car.get("year", 2020))

    # Normalize with simple scales
    hp_s = min(1.0, hp / 400)
    mpg_s = min(1.0, mpg / 60)
    safety_s = min(1.0, safety / 5)
    price_s = max(0.0, 1 - (price - 20000) / 80000)  # 20k best, 100k worse
    year_s = max(0.0, (year - 2015) / 10)  # 2015->0, 2025->1

    return 0.35 * hp_s + 0.25 * mpg_s + 0.25 * safety_s + 0.1 * year_s + 0.05 * price_s


@app.get("/cars")
def list_cars(q: Optional[str] = Query(default=None, description="Search by brand or model"), limit: int = 200):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    filter_q = {}
    if q:
        filter_q = {"$or": [
            {"brand": {"$regex": q, "$options": "i"}},
            {"model": {"$regex": q, "$options": "i"}}
        ]}
    docs = db["car"].find(filter_q).limit(limit)
    return [serialize_car(d) for d in docs]


@app.post("/compare")
def compare_cars(payload: CompareRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    if not payload.ids or len(payload.ids) < 1:
        raise HTTPException(status_code=400, detail="Provide 1 to 3 car ids")
    if len(payload.ids) > 3:
        raise HTTPException(status_code=400, detail="Maximum of 3 cars can be compared")

    object_ids = []
    for sid in payload.ids:
        try:
            object_ids.append(ObjectId(sid))
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid id: {sid}")
    docs = list(db["car"].find({"_id": {"$in": object_ids}}))
    if len(docs) == 0:
        raise HTTPException(status_code=404, detail="No cars found for provided ids")

    serialized = [serialize_car(d) for d in docs]
    scored = [{"car": c, "score": score_car(c)} for c in serialized]
    winner = max(scored, key=lambda x: x["score"]) if scored else None

    # Feature-by-feature winners
    def best_by(key: str, reverse: bool = True):
        return max(serialized, key=lambda x: x.get(key, 0)) if reverse else min(serialized, key=lambda x: x.get(key, 0))

    comparison = {
        "cars": serialized,
        "ranking": sorted(scored, key=lambda x: x["score"], reverse=True),
        "winner": winner,
        "feature_winners": {
            "horsepower": best_by("horsepower")["id"],
            "mpg": best_by("mpg")["id"],
            "safety_rating": best_by("safety_rating")["id"],
            "price": best_by("price", reverse=False)["id"],
            "year": best_by("year")["id"],
        }
    }
    return comparison


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

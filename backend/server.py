from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="FinTrack API", description="Personal Finance Tracking API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ========== Models ==========

class SpendingCreate(BaseModel):
    category: str
    date: str  # Format: YYYY-MM-DD
    amount: float

class SpendingUpdate(BaseModel):
    category: Optional[str] = None
    date: Optional[str] = None
    amount: Optional[float] = None

class Spending(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    date: str
    amount: float
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class IncomeCreate(BaseModel):
    month: str  # Format: YYYY-MM
    income: float
    saved: float = 0
    home: float = 0

class IncomeUpdate(BaseModel):
    income: Optional[float] = None
    saved: Optional[float] = None
    home: Optional[float] = None

class Income(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    month: str
    income: float
    saved: float = 0
    home: float = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ========== Root Endpoint ==========

@api_router.get("/")
async def root():
    return {"message": "FinTrack API is running", "version": "1.0.0"}

# ========== Spendings Endpoints ==========

@api_router.get("/spendings", response_model=List[Spending])
async def get_spendings():
    """Get all spending records"""
    spendings = await db.spendings.find({}, {"_id": 0}).to_list(10000)
    return spendings

@api_router.post("/spendings", response_model=Spending, status_code=201)
async def create_spending(spending: SpendingCreate):
    """Create a new spending record"""
    spending_obj = Spending(**spending.model_dump())
    doc = spending_obj.model_dump()
    await db.spendings.insert_one(doc)
    return spending_obj

@api_router.put("/spendings/{spending_id}", response_model=Spending)
async def update_spending(spending_id: str, spending: SpendingUpdate):
    """Update a spending record"""
    update_data = {k: v for k, v in spending.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db.spendings.find_one_and_update(
        {"id": spending_id},
        {"$set": update_data},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Spending not found")
    
    del result["_id"]
    return result

@api_router.delete("/spendings/{spending_id}")
async def delete_spending(spending_id: str):
    """Delete a spending record"""
    result = await db.spendings.delete_one({"id": spending_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Spending not found")
    return {"message": "Spending deleted successfully"}

@api_router.post("/spendings/bulk", response_model=dict)
async def create_bulk_spendings(spendings: List[SpendingCreate]):
    """Create multiple spending records at once"""
    spending_docs = []
    for s in spendings:
        spending_obj = Spending(**s.model_dump())
        spending_docs.append(spending_obj.model_dump())
    
    if spending_docs:
        await db.spendings.insert_many(spending_docs)
    
    return {"message": f"Created {len(spending_docs)} spending records"}

# ========== Income Endpoints ==========

@api_router.get("/income", response_model=List[Income])
async def get_income():
    """Get all income records"""
    income_records = await db.income.find({}, {"_id": 0}).to_list(1000)
    return income_records

@api_router.post("/income", response_model=Income, status_code=201)
async def create_income(income: IncomeCreate):
    """Create a new income record"""
    # Check if month already exists
    existing = await db.income.find_one({"month": income.month}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Income record for this month already exists. Use PUT to update.")
    
    income_obj = Income(**income.model_dump())
    doc = income_obj.model_dump()
    await db.income.insert_one(doc)
    return income_obj

@api_router.put("/income/{month}", response_model=Income)
async def update_income(month: str, income: IncomeUpdate):
    """Update an income record by month (format: YYYY-MM)"""
    update_data = {k: v for k, v in income.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db.income.find_one_and_update(
        {"month": month},
        {"$set": update_data},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Income record not found")
    
    del result["_id"]
    return result

@api_router.delete("/income/{month}")
async def delete_income(month: str):
    """Delete an income record by month"""
    result = await db.income.delete_one({"month": month})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Income record not found")
    return {"message": "Income record deleted successfully"}

@api_router.post("/income/bulk", response_model=dict)
async def create_bulk_income(income_records: List[IncomeCreate]):
    """Create multiple income records at once"""
    income_docs = []
    for i in income_records:
        income_obj = Income(**i.model_dump())
        income_docs.append(income_obj.model_dump())
    
    if income_docs:
        await db.income.insert_many(income_docs)
    
    return {"message": f"Created {len(income_docs)} income records"}

# ========== Statistics Endpoint ==========

@api_router.get("/statistics")
async def get_statistics():
    """Get summary statistics"""
    spendings = await db.spendings.find({}, {"_id": 0, "amount": 1}).to_list(10000)
    income_records = await db.income.find({}, {"_id": 0, "income": 1, "saved": 1, "home": 1}).to_list(1000)
    
    total_spending = sum(s.get("amount", 0) for s in spendings)
    total_income = sum(i.get("income", 0) for i in income_records)
    total_saved = sum(i.get("saved", 0) for i in income_records)
    total_home = sum(i.get("home", 0) for i in income_records)
    
    return {
        "total_spending": total_spending,
        "total_income": total_income,
        "total_saved": total_saved,
        "total_home": total_home,
        "net_balance": total_income - total_spending,
        "spending_count": len(spendings),
        "income_months": len(income_records)
    }

# ========== Data Seeding Endpoint ==========

@api_router.post("/seed")
async def seed_data():
    """Seed the database with initial data (only if empty)"""
    spending_count = await db.spendings.count_documents({})
    income_count = await db.income.count_documents({})
    
    if spending_count > 0 or income_count > 0:
        return {
            "message": "Database already has data",
            "spendings": spending_count,
            "income_records": income_count
        }
    
    # Initial spending data
    initial_spendings = [
        {"category": "Luminar", "date": "2025-03-27", "amount": 110424},
        {"category": "Internet", "date": "2025-03-27", "amount": 7000},
        {"category": "iTunes", "date": "2025-03-27", "amount": 7250},
        {"category": "ChatGPT", "date": "2025-03-29", "amount": 10010},
        {"category": "Internet", "date": "2025-04-02", "amount": 5000},
        {"category": "Taxi", "date": "2025-04-06", "amount": 5000},
        {"category": "Food", "date": "2025-04-06", "amount": 11500},
        {"category": "Taxi", "date": "2025-04-07", "amount": 10000},
        {"category": "Food", "date": "2025-04-07", "amount": 5250},
        {"category": "Barber", "date": "2025-04-07", "amount": 5000},
        {"category": "Taxi", "date": "2025-04-08", "amount": 17250},
        {"category": "College Project", "date": "2025-04-08", "amount": 60000},
        {"category": "Taxi", "date": "2025-04-09", "amount": 5000},
        {"category": "Food", "date": "2025-04-09", "amount": 6750},
        {"category": "Taxi", "date": "2025-04-10", "amount": 14416},
        {"category": "Food", "date": "2025-04-10", "amount": 21275},
        {"category": "Food", "date": "2025-04-12", "amount": 10000},
        {"category": "Taxi", "date": "2025-04-13", "amount": 11871.55},
        {"category": "Food", "date": "2025-04-13", "amount": 8775},
        {"category": "Doctor", "date": "2025-04-13", "amount": 28750},
        {"category": "Taxi", "date": "2025-04-14", "amount": 79750},
        {"category": "Food", "date": "2025-04-14", "amount": 6500},
        {"category": "Food", "date": "2025-04-16", "amount": 6500},
        {"category": "Food", "date": "2025-04-17", "amount": 13625},
        {"category": "Spotify", "date": "2025-04-17", "amount": 4500},
        {"category": "Food", "date": "2025-04-18", "amount": 12000},
        {"category": "Food", "date": "2025-04-19", "amount": 16600},
        {"category": "365DataSci", "date": "2025-04-19", "amount": 29584.80},
        {"category": "Food", "date": "2025-04-20", "amount": 4655},
        {"category": "Food", "date": "2025-04-21", "amount": 3750},
        {"category": "Food", "date": "2025-04-23", "amount": 5500},
        {"category": "Food", "date": "2025-04-24", "amount": 4250},
        {"category": "Barber", "date": "2025-04-24", "amount": 10000},
        {"category": "Home", "date": "2025-04-25", "amount": 35000},
        {"category": "Food", "date": "2025-04-26", "amount": 18250},
        {"category": "Taxi", "date": "2025-04-27", "amount": 9037},
        {"category": "Food", "date": "2025-04-27", "amount": 3250},
        {"category": "With-Msto", "date": "2025-04-27", "amount": 25050},
        {"category": "Korek", "date": "2025-04-28", "amount": 1400},
        {"category": "Taxi", "date": "2025-04-28", "amount": 12576.36},
        {"category": "New Laptop", "date": "2025-04-28", "amount": 1501000},
        {"category": "Taxi", "date": "2025-04-30", "amount": 4079.82},
        {"category": "Food", "date": "2025-04-30", "amount": 3750},
        {"category": "Gaming", "date": "2025-05-01", "amount": 40102},
        {"category": "Taxi", "date": "2025-05-02", "amount": 9030},
        {"category": "Taxi", "date": "2025-05-04", "amount": 7983},
        {"category": "Food", "date": "2025-05-04", "amount": 10250},
        {"category": "Food", "date": "2025-05-05", "amount": 6750},
        {"category": "Taxi", "date": "2025-05-06", "amount": 6139},
        {"category": "Taxi", "date": "2025-05-07", "amount": 1000},
        {"category": "Food", "date": "2025-05-07", "amount": 3000},
        {"category": "Food", "date": "2025-05-08", "amount": 5250},
        {"category": "Taxi", "date": "2025-05-10", "amount": 5000},
        {"category": "Food", "date": "2025-05-10", "amount": 5500},
        {"category": "Taxi", "date": "2025-05-12", "amount": 11500},
        {"category": "Food", "date": "2025-05-12", "amount": 3750},
        {"category": "Barber", "date": "2025-05-12", "amount": 5000},
        {"category": "Taxi", "date": "2025-05-13", "amount": 12500},
        {"category": "Food", "date": "2025-05-13", "amount": 2000},
        {"category": "College Poster", "date": "2025-05-13", "amount": 4000},
        {"category": "Taxi", "date": "2025-05-14", "amount": 13947},
        {"category": "Food", "date": "2025-05-14", "amount": 4000},
        {"category": "Taxi", "date": "2025-05-17", "amount": 16000},
        {"category": "Food", "date": "2025-05-17", "amount": 4000},
        {"category": "Laptop", "date": "2025-05-17", "amount": 115000},
        {"category": "Controller", "date": "2025-05-17", "amount": 35000},
        {"category": "Taxi", "date": "2025-05-18", "amount": 89750},
        {"category": "Food", "date": "2025-05-18", "amount": 29000},
        {"category": "Taxi", "date": "2025-05-19", "amount": 5000},
        {"category": "Food", "date": "2025-05-19", "amount": 5000},
        {"category": "Taxi", "date": "2025-05-20", "amount": 5000},
        {"category": "Taxi", "date": "2025-05-21", "amount": 10000},
        {"category": "Food", "date": "2025-05-21", "amount": 1250},
        {"category": "College Project", "date": "2025-05-21", "amount": 15750},
        {"category": "Food", "date": "2025-05-22", "amount": 4250},
        {"category": "Food", "date": "2025-05-25", "amount": 6250},
        {"category": "Taxi", "date": "2025-05-26", "amount": 6500},
        {"category": "Food", "date": "2025-05-26", "amount": 5000},
        {"category": "Food", "date": "2025-05-27", "amount": 5500},
        {"category": "With-Mattin", "date": "2025-05-27", "amount": 150150},
        {"category": "College Project", "date": "2025-05-27", "amount": 209209},
        {"category": "Food", "date": "2025-05-28", "amount": 5500},
        {"category": "Taxi", "date": "2025-05-29", "amount": 15000},
        {"category": "16GB RAM", "date": "2025-05-29", "amount": 73000},
        {"category": "Gaming", "date": "2025-05-30", "amount": 40040},
        {"category": "Taxi", "date": "2025-05-31", "amount": 12000},
        {"category": "Food", "date": "2025-05-31", "amount": 39169},
        {"category": "Bank Fees", "date": "2025-05-31", "amount": 1500},
        {"category": "Photo Print", "date": "2025-05-31", "amount": 19000},
        {"category": "Korek", "date": "2025-05-31", "amount": 10100},
        {"category": "Taxi", "date": "2025-06-01", "amount": 19000},
        {"category": "Food", "date": "2025-06-01", "amount": 10000},
        {"category": "Belt", "date": "2025-06-01", "amount": 30000},
        {"category": "Watch", "date": "2025-06-01", "amount": 40000},
        {"category": "Food", "date": "2025-06-02", "amount": 4500},
        {"category": "Taxi", "date": "2025-06-04", "amount": 7000},
        {"category": "Food", "date": "2025-06-04", "amount": 28018},
        {"category": "Controller", "date": "2025-06-04", "amount": 80000},
        {"category": "Wallet", "date": "2025-06-04", "amount": 4000},
        {"category": "Shoes", "date": "2025-06-04", "amount": 30000},
        {"category": "Food", "date": "2025-06-07", "amount": 2000},
        {"category": "Food", "date": "2025-06-08", "amount": 4000},
        {"category": "Taxi", "date": "2025-06-10", "amount": 23250},
        {"category": "Hospital (EIH)", "date": "2025-06-10", "amount": 106250},
        {"category": "Taxi", "date": "2025-06-11", "amount": 15250},
        {"category": "Food", "date": "2025-06-11", "amount": 10000},
        {"category": "Keyboard", "date": "2025-06-11", "amount": 30000},
        {"category": "Taxi", "date": "2025-06-12", "amount": 7500},
        {"category": "Food", "date": "2025-06-12", "amount": 6250},
        {"category": "Taxi", "date": "2025-06-15", "amount": 13250},
        {"category": "Food", "date": "2025-06-15", "amount": 4500},
        {"category": "Taxi", "date": "2025-06-16", "amount": 16029.78},
        {"category": "Food", "date": "2025-06-16", "amount": 7125},
        {"category": "Taxi", "date": "2025-06-17", "amount": 6810.82},
        {"category": "Taxi", "date": "2025-06-18", "amount": 3630.66},
        {"category": "Food", "date": "2025-06-18", "amount": 3750},
        {"category": "Taxi", "date": "2025-06-19", "amount": 15000},
        {"category": "Food", "date": "2025-06-19", "amount": 7362},
        {"category": "Food", "date": "2025-06-20", "amount": 10000},
        {"category": "Food", "date": "2025-06-22", "amount": 5500},
        {"category": "Taxi", "date": "2025-06-23", "amount": 5366.91},
        {"category": "Food", "date": "2025-06-24", "amount": 4000},
        {"category": "Fuel", "date": "2025-06-24", "amount": 10000},
        {"category": "Food", "date": "2025-06-26", "amount": 33750},
        {"category": "Fuel", "date": "2025-06-26", "amount": 10000},
        {"category": "Taxi", "date": "2025-06-27", "amount": 5500},
        {"category": "Taxi", "date": "2025-06-28", "amount": 5000},
        {"category": "Food", "date": "2025-06-28", "amount": 6175},
        {"category": "Food", "date": "2025-06-29", "amount": 6175},
        {"category": "Taxi", "date": "2025-06-30", "amount": 12660},
        {"category": "Food", "date": "2025-06-30", "amount": 3750},
        {"category": "Taxi", "date": "2025-07-01", "amount": 16523},
        {"category": "Food", "date": "2025-07-01", "amount": 16500},
        {"category": "Headset", "date": "2025-07-01", "amount": 115500},
        {"category": "Barber", "date": "2025-07-01", "amount": 5000},
        {"category": "Food", "date": "2025-07-03", "amount": 3750},
        {"category": "Internet", "date": "2025-07-03", "amount": 29500},
        {"category": "Food", "date": "2025-07-04", "amount": 5750},
        {"category": "Internet", "date": "2025-07-04", "amount": 40000},
        {"category": "Taxi", "date": "2025-07-06", "amount": 6750},
        {"category": "Taxi", "date": "2025-07-07", "amount": 4898},
        {"category": "Food", "date": "2025-07-07", "amount": 5750},
        {"category": "Gaming", "date": "2025-07-07", "amount": 67000},
        {"category": "Taxi", "date": "2025-07-08", "amount": 32357},
        {"category": "Car Fragrance", "date": "2025-07-08", "amount": 4500},
        {"category": "Barber", "date": "2025-07-08", "amount": 5000},
        {"category": "Taxi", "date": "2025-07-11", "amount": 16663},
        {"category": "Food", "date": "2025-07-11", "amount": 7600},
        {"category": "Taxi", "date": "2025-07-12", "amount": 7316},
        {"category": "Food", "date": "2025-07-12", "amount": 5937},
        {"category": "Taxi", "date": "2025-07-13", "amount": 12174},
        {"category": "Food", "date": "2025-07-13", "amount": 6500},
        {"category": "Taxi", "date": "2025-07-14", "amount": 12416},
        {"category": "Food", "date": "2025-07-14", "amount": 3750},
        {"category": "Taxi", "date": "2025-07-15", "amount": 10210},
        {"category": "Food", "date": "2025-07-15", "amount": 20000},
        {"category": "Gaming", "date": "2025-07-15", "amount": 7000},
        {"category": "Food", "date": "2025-07-18", "amount": 5500},
        {"category": "Food", "date": "2025-07-19", "amount": 5500},
        {"category": "Gaming", "date": "2025-07-19", "amount": 21447},
        {"category": "Card Swap", "date": "2025-07-19", "amount": 10000},
        {"category": "Taxi", "date": "2025-07-20", "amount": 14015},
        {"category": "Gaming", "date": "2025-07-20", "amount": 34573},
        {"category": "Taxi", "date": "2025-07-21", "amount": 13802},
        {"category": "Food", "date": "2025-07-21", "amount": 3750},
        {"category": "Taxi", "date": "2025-07-22", "amount": 12687},
        {"category": "Taxi", "date": "2025-07-23", "amount": 11681},
        {"category": "Food", "date": "2025-07-23", "amount": 6000},
        {"category": "Taxi", "date": "2025-07-24", "amount": 11000},
        {"category": "Gaming", "date": "2025-07-24", "amount": 7000},
        {"category": "Food", "date": "2025-07-25", "amount": 5700},
        {"category": "Food", "date": "2025-07-26", "amount": 2500},
        {"category": "Taxi", "date": "2025-07-27", "amount": 6822},
        {"category": "Food", "date": "2025-07-27", "amount": 11000},
        {"category": "Taxi", "date": "2025-07-29", "amount": 18427},
        {"category": "Taxi", "date": "2025-07-30", "amount": 11750},
        {"category": "Food", "date": "2025-07-30", "amount": 11410},
        {"category": "Food", "date": "2025-07-31", "amount": 7125},
        {"category": "TOEFL", "date": "2025-07-31", "amount": 100100},
        {"category": "Shoe", "date": "2025-07-31", "amount": 170750},
        {"category": "Food", "date": "2025-08-01", "amount": 11044},
        {"category": "Fuel", "date": "2025-08-01", "amount": 15000},
        {"category": "Book", "date": "2025-08-01", "amount": 64250},
        {"category": "Taxi", "date": "2025-08-02", "amount": 15000},
        {"category": "Food", "date": "2025-08-02", "amount": 1500},
        {"category": "Korek", "date": "2025-08-04", "amount": 25000},
        {"category": "Fuel", "date": "2025-08-05", "amount": 8000},
        {"category": "TOEFL", "date": "2025-08-06", "amount": 21500},
        {"category": "Taxi", "date": "2025-08-07", "amount": 12703},
        {"category": "Food", "date": "2025-08-07", "amount": 5225},
        {"category": "Taxi", "date": "2025-08-08", "amount": 8853},
        {"category": "Taxi", "date": "2025-08-09", "amount": 15000},
        {"category": "Food", "date": "2025-08-09", "amount": 6412},
        {"category": "Internet", "date": "2025-08-09", "amount": 2400},
        {"category": "Food", "date": "2025-08-12", "amount": 5700},
        {"category": "FLUX.1", "date": "2025-08-12", "amount": 13755},
        {"category": "Food", "date": "2025-08-13", "amount": 12000},
        {"category": "HONOR 400", "date": "2025-08-13", "amount": 482000},
        {"category": "Food", "date": "2025-08-14", "amount": 6000},
        {"category": "Fuel", "date": "2025-08-14", "amount": 20000},
        {"category": "Food", "date": "2025-08-15", "amount": 5937},
        {"category": "Book", "date": "2025-08-15", "amount": 2000},
        {"category": "Food", "date": "2025-08-17", "amount": 13000},
        {"category": "Car Care", "date": "2025-08-18", "amount": 10000},
        {"category": "Food", "date": "2025-08-19", "amount": 6412},
        {"category": "Car Care", "date": "2025-08-20", "amount": 41000},
        {"category": "Food", "date": "2025-08-20", "amount": 5500},
        {"category": "Food", "date": "2025-08-21", "amount": 5875},
        {"category": "Barber", "date": "2025-08-21", "amount": 2000},
        {"category": "Food", "date": "2025-08-22", "amount": 6887.50},
        {"category": "Food", "date": "2025-08-25", "amount": 17500},
        {"category": "Fuel", "date": "2025-08-27", "amount": 25000},
        {"category": "Food", "date": "2025-08-29", "amount": 6237},
        {"category": "Food", "date": "2025-08-30", "amount": 11277.25},
        {"category": "Fuel", "date": "2025-08-30", "amount": 25000},
        {"category": "Food", "date": "2025-08-31", "amount": 22750},
        {"category": "Garage", "date": "2025-08-31", "amount": 2000},
        {"category": "Food", "date": "2025-09-01", "amount": 2000},
        {"category": "Garage", "date": "2025-09-01", "amount": 2000},
        {"category": "Food", "date": "2025-09-03", "amount": 10391},
        {"category": "Car Wash", "date": "2025-09-04", "amount": 6000},
        {"category": "Fuel", "date": "2025-09-04", "amount": 10000},
        {"category": "Internet", "date": "2025-09-04", "amount": 40400},
        {"category": "Food", "date": "2025-09-06", "amount": 3500},
        {"category": "Fuel", "date": "2025-09-08", "amount": 25000},
        {"category": "Food", "date": "2025-09-09", "amount": 5500},
        {"category": "Food", "date": "2025-09-11", "amount": 5000},
        {"category": "Barber", "date": "2025-09-12", "amount": 15000},
        {"category": "Food", "date": "2025-09-13", "amount": 16000},
        {"category": "Food", "date": "2025-09-16", "amount": 5750},
        {"category": "Food", "date": "2025-09-17", "amount": 4569},
        {"category": "Food", "date": "2025-09-18", "amount": 4500},
        {"category": "Barber", "date": "2025-09-19", "amount": 10000},
        {"category": "Food", "date": "2025-09-20", "amount": 7000},
        {"category": "Food", "date": "2025-09-21", "amount": 6412},
        {"category": "Food", "date": "2025-09-22", "amount": 6412},
        {"category": "Food", "date": "2025-09-25", "amount": 13512},
        {"category": "Food", "date": "2025-09-26", "amount": 4500},
        {"category": "Fuel", "date": "2025-09-26", "amount": 25000},
        {"category": "Car Care", "date": "2025-09-26", "amount": 9000},
        {"category": "Food", "date": "2025-09-27", "amount": 11250},
        {"category": "FIB Extract", "date": "2025-09-27", "amount": 12000},
        {"category": "Food", "date": "2025-09-30", "amount": 4000},
        {"category": "Car Care", "date": "2025-10-01", "amount": 5000},
        {"category": "Food", "date": "2025-10-01", "amount": 12500},
        {"category": "Food", "date": "2025-10-02", "amount": 6700},
        {"category": "Car Plate", "date": "2025-10-02", "amount": 1550000},
        {"category": "Fuel", "date": "2025-10-03", "amount": 25000},
        {"category": "Food", "date": "2025-10-04", "amount": 5000},
        {"category": "Food", "date": "2025-10-05", "amount": 5000},
        {"category": "Food", "date": "2025-10-06", "amount": 6507},
        {"category": "Certificate", "date": "2025-10-07", "amount": 50000},
        {"category": "Food", "date": "2025-10-08", "amount": 12259},
        {"category": "Food", "date": "2025-10-09", "amount": 5500},
        {"category": "Food", "date": "2025-10-11", "amount": 20000},
        {"category": "Car Care", "date": "2025-10-12", "amount": 5000},
        {"category": "Food", "date": "2025-10-12", "amount": 6000},
        {"category": "Car Wash", "date": "2025-10-12", "amount": 10000},
        {"category": "Food", "date": "2025-10-13", "amount": 9950},
        {"category": "Food", "date": "2025-10-14", "amount": 5000},
        {"category": "Food", "date": "2025-10-15", "amount": 9500},
        {"category": "Food", "date": "2025-10-16", "amount": 5225},
        {"category": "Malzama", "date": "2025-10-17", "amount": 36000},
        {"category": "Food", "date": "2025-10-17", "amount": 3750},
        {"category": "Fuel", "date": "2025-10-17", "amount": 25000},
        {"category": "Internet", "date": "2025-10-17", "amount": 5000},
        {"category": "Food", "date": "2025-10-18", "amount": 15000},
        {"category": "Food", "date": "2025-10-20", "amount": 5795},
        {"category": "Food", "date": "2025-10-21", "amount": 6500},
        {"category": "Food", "date": "2025-10-22", "amount": 4000},
        {"category": "Food", "date": "2025-10-23", "amount": 11625},
        {"category": "Food", "date": "2025-10-24", "amount": 5650},
        {"category": "Food", "date": "2025-10-25", "amount": 17000},
        {"category": "Fuel", "date": "2025-10-25", "amount": 15000},
        {"category": "Food", "date": "2025-10-26", "amount": 5000},
        {"category": "Food", "date": "2025-10-27", "amount": 5500},
        {"category": "Food", "date": "2025-10-28", "amount": 5842},
        {"category": "Food", "date": "2025-10-29", "amount": 7750},
        {"category": "Fuel", "date": "2025-10-30", "amount": 20000},
        {"category": "Food", "date": "2025-10-31", "amount": 2000},
        {"category": "Barber", "date": "2025-10-31", "amount": 5000},
        {"category": "Food", "date": "2025-11-01", "amount": 6250},
        {"category": "Food", "date": "2025-11-03", "amount": 5700},
        {"category": "Food", "date": "2025-11-05", "amount": 9831},
        {"category": "Food", "date": "2025-11-06", "amount": 8975},
        {"category": "Food", "date": "2025-11-07", "amount": 4914},
        {"category": "Food", "date": "2025-11-08", "amount": 15750},
        {"category": "Korek", "date": "2025-11-08", "amount": 1400},
        {"category": "Car Wash", "date": "2025-11-09", "amount": 6000},
        {"category": "Food", "date": "2025-11-09", "amount": 35000},
        {"category": "Fuel", "date": "2025-11-09", "amount": 10000},
        {"category": "Internet", "date": "2025-11-10", "amount": 5000},
        {"category": "Food", "date": "2025-11-11", "amount": 5555},
        {"category": "Food", "date": "2025-11-13", "amount": 5115},
        {"category": "GitHub Copilot", "date": "2025-11-13", "amount": 13755},
        {"category": "Food", "date": "2025-11-14", "amount": 6757},
        {"category": "Food", "date": "2025-11-15", "amount": 15000},
        {"category": "Fuel", "date": "2025-11-15", "amount": 20000},
        {"category": "Food", "date": "2025-11-17", "amount": 6060},
        {"category": "Food", "date": "2025-11-18", "amount": 2500},
        {"category": "Food", "date": "2025-11-19", "amount": 6717},
        {"category": "Food", "date": "2025-11-20", "amount": 11110},
        {"category": "SQL Course", "date": "2025-11-20", "amount": 13780},
        {"category": "Internet", "date": "2025-11-20", "amount": 5000},
        {"category": "Car Wash", "date": "2025-11-21", "amount": 6000},
        {"category": "Food", "date": "2025-11-21", "amount": 4118},
        {"category": "Fuel", "date": "2025-11-21", "amount": 15000},
        {"category": "Car Care", "date": "2025-11-21", "amount": 2000},
        {"category": "Food", "date": "2025-11-22", "amount": 14000},
        {"category": "Food", "date": "2025-11-23", "amount": 6060},
        {"category": "Car Wash", "date": "2025-11-25", "amount": 5808},
        {"category": "Food", "date": "2025-11-26", "amount": 6439},
        {"category": "Fuel", "date": "2025-11-26", "amount": 15000},
        {"category": "Jacket", "date": "2025-11-27", "amount": 85000},
        {"category": "Barber", "date": "2025-11-28", "amount": 7000},
        {"category": "Fuel", "date": "2025-11-29", "amount": 25000},
        {"category": "Food", "date": "2025-12-01", "amount": 6060},
        {"category": "Food", "date": "2025-12-03", "amount": 12726},
        {"category": "Food", "date": "2025-12-04", "amount": 4545},
        {"category": "Food", "date": "2025-12-05", "amount": 8535},
        {"category": "Charger", "date": "2025-12-07", "amount": 20000},
        {"category": "Food", "date": "2025-12-10", "amount": 17000},
        {"category": "Fuel", "date": "2025-12-10", "amount": 20000},
        {"category": "Internet", "date": "2025-12-10", "amount": 5000},
        {"category": "Internet", "date": "2025-12-12", "amount": 20000},
        {"category": "Fuel", "date": "2025-12-13", "amount": 10000},
        {"category": "Food", "date": "2025-12-17", "amount": 21403},
        {"category": "Parking", "date": "2025-12-18", "amount": 6000},
        {"category": "Food", "date": "2025-12-18", "amount": 1000},
        {"category": "Food", "date": "2025-12-19", "amount": 21500},
        {"category": "Barber", "date": "2025-12-19", "amount": 5000},
        {"category": "Food", "date": "2025-12-21", "amount": 10000},
        {"category": "Food", "date": "2025-12-22", "amount": 7070},
        {"category": "Food", "date": "2025-12-23", "amount": 48480},
        {"category": "Food", "date": "2025-12-24", "amount": 6500},
        {"category": "Gaming", "date": "2025-12-24", "amount": 5999},
        {"category": "Car Oil", "date": "2025-12-25", "amount": 50000},
        {"category": "Fuel", "date": "2025-12-25", "amount": 20000},
        {"category": "Transaction Fee", "date": "2025-12-25", "amount": 1202},
        {"category": "Food", "date": "2025-12-26", "amount": 10815},
        {"category": "Food", "date": "2025-12-27", "amount": 11817},
        {"category": "Food", "date": "2025-12-28", "amount": 17600},
        {"category": "Shampoo", "date": "2025-12-28", "amount": 11500},
        {"category": "Food", "date": "2025-12-29", "amount": 6880},
        {"category": "ChatGPT", "date": "2026-01-01", "amount": 6550},
        {"category": "Food", "date": "2026-01-02", "amount": 25000},
        {"category": "Food", "date": "2026-01-03", "amount": 4383},
        {"category": "Food", "date": "2026-01-04", "amount": 5750},
        {"category": "Food", "date": "2026-01-05", "amount": 22750},
        {"category": "Food", "date": "2026-01-07", "amount": 11000},
        {"category": "Food", "date": "2026-01-08", "amount": 3500},
        {"category": "Food", "date": "2026-01-09", "amount": 8232},
        {"category": "Food", "date": "2026-01-10", "amount": 6186},
        {"category": "Food", "date": "2026-01-11", "amount": 10000},
        {"category": "Canva Pro", "date": "2026-01-11", "amount": 5000},
        {"category": "Food", "date": "2026-01-12", "amount": 11575},
        {"category": "Fuel", "date": "2026-01-12", "amount": 20000},
        {"category": "Car Care", "date": "2026-01-12", "amount": 2000},
        {"category": "Food", "date": "2026-01-14", "amount": 17019},
        {"category": "Food", "date": "2026-01-15", "amount": 6565},
        {"category": "Barber", "date": "2026-01-16", "amount": 10000},
        {"category": "Food", "date": "2026-01-16", "amount": 18000},
        {"category": "Food", "date": "2026-01-17", "amount": 40000},
        {"category": "Internet", "date": "2026-01-18", "amount": 5000},
        {"category": "Food", "date": "2026-01-18", "amount": 4500},
        {"category": "Food", "date": "2026-01-19", "amount": 3500},
        {"category": "Food", "date": "2026-01-21", "amount": 4750},
        {"category": "Food", "date": "2026-01-22", "amount": 24500},
        {"category": "Food", "date": "2026-01-23", "amount": 3850},
        {"category": "Food", "date": "2026-01-24", "amount": 11250},
        {"category": "Food", "date": "2026-01-25", "amount": 8750},
        {"category": "Food", "date": "2026-01-26", "amount": 12970},
        {"category": "Sherwan's Farewell", "date": "2026-01-27", "amount": 15050},
        {"category": "Food", "date": "2026-01-27", "amount": 6866},
        {"category": "Redmi Pad 2 Pro", "date": "2026-01-27", "amount": 425000},
        {"category": "Parking", "date": "2026-01-28", "amount": 2000},
        {"category": "Grade 12 Transcript", "date": "2026-01-28", "amount": 35000},
        {"category": "Food", "date": "2026-01-29", "amount": 18505},
        {"category": "Food", "date": "2026-01-31", "amount": 14250}
    ]
    
    # Initial income data
    initial_income = [
        {"month": "2025-03", "income": 765848.36, "saved": 0, "home": 700000},
        {"month": "2025-04", "income": 1059769.54, "saved": 0, "home": 0},
        {"month": "2025-05", "income": 1299260, "saved": 0, "home": 0},
        {"month": "2025-06", "income": 807067.18, "saved": 0, "home": 0},
        {"month": "2025-07", "income": 1324384.05, "saved": 0, "home": 0},
        {"month": "2025-08", "income": 807067.18, "saved": 0, "home": 0},
        {"month": "2025-09", "income": 1324384.05, "saved": 200000, "home": 0},
        {"month": "2025-10", "income": 807067.18, "saved": 600000, "home": 0},
        {"month": "2025-11", "income": 1324384.05, "saved": 1000000, "home": 0},
        {"month": "2025-12", "income": 821667.18, "saved": 0, "home": 0},
        {"month": "2026-01", "income": 1359322.02, "saved": 0, "home": 0}
    ]
    
    # Insert spendings
    spending_docs = []
    for s in initial_spendings:
        spending_obj = Spending(**s)
        spending_docs.append(spending_obj.model_dump())
    
    if spending_docs:
        await db.spendings.insert_many(spending_docs)
    
    # Insert income
    income_docs = []
    for i in initial_income:
        income_obj = Income(**i)
        income_docs.append(income_obj.model_dump())
    
    if income_docs:
        await db.income.insert_many(income_docs)
    
    return {
        "message": "Database seeded successfully",
        "spendings_created": len(spending_docs),
        "income_records_created": len(income_docs)
    }

# Include the router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from datetime import datetime
import os
from bson import ObjectId

# ========== MongoDB Setup ==========
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["farmdb"]
collection = db["readings"]

# ========== FastAPI Setup ==========
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Cache latest for /api/latest
latest_data = {}

@app.post("/receive")
async def receive_data(request: Request):
    global latest_data
    latest_data = await request.json()
    latest_data["timestamp"] = latest_data.get("timestamp") or datetime.now().isoformat()
    
    # Save to MongoDB
    collection.insert_one(latest_data)
    return {"status": "success"}

@app.get("/api/latest")
async def get_latest():
    safe_data = latest_data.copy()
    if "_id" in safe_data:
        safe_data["_id"] = str(safe_data["_id"])
    return JSONResponse(content=safe_data)

@app.get("/api/history")
async def get_history():
    # Fetch last 10 readings, sorted by most recent
    records = collection.find().sort("timestamp", -1).limit(10)
    history = []
    for r in records:
        r["_id"] = str(r["_id"])  # Remove ObjectId if needed
        history.append(r)
    return JSONResponse(content=history[::-1])  # Return in chronological order

@app.get("/visualise", response_class=HTMLResponse)
async def visualise_page(request: Request):
    return templates.TemplateResponse("visualise.html", {"request": request})

@app.get("/api/live_stream")
async def live_stream():
    # Return latest data (already sanitized)
    safe_data = latest_data.copy()
    if "_id" in safe_data:
        safe_data["_id"] = str(safe_data["_id"])
    return JSONResponse(content=safe_data)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

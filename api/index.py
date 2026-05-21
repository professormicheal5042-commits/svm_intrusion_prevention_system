import os
import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SVM Intrusion Prevention System API",
    description="Backend API for SmartGuard IPS Dashboard",
    version="1.0.0"
)

# Load the SVM Model (Vercel-compatible path)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "svm_model.pkl")
svm_model = None

try:
    if os.path.exists(MODEL_PATH):
        svm_model = joblib.load(MODEL_PATH)
        print("SVM Model loaded successfully.")
    else:
        print(f"Warning: Model file not found at {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")


# Configure CORS for Firebase frontend and local development
# CORS origins — now using wildcard (allow_credentials must be False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.upload import router as upload_router
from api.live_traffic import router as live_traffic_router
from api.reports import router as reports_router
from api.stats import router as stats_router
from api.save import router as save_router

app.include_router(upload_router)
app.include_router(live_traffic_router)
app.include_router(reports_router)
app.include_router(stats_router)
app.include_router(save_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the SVM Intrusion Prevention System API"}

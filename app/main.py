from fastapi import FastAPI
import monitoring.langsmith_config
from app.api_routes import router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for charts
charts_dir = "charts"
if os.path.exists(charts_dir):
    app.mount("/charts", StaticFiles(directory=charts_dir), name="charts")

@app.get("/")
def home():
    return {"message": "OpenClaw Bot Running"}

@app.get("/health")
def health():
    return {"message": "OK"}


app.include_router(router)

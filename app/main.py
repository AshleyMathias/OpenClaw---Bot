from fastapi import FastAPI
from app.api_routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "OpenClaw Bot Running"}

@app.get("/health")
def health():
    return {"message": "OK"}


app.include_router(router)

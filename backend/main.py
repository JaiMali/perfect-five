from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Perfect Five API",
    description="Backend API for the Perfect Five app",
    version="1.0.0",
)

# CORS middleware — needed later when your frontend talks to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock this down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Welcome to the Perfect Five API!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

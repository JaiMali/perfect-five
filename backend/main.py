from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.scoring import generate_reference, calculate_score
from backend.schemas import ScoreRequest, ScoreResponse, ReferenceResponse, Point

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

CHARACTERS = ["5", "3", "8", "2", "S", "A", "B"]

# Cache reference points so we don't regenerate every request
reference_cache: dict[str, list[tuple]] = {}

def get_reference(character: str) -> list[tuple]:
    """Get reference points, using cache if available."""
    if character not in reference_cache:
        reference_cache[character] = generate_reference(character)
    return reference_cache[character]



@app.get("/")
def root():
    return {"message": "Welcome to the Perfect Five API!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/characters")
def list_characters():
    return {"characters": CHARACTERS}


@app.get("/reference/{character}", response_model=ReferenceResponse)
def get_reference_points(character: str):
    if character not in CHARACTERS:
        raise HTTPException(
            status_code=400,
            detail=f"Character '{character}' not supported. Choose from: {CHARACTERS}"
        )
    
    edge_points = get_reference(character)

    return ReferenceResponse(
        character=character,
        edge_points=[Point(x=p[0], y=p[1]) for p in edge_points],
        num_points=len(edge_points),
    )

    
@app.post("/score", response_model=ScoreResponse)
def score_drawing(request: ScoreRequest):
    if request.character not in CHARACTERS:
        raise HTTPException(
            status_code=400,
            detail=f"Character '{request.character}' not supported."
        )

    if len(request.user_points) < 10:
        raise HTTPException(
            status_code=400,
            detail="Need at least 10 points to score a drawing."
        )
    


# Convert Pydantic Points to tuples for scoring logic
    user_tuples = [(p.x, p.y) for p in request.user_points]
    ref_points = get_reference(request.character)

    score = calculate_score(user_tuples, ref_points)


    # Generate feedback
    if score >= 80:
        feedback = "Amazing! Nearly perfect!"
    elif score >= 60:
        feedback = "Nice work! Getting close!"
    else:
        feedback = "Not bad, keep practicing!"

    return ScoreResponse(
        score=score,
        character=request.character,
        num_user_points=len(request.user_points),
        feedback=feedback,
    )

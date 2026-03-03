Perfect five is a web-based drawing game that scores how accurately you can draw characters. Built with FastAPI and React + TypeScript.
Intended to be a copy cat of the game where you need to draw a perfect circle. (https://neal.fun/perfect-circle/)
My take on making a mini game with python for the first time, and experimenting with FastAPI, TypeScript, and React


Live Demo: https://perfect-five.vercel.app
API Documentation: https://perfect-five-api.onrender.com/docs


---

## Features

- Real-time scoring as you draw
- Multiple characters to practice (5, 3, 8, 2, S, A, B)
- Overlay toggle to see the perfect shape
- Mobile-friendly with touch support
- Fast API with automatic documentation

---

## Tech Stack

Backend:
- FastAPI
- Pydantic (data validation)
- Pillow (image processing)
- Uvicorn (ASGI server)

Frontend:
- React 18
- TypeScript
- Vite
- HTML Canvas for drawing

DevOps:
- Render (backend hosting)
- Vercel (frontend hosting)
- Docker
- GitHub Actions (CI/CD)


---


## Project Structure
```
perfect-five/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   └── test_scoring.py
│   ├── __init__.py
│   ├── main.py
│   ├── scoring.py
│   ├── schemas.py
│   ├── Dockerfile
│   ├── librefranklin-bold.ttf
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── DrawingCanvas.tsx
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── api.ts
│   │   ├── types.ts
│   │   └── main.tsx
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   └── screenshot.png
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── render.yaml
└── README.md
```
---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker (optional)


### Backend Setup
```
python3 -m venv venv
(mac) source venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```
Backend runs at http://127.0.0.1:8000


### Frontend Setup
```
cd frontend
npm install
npm run dev
```
Frontend runs at http://localhost:5173


### Docker Setup

```
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

---

## API Endpoints

GET  /              Health check
GET  /health        Service status
GET  /characters    List available characters
GET  /reference/{char}   Get reference points for a character
POST /score         Score a user's drawing

Full documentation at /docs endpoint.

---

## How Scoring Works

1. Reference Generation: Each character is rendered as a 500x500 image and only edge points are extracted (since pixel density varies between characters, giving an unfair importance to denser parts of a character)
2. Normalization: Both user drawing and reference are normalized to a 0-100 scale
3. Bidirectional Distance: Measures accuracy (How close user is to reference) and coverage (How close reference points are to user)
4. Final Score: Combined average converted to a percentage

---

## Running Tests

```
pytest backend/tests/ -v
```
---

## Roadmap

[x] Core drawing functionality
[x] Real-time scoring
[x] Multiple character support
[x] Deploy to production
[x] Docker containerization
[x] CI/CD pipeline
[x] Improve scoring algorithm
[x] Add user accounts and leaderboard

---

## License

MIT

---

# OddNoty 🚨⚽

**Real-time Over/Under Goal Odds Alert Platform**

OddNoty monitors live football matches and generates alerts when specific Over/Under odds conditions are met — helping bettors, trading syndicates, and sports analysts spot profitable opportunities in real time.

---

## Tech Stack

| Layer      | Technology     |
|------------|----------------|
| Frontend   | Next.js (App Router, TypeScript) |
| Backend    | FastAPI (Python) |
| Worker     | Python async worker |
| Database   | PostgreSQL |
| Cache      | Redis |
| Alerts     | Telegram Bot |
| Deployment | Docker / Docker Compose |

## Supported Markets

| Over    | Under    |
|---------|----------|
| Over 0.5 | Under 0.5 |
| Over 1.5 | Under 1.5 |
| Over 2.5 | Under 2.5 |
| Over 3.5 | Under 3.5 |

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend dev)
- Python 3.11+ (for backend / worker dev)
- PostgreSQL 15+
- Redis 7+

### 1. Clone & Configure

```bash
git clone <repo-url> OddNoty
cd OddNoty
cp .env.example .env
# Edit .env with your API keys and database credentials
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

| Service   | URL                        |
|-----------|----------------------------|
| Frontend  | http://localhost:3000       |
| Backend   | http://localhost:8000       |
| API Docs  | http://localhost:8000/docs  |

### 3. Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Worker:**
```bash
cd worker
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
OddNoty/
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
├── worker/           # Async odds worker
├── docker/           # Dockerfiles
├── docs/             # Documentation
├── scripts/          # Utility scripts
├── docker-compose.yml
├── .env.example
└── README.md
```

## Deployment (Run 24/7)

Since OddNoty needs to monitor matches while your laptop is off, you should deploy the worker to a cloud platform:

### Render (Recommended)
1. Push your code to GitHub: `git push origin main`
2. Create a **Background Worker** on [Render](https://render.com/).
3. Connect your GitHub repo.
4. Set the build command: `pip install -r worker/requirements.txt`
5. Set the start command: `python worker/main.py`
6. Add Environment Variables from your `.env` to the Render Dashboard.

### Key Pool Configuration
OddNoty uses a **Multi-Key Rotation** system to maximize free API quotas.
- Copy `worker/goaledge_keys.yaml` to `worker/goaledge_keys.local.yaml`.
- Add your actual API keys to the `.local.yaml` file.
- The worker will automatically prefer `.local.yaml` and rotate keys if one hits a limit (429).

## Data Pipeline (every 10-30 seconds)

1. **Score Pillar**: Fetch live scores (Football-Data, API-Football)
2. **Odds Pillar**: Fetch O/U odds (TheOddsAPI, Betfair)
3. **Storage**: Save odds snapshots to PostgreSQL
4. **Movement**: Detect significant price shifts (>15%)
5. **Alerts**: Evaluate custom rules & notify via Telegram

## License

MIT

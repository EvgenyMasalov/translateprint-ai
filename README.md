# LyricAI Studio (TranslatePrint AI)

Professional AI-powered songwriting and translation platform.

## Architecture

LyricAI Studio uses a modular Python backend and a decoupled frontend architecture.

### Backend (app/)
- **FastAPI:** Modern, high-performance web framework.
- **SQLAlchemy & Alembic:** Robust database ORM and migration system.
- **JWT Security:** Standard-based user authentication.
- **Service Layer:** Clean integration with external LLM providers.

### Frontend (Vanilla JS + ES Modules)
- **Modular JS:** Reusable logic for API calls, Auth, and UI utilities in `assets/js/`.
- **Tailwind CSS:** Modern styling with dark mode support.
- **localStorage Sync:** Efficient state management across pages.

## Project Structure

```
├── app/                # Backend source
│   ├── api/            # API Routers (auth, songs, webhooks)
│   ├── core/           # Config, Security, DB session
│   ├── models/         # SQLAlchemy & Pydantic models
│   └── services/       # Business logic (LLM integrations)
├── assets/js/          # Frontend modules (api, auth, editor)
├── alembic/            # Database Migrations
├── tests/              # Python Unit Tests
├── tests-e2e/          # Playwright E2E Tests
├── index.html          # Main Editor UI
├── agent.html          # AI Agent UI
└── registration.html   # Auth UI
```

## Setup & Running

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Create `.env` from `.env.example` and set your `JWT_SECRET`.

3. **Run Migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start Backend:**
   ```bash
   python -m app.main
   ```

5. **Start Frontend:**
   You can use any static server, e.g.:
   ```bash
   npx http-server . -p 8080
   ```

## Testing

- **Unit Tests:**
  ```bash
  $env:PYTHONPATH="."; python -m unittest discover tests
  ```
- **E2E Tests:**
  ```bash
  cd tests-e2e
  npm test
  ```

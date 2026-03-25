# TranslatePrint AI — LyricAI Studio

A multi-agent AI songwriting and translation platform powered by n8n, Polza AI, and Claude Sonnet 4.

## Architecture

The system uses a **3-webhook microservice architecture** orchestrated by n8n:

| Webhook | Agent | Model | Purpose |
|---------|-------|-------|---------|
| `/analyze-lyrics` | Linguistic Analyzer + Cultural Bridge | Magnum 72b | Structure, metaphors, mood, literal translation |
| `/poet-agent` | Creative Poet | Rocinante 12b | Poetic adaptation preserving rhythm |
| `/literary-editor` | Literary Editor | Claude Sonnet 4 | Surgical final polish |

## Pages

- **Editor** (`index.html`) — Main dashboard with lyrics input, language selection, and 4 analysis cards (Mood, Structure, Metaphors, Translation)
- **Agent Pro** (`agent.html`) — Premium literary editing page with Analyze Manuscript (Rocinante) and Deep Analyze (Claude Sonnet 4)

## Quick Start

1. Make sure Docker Desktop is running with n8n container
2. Import `n8n_workflow_user_fixed.json` into n8n and configure API keys
3. Double-click `start.bat`

## Tech Stack

- **Frontend:** HTML + Tailwind CSS + Vanilla JS
- **Backend:** n8n (Docker) with LangChain AI Agents
- **Models:** Magnum v4 72b, Rocinante 12b, Claude Sonnet 4 (via Polza AI)
- **State:** Browser localStorage for cross-page data sync

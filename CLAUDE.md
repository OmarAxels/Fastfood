# Claude AI Assistant Notes

## Virtual Environment
**IMPORTANT**: Always activate the virtual environment before running any Python commands:

For scraper (located in scraper/venv):
```bash
cd scraper && source venv/Scripts/activate
```

For backend (located in backend/venv):
```bash
cd backend && source venv/Scripts/activate
```

## Common Commands
- Run scraper: `python scraper/src/main.py`
- Run tests: `pytest` (after activating venv)
- Run lint: `ruff check .` (after activating venv)
- Run typecheck: `mypy .` (after activating venv)

## Project Structure
- `scraper/` - Main scraper application
- `backend/` - Backend API
- `frontend/` - Next.js frontend application

## Notes
- This project uses a Python virtual environment
- Always activate venv before running Python commands
- The scraper extracts restaurant offers and processes them with AI
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Note**: For comprehensive instructions, architecture details, and project conventions, please refer to [AGENTS.md](AGENTS.md).

## Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Development server
python src/app.py

# Format and lint
black src/ tests/
isort src/ tests/
ruff check src/ tests/
ruff format src/ tests/
```

See [AGENTS.md](AGENTS.md) for more details.

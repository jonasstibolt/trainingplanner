# Training Planner

A local-first training plan manager built with Django.

Plans are written in Markdown, versioned automatically on edit,
and can be restored safely. Designed to work well with LLM-generated
training plans and manual editing.

## Core ideas
- Markdown is the source of truth
- Plans are versioned on change
- Restores are reversible
- Offline-first, no cloud required

## Running locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver

## LICENSE
MIT

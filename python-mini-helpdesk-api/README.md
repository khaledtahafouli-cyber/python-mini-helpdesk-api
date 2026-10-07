# Mini Help Desk API

A small Python REST API for managing tasks and help-desk tickets.

## Features
- Create a task
- List all tasks
- Get a task by ID
- Update a task
- Delete a task
- Status values: Open, In Progress, Completed
- Priority levels: Low, Medium, High
- SQLite database storage
- Clear API documentation

## Technologies Used
- Python 3
- Flask
- SQLite

## Project Structure
- `app.py` - main API logic
- `tests/` - test files
- `data/` - SQLite database directory

## Installation
```bash
git clone <repository-url>
cd python-mini-helpdesk-api
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
Start the server:
```bash
python app.py
```

Use the API:
```bash
curl http://127.0.0.1:5000/tasks
curl -X POST http://127.0.0.1:5000/tasks -H "Content-Type: application/json" -d '{"title":"Fix bug","description":"Login error","status":"Open","priority":"High"}'
curl http://127.0.0.1:5000/tasks/1
curl -X PUT http://127.0.0.1:5000/tasks/1 -H "Content-Type: application/json" -d '{"status":"In Progress","priority":"Medium"}'
curl -X DELETE http://127.0.0.1:5000/tasks/1
```

## Running Tests
```bash
pytest
```

## Future Improvements
- Add auth for users
- Add task comments
- Add filters by status and priority
- Add pagination

# Personalized Learning Path - Backend

This is the FastAPI backend for the Personalized Learning Path application. It provides APIs for generating personalized learning paths based on user profiles and skills.

## Features

- User profile management
- Personalized learning path generation
- NSQF course catalog
- Chat-based learning assistant (with OpenAI integration)
- RESTful API with JWT authentication

## Prerequisites

- Python 3.9+
- SQLite (default) or PostgreSQL
- OpenAI API key (optional, for chat functionality)

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/personalized-learning-path.git
   cd personalized-learning-path/backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix or MacOS:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python -m scripts.init_db
   ```

## Running the Application

### Development

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Production

For production, use a production-grade ASGI server like Uvicorn with Gunicorn:

```bash
pip install gunicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Available Endpoints

- `GET /health` - Health check
- `POST /api/profile` - Create a new learner profile
- `POST /api/recommend` - Get learning path recommendations
- `GET /api/courses` - List NSQF courses
- `POST /api/chat` - Chat with learning assistant

## Testing

Run the test suite with:

```bash
pytest tests/ -v
```

## Project Structure

```
backend/
├── app/
│   ├── api/               # API routes
│   ├── core/              # Core configurations
│   ├── db/                # Database configurations
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic models
│   ├── services/          # Business logic
│   ├── database.py        # Database connection
│   └── main.py            # FastAPI application
├── tests/                 # Test files
├── scripts/               # Utility scripts
├── .env.example           # Environment variables template
└── requirements.txt       # Dependencies
```

## Environment Variables

See `.env.example` for all available environment variables.

## License

MIT

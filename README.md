# Personalized Learning Path

A full-stack application for creating personalized learning paths using AI recommendations.

## Project Structure

```
personalized-learning-path/
├── backend/               # FastAPI backend
│   ├── app/              
│   │   ├── api/          # API routes
│   │   ├── core/         # Core configurations
│   │   ├── db/           # Database configurations
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic models
│   │   ├── services/     # Business logic
│   │   └── tests/        # Backend tests
│   └── migrations/       # Database migrations
│
├── frontend/             # React frontend
│   └── src/
│       ├── components/   # Reusable components
│       ├── pages/        # Page components
│       ├── services/     # API services
│       ├── utils/        # Utility functions
│       └── assets/       # Static assets
│
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore file
└── docker-compose.yml  # Docker configuration (optional)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory and set up the virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   # Activate the virtual environment
   # Windows:
   .\.venv\Scripts\activate
   # Unix/macOS:
   # source .venv/bin/activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the following variables:
     ```env
     # Required for AI features
     OPENAI_API_KEY=your_openai_api_key_here
     
     # Database configuration
     DATABASE_URL=sqlite:///./learning_path.db
     
     # Security (generate with: openssl rand -hex 32)
     SECRET_KEY=your_secret_key_here
     ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
     ```

4. Initialize the database and seed with sample data:
   ```bash
   make seed
   ```

5. Start the backend server:
   ```bash
   make run
   ```
   The API will be available at `http://localhost:8000`
   - API Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Frontend Setup

1. Navigate to the frontend directory and install dependencies:
   ```bash
   cd ../frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`

## 🛠 Development Commands

### Backend Commands
```bash
# Run database migrations
alembic upgrade head

# Run tests
make test

# Format code
make format

# Lint code
make lint
```

### Frontend Commands
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm test
```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

## Development

- Backend API will be available at `http://localhost:8000`
- Frontend will be available at `http://localhost:5173`
- API documentation (Swagger UI) at `http://localhost:8000/docs`

## Testing

Run backend tests:
```bash
cd backend
pytest
```

## License

MIT

# Smart Farming Advisory System

AI-powered farming recommendations combining weather data and machine learning.

## Tech Stack
- **Backend**: Flask
- **ML**: scikit-learn
- **Database**: PostgreSQL (Neon)
- **Weather API**: OpenWeather

## Quick Start

```bash
# Clone and setup
git clone <repo>
cd smart_farming_advisory

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run application
python app.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/predict` | Predict crop yield |
| POST | `/api/v1/advisory` | Get farming recommendations |
| GET | `/api/v1/weather/<location>` | Get current weather |

## Project Structure

```
smart_farming_advisory/
├── config/           # Configuration
├── src/              # Source code
│   ├── api/          # Flask routes
│   ├── models/       # ML & weather services
│   ├── services/     # Business logic
│   ├── entities/     # ORM models
│   └── utils/        # Utilities
├── ml_models/        # Trained models
├── tests/            # Test suite
└── scripts/          # Utility scripts
```

## License

MIT

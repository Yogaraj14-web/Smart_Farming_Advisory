# Smart Farming Advisory System using AI
## Project Structure

```
smart_farming_advisory/
│
├── config/                          # Configuration management
│   ├── __init__.py
│   ├── settings.py                  # Environment variables, API keys, DB config
│   └── constants.py                 # Fixed values (crop types, thresholds)
│
├── src/                             # Source code
│   ├── __init__.py
│   │
│   ├── api/                         # API layer
│   │   ├── __init__.py
│   │   ├── routes.py                # Flask route definitions
│   │   └── schemas.py                # Request/response schemas (Pydantic)
│   │
│   ├── models/                      # ML and external services
│   │   ├── __init__.py
│   │   ├── ml_models.py             # ML model loading and inference
│   │   ├── crop_advisor.py           # Main advisory logic
│   │   └── weather_service.py        # OpenWeather API integration
│   │
│   ├── services/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── database.py              # Database operations
│   │   ├── farm_service.py          # Farm CRUD operations
│   │   └── advisory_service.py      # Advisory generation logic
│   │
│   ├── entities/                    # Data models
│   │   ├── __init__.py
│   │   └── models.py                # ORM models (SQLAlchemy)
│   │
│   └── utils/                       # Utilities
│       ├── __init__.py
│       ├── logger.py                # Logging configuration
│       └── validators.py             # Input validation
│
├── ml_models/                       # ML model artifacts
│   ├── __init__.py
│   ├── crop_yield_model.pkl         # Trained model file
│   ├── scaler.pkl                   # Feature scaler
│   └── model_config.json            # Model metadata
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── test_api/                    # API endpoint tests
│   ├── test_models/                 # ML model tests
│   └── test_services/                # Service layer tests
│
├── migrations/                      # Database migrations (Alembic)
│
├── scripts/                         # Utility scripts
│   └── train_model.py               # Model training script
│
├── logs/                            # Log files
│
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
├── .gitignore
├── app.py                           # Application entry point
├── wsgi.py                          # WSGI entry point
├── Dockerfile                       # Docker configuration
└── README.md                        # Project documentation
```

## File Responsibilities

| File | Responsibility |
|------|----------------|
| [`config/settings.py`](config/settings.py) | Loads env vars, API keys, DB URI from `.env` |
| [`config/constants.py`](config/constants.py) | Crop types, soil types, irrigation thresholds |
| [`src/api/routes.py`](src/api/routes.py) | Flask endpoints (`/predict`, `/weather`, `/farm`) |
| [`src/api/schemas.py`](src/api/schemas.py) | Pydantic schemas for request/response validation |
| [`src/models/weather_service.py`](src/models/weather_service.py) | Calls OpenWeather API, caches responses |
| [`src/models/ml_models.py`](src/models/ml_models.py) | Loads `.pkl` models, runs inference |
| [`src/models/crop_advisor.py`](src/models/crop_advisor.py) | Combines weather + ML output for recommendations |
| [`src/services/database.py`](src/services/database.py) | DB connection pool, session management |
| [`src/services/farm_service.py`](src/services/farm_service.py) | Farm CRUD, historical data management |
| [`src/services/advisory_service.py`](src/services/advisory_service.py) | Generates farming recommendations |
| [`src/entities/models.py`](src/entities/models.py) | SQLAlchemy ORM models (Farm, Crop, Advisory) |
| [`src/utils/logger.py`](src/utils/logger.py) | Configures structured logging |
| [`src/utils/validators.py`](src/utils/validators.py) | Input sanitization and validation |
| [`ml_models/crop_yield_model.pkl`](ml_models/crop_yield_model.pkl) | Trained scikit-learn model |
| [`scripts/train_model.py`](scripts/train_model.py) | Model training pipeline |
| [`app.py`](app.py) | Flask app factory, middleware setup |

# Smart Farming Advisory System - Frontend

React frontend for the Smart Farming Advisory System.

## Tech Stack
- React 18
- Vite (build tool)
- Plain CSS (no Tailwind, Bootstrap, MUI)
- Fetch API

## Project Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── App.css
    ├── index.css
    ├── services/
    │   └── api.js          # API integration
    └── components/
        ├── PredictForm.jsx  # Predict endpoint form
        ├── SubmitForm.jsx   # Submit + Save form
        └── History.jsx      # History table
```

## Installation & Running

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# The app will open at http://localhost:3000
```

## API Configuration

The frontend connects to the Flask backend at:
- **Base URL**: `http://localhost:5000`

Ensure the Flask backend is running before using the frontend.

## Features

### 1. Predict Fertilizer (POST /predict)
- Enter soil nutrient values (N, P, K)
- Select leaf color from dropdown
- Enter city for weather data
- Get AI recommendation without saving

### 2. Submit & Save (POST /submit-data)
- Same inputs as Predict form
- Additionally saves result to Neon PostgreSQL database
- Records sensor data, weather, and prediction

### 3. History (GET /history)
- View past predictions in a table
- Filter by user ID
- Shows date, city, fertilizer, and confidence

## Dependencies

All dependencies are in `package.json`:
- react
- react-dom
- @vitejs/plugin-react
- vite

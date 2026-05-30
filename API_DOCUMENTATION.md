# API Documentation

## Electricity Demand Forecasting System - API Reference

Base URL: `http://localhost:5000/api`

---

## Endpoints

### 1. System Status

**GET** `/status`

Get the current system and models status.

**Response:**
```json
{
  "status": "ready",
  "models_loaded": true,
  "available_models": ["arima", "sarima", "prophet", "lstm"],
  "timestamp": "2024-01-15T10:30:45.123456",
  "total_predictions": 42,
  "last_prediction": {
    "timestamp": "2024-01-15T10:30:00",
    "model": "lstm",
    "forecast_days": 7,
    "predictions_count": 7
  }
}
```

**Status Codes:**
- `200 OK` - System is operational

---

### 2. Make Predictions

**POST** `/predict`

Generate electricity demand forecast using specified model.

**Request Body:**
```json
{
  "days_ahead": 7,
  "model_type": "best"
}
```

**Parameters:**
- `days_ahead` (integer): Number of days to forecast (1-90, default: 7)
- `model_type` (string): Model to use - "best", "arima", "sarima", "prophet", "lstm" (default: "best")

**Response:**
```json
{
  "model": "lstm",
  "forecast_days": 7,
  "predictions": [98.5, 102.3, 105.1, 103.8, 101.2, 99.5, 97.8],
  "dates": [
    "2024-01-16",
    "2024-01-17",
    "2024-01-18",
    "2024-01-19",
    "2024-01-20",
    "2024-01-21",
    "2024-01-22"
  ],
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

**Status Codes:**
- `200 OK` - Prediction successful
- `400 Bad Request` - Invalid model type
- `503 Service Unavailable` - Models not loaded
- `500 Internal Server Error` - Prediction failed

---

### 3. Get Best Model

**GET** `/models/best`

Get information about the best performing model.

**Response:**
```json
{
  "best_model": "lstm",
  "training_date": "2024-01-15T08:15:30",
  "metrics": {
    "rmse": 10.89,
    "mae": 8.45,
    "mape": 6.89,
    "r2": 0.8912,
    "directional_accuracy": 85.23
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Model info not available

---

### 4. Compare Models

**GET** `/models/comparison`

Compare performance metrics of all trained models.

**Response:**
```json
{
  "comparison": {
    "arima": {
      "metrics": {
        "rmse": 12.45,
        "mae": 9.87,
        "mape": 8.92,
        "r2": 0.8456,
        "directional_accuracy": 78.45
      },
      "is_best": false
    },
    "lstm": {
      "metrics": {
        "rmse": 10.89,
        "mae": 8.45,
        "mape": 6.89,
        "r2": 0.8912,
        "directional_accuracy": 85.23
      },
      "is_best": true
    }
  },
  "best_model": "lstm",
  "training_date": "2024-01-15T08:15:30"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Model info not available

---

### 5. Get Historical Data

**GET** `/historical`

Get historical actual vs predicted demand data.

**Query Parameters:**
- `days` (integer): Number of days to retrieve (default: 30, max: 365)

**Response:**
```json
{
  "dates": ["2024-01-01", "2024-01-02", "..."],
  "actual": [85.2, 86.5, 88.1, "..."],
  "predicted": [84.9, 86.2, 88.5, "..."]
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Failed to retrieve data

---

### 6. Get Insights

**GET** `/insights`

Get trend analysis and seasonal patterns.

**Response:**
```json
{
  "seasonal_patterns": {
    "peak_hours": [18, 19, 20],
    "off_peak_hours": [2, 3, 4, 5],
    "seasonal_variation": "Higher in winter and summer, lower in spring and fall"
  },
  "trends": {
    "overall_trend": "Slight upward trend",
    "year_over_year_change": "+3.5%",
    "month_over_month_change": "+1.2%"
  },
  "anomalies": {
    "recent_events": [],
    "forecasted_anomalies": []
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Failed to calculate insights

---

### 7. Get Prediction Logs

**GET** `/logs`

Get history of all predictions made.

**Query Parameters:**
- `limit` (integer): Maximum number of logs to return (default: 50, max: 1000)

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "model": "lstm",
      "forecast_days": 7,
      "predictions_count": 7
    },
    {
      "timestamp": "2024-01-15T10:25:15",
      "model": "arima",
      "forecast_days": 14,
      "predictions_count": 14
    }
  ],
  "total": 2
}
```

**Status Codes:**
- `200 OK` - Success

---

### 8. Clear Logs

**POST** `/clear-logs`

Clear all prediction logs (requires confirmation).

**Response:**
```json
{
  "message": "Logs cleared"
}
```

**Status Codes:**
- `200 OK` - Logs cleared
- `500 Internal Server Error` - Failed to clear logs

---

### 9. Health Check

**GET** `/health`

Simple health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message describing what went wrong"
}
```

**Common Errors:**
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service not ready

---

## Authentication

The API currently does not require authentication. In production, implement:
- JWT tokens
- API keys
- OAuth 2.0

---

## Rate Limiting

No rate limiting is currently implemented. In production, recommend:
- 100 requests per minute per IP
- Adaptive rate limiting for ML prediction endpoints

---

## Example Usage

### Python (requests library)

```python
import requests
import json

BASE_URL = "http://localhost:5000/api"

# Get status
response = requests.get(f"{BASE_URL}/status")
print(response.json())

# Make prediction
payload = {
    "days_ahead": 7,
    "model_type": "best"
}
response = requests.post(f"{BASE_URL}/predict", json=payload)
predictions = response.json()
print(predictions)

# Get models comparison
response = requests.get(f"{BASE_URL}/models/comparison")
comparison = response.json()
print(comparison)
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:5000/api";

// Get status
fetch(`${BASE_URL}/status`)
  .then(res => res.json())
  .then(data => console.log(data));

// Make prediction
fetch(`${BASE_URL}/predict`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    days_ahead: 7,
    model_type: "best"
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

### curl

```bash
# Get status
curl http://localhost:5000/api/status

# Make prediction
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "days_ahead": 7,
    "model_type": "best"
  }'

# Get models comparison
curl http://localhost:5000/api/models/comparison
```

---

## Response Time

Typical response times:
- Status endpoint: < 50ms
- Historical data: 100-300ms
- Prediction (ARIMA/SARIMA): 200-500ms
- Prediction (LSTM): 500-2000ms
- Comparison/Insights: 100-200ms

---

## CORS Configuration

The API enables CORS for all origins. Update `app.py` for production:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

---

## Versioning

Current API Version: 1.0

The API URL follows: `/api/v1/endpoint` (future versions)

---

## Changelog

### v1.0 (2024-01-15)
- Initial API release
- Support for 4 ML models
- Prediction logging
- Model comparison metrics

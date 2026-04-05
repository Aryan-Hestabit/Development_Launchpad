# Deployment Notes - Income Prediction API

## Overview

FastAPI-based REST API for income prediction (>50K or <=50K) using XGBoost model with drift monitoring capabilities.

**Model:** XGBoost Classifier  
**Features:** 30 engineered features  
**Task:** Binary classification  
**Framework:** FastAPI + Uvicorn  
**Deployment:** Docker containerized  

---

## Project Structure

``` bash
Week6/
├── deployment/
│   ├── api.py                          # FastAPI application
│   ├── deploy_preprocessing.py         # Preprocessing pipeline
│   ├── Dockerfile                      # Container definition
│   ├── Deployment_Requirement.txt      # Python dependencies
│   └── .env.example                    # Environment config template
├── monitoring/
│   └── drift_checker.py                # Drift detection module
├── models/
│   └── tuned_model.pkl                 # Trained XGBoost model
├── data/processed/
│   ├── transformers.pkl                # Fitted encoders/scalers
│   ├── selected_features.json          # 30 feature names
│   └── X_train.csv                     # Training reference for drift
└── logs/
    ├── prediction_logs.csv             # Raw prediction audit log
    └── engineered_features_log.csv     # Engineered features for drift
```
## Option 2: Docker Deployment

### 1. Build Docker image:
```bash
docker build -f deployment/Dockerfile -t income-predictor .
```

**Build time:** ~3-5 minutes (first time)

### 2. Run container with volume mount:
```bash
docker run -p 8000:8000 -v $(pwd)/logs:/app/logs income-predictor
```

**Why volume mount?**  
Logs are written inside the container. Volume mount persists them on your host machine.

#### 3. Access the API:
- **API Base:** http://0.0.0.0:8000
- **Interactive Docs:** http://0.0.0.0:8000/docs

#### 4. Stop container:
```bash
docker stop "containerid"
```


## API Endpoints

### 1. `GET /` - Health Check

**Description:** Verify API is running

**Request:**
```bash
curl http://0.0.0.0:8000/
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Income Prediction API is running"
  "model_type": "XGBClassifier",
  "n_features": 30,
  "target_classes": ["<=50K", ">50K"]
}
```

---


### 3. `POST /predict` - Make Prediction

**Description:** Predict income category for an individual

**Request:**
```bash
curl -X POST http://0.0.0.0:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 39,
    "workclass": "State-gov",
    "education.num": 13,
    "marital.status": "Never-married",
    "occupation": "Adm-clerical",
    "relationship": "Not-in-family",
    "race": "White",
    "sex": "Male",
    "capital.gain": 2174,
    "capital.loss": 0,
    "hours.per.week": 40,
    "native.country": "United-States"
  }'
```

**Input Schema:**

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| age | int | 17-90 | Age of individual |
| workclass | string | required | Type of employment |
| education.num | int | 1-16 | Years of education |
| marital.status | string | required | Marital status |
| occupation | string | required | Occupation type |
| relationship | string | required | Relationship status |
| race | string | required | Race |
| sex | string | "Male" or "Female" | Sex |
| capital.gain | float | >= 0 | Capital gains |
| capital.loss | float | >= 0 | Capital losses |
| hours.per.week | int | 1-100 | Hours worked per week |
| native.country | string | required | Native country |

**Response:**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "prediction": 0,
  "label": "<=50K",
  "probability": 0.234,
  "model_version": "1.0.0",
  "timestamp": "2026-02-22 10:30:00"
}
```

**What happens behind the scenes:**
1. Input validation (Pydantic)
2. Feature engineering (23 features created)
3. Transformation (encoders/scalers applied → 60 features)
4. Feature selection (filtered to 30 features)
5. Model prediction
6. Logging to both CSV files

---

### 4. `GET /check-drift?days=7` - Check Data Drift

**Description:** Analyze drift in engineered features

**Request:**
```bash
# Check last 7 days (default)
curl http://localhost:8000/check-drift

# Check last 30 days
curl http://localhost:8000/check-drift?days=30
```

**Response:**
```json
{
  "status": "success",
  "days_analyzed": 7,
  "total_predictions": 523,
  "recent_predictions": 89,
  "features_analyzed": 30,
  "drift_results": [
    {
      "feature": "age",
      "value": 0.772,
      "status": "significant_drift",
      "metric": "psi"
    },
    {
      "feature": "is_married",
      "value": 0.12,
      "status": "significant_drift",
      "metric": "proportion_diff"
    }
  ],
  "recommendation": "retrain",
  "message": "2 features showing significant drift. Retrain recommended!",
  "threshold_psi": 0.2,
  "note": "Drift check performed on 30 engineered features that the model actually uses"
}
```

**Drift Metrics:**

| Metric | Used For | Thresholds |
|--------|----------|------------|
| **PSI** | Continuous features | < 0.1 = Stable, 0.1-0.2 = Slight, > 0.2 = Significant |
| **Proportion Diff** | Binary features (0/1) | < 5% = Stable, 5-10% = Slight, > 10% = Significant |

**Recommendations:**
- `stable` → No action needed
- `monitor` → Watch closely, no immediate action
- `retrain` → Model retraining recommended

---

## Logging

### Two log files are created:

#### 1. `logs/prediction_logs.csv`
**Purpose:** Audit trail of raw predictions

**Columns:**
```
request_id, timestamp, age, workclass, education.num, marital.status, 
occupation, relationship, race, sex, capital.gain, capital.loss, 
hours.per.week, native.country, prediction, probability, model_version
```

**Use case:** Track what users sent to the API

---

#### 2. `logs/engineered_features_log.csv`
**Purpose:** Drift monitoring

**Columns:**
```
request_id, timestamp, [30 engineered features], prediction, 
probability, model_version
```

**Use case:** Compare with training data to detect drift

---
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
import pickle
import pandas as pd
import os
import sys
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from deploy_preprocessing import preprocess

sys.path.append('../monitoring')
from drift_checker import check_drift

load_dotenv()

# Load model once at startup
MODEL_PATH = os.getenv('MODEL_PATH', '../models/tuned_model.pkl')
LOG_PATH = os.getenv('LOG_PATH', '../logs/prediction_logs.csv')
ENGINEERED_LOG_PATH = os.getenv('ENGINEERED_LOG_PATH', '../logs/engineered_features_log.csv')

with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

# Create logs directory
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# Initialize raw prediction log file
if not os.path.exists(LOG_PATH):
    log_headers = [
        'request_id', 'timestamp', 'age', 'workclass', 'education.num',
        'marital.status', 'occupation', 'relationship', 'race', 'sex',
        'capital.gain', 'capital.loss', 'hours.per.week', 'native.country',
        'prediction', 'probability', 'model_version'
    ]
    pd.DataFrame(columns=log_headers).to_csv(LOG_PATH, index=False)
    print(f"Created prediction log: {LOG_PATH}")

app = FastAPI(
    title="Income Prediction API",
    description="Predict income >50K or <=50K using XGBoost model"
)


# Input schema
class PredictionInput(BaseModel):
    age: int = Field(..., ge=17, le=90, description="Age of the individual")
    workclass: str = Field(..., description="Type of employment")
    education_num: int = Field(..., ge=1, le=16, description="Years of education", alias="education.num")
    marital_status: str = Field(..., description="Marital status", alias="marital.status")
    occupation: str = Field(..., description="Occupation type")
    relationship: str = Field(..., description="Relationship status")
    race: str = Field(..., description="Race")
    sex: Literal["Male", "Female"] = Field(..., description="Sex")
    capital_gain: float = Field(..., ge=0, description="Capital gains", alias="capital.gain")
    capital_loss: float = Field(..., ge=0, description="Capital losses", alias="capital.loss")
    hours_per_week: int = Field(..., ge=1, le=100, description="Hours worked per week", alias="hours.per.week")
    native_country: str = Field(..., description="Native country", alias="native.country")

    class Config:
        populate_by_name = True


# Output schema
class PredictionOutput(BaseModel):
    request_id: str
    prediction: int
    label: str
    probability: float
    model_version: str
    timestamp: str


@app.get("/")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Income Prediction API is running",
        "model_type": type(model).__name__,
        "n_features": 30,
        "target_classes": ["<=50K", ">50K"]
    }


@app.post("/predict", response_model=PredictionOutput)
def predict(input_data: PredictionInput):
    try:
        # Generate request ID and timestamp
        request_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Convert input to dict (handles aliases)
        input_dict = input_data.dict(by_alias=True)
        
        # Preprocess
        X = preprocess(input_dict)
        
        # Predict
        prediction = int(model.predict(X)[0])
        probability = float(model.predict_proba(X)[0, 1])
        
        # Label
        label = ">50K" if prediction == 1 else "<=50K"
        
        # Log 1: Raw input + prediction (for audit trail)
        log_entry = {
            'request_id': request_id,
            'timestamp': timestamp,
            **input_dict,
            'prediction': prediction,
            'probability': probability,
        }
        log_df = pd.DataFrame([log_entry])
        log_df.to_csv(LOG_PATH, mode='a', header=False, index=False)
        
        # Log 2: Engineered features (for drift monitoring)
        engineered_entry = {
            'request_id': request_id,
            'timestamp': timestamp,
            **X.iloc[0].to_dict(),  # 30 engineered features
            'prediction': prediction,
            'probability': probability,
        }
        engineered_df = pd.DataFrame([engineered_entry])
        
        # Write with header if file doesn't exist
        if not os.path.exists(ENGINEERED_LOG_PATH):
            engineered_df.to_csv(ENGINEERED_LOG_PATH, mode='w', header=True, index=False)
        else:
            engineered_df.to_csv(ENGINEERED_LOG_PATH, mode='a', header=False, index=False)
        
        # Return response
        return PredictionOutput(
            request_id=request_id,
            prediction=prediction,
            label=label,
            probability=probability,
            timestamp=timestamp
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.get("/check-drift")
def check_drift_endpoint(days: int = 7):
    try:
        # Import and call drift checker
        
        # Call with return_results=True to get dict instead of prints
        result = check_drift(days_window=days, return_results=True)
        
        if result is None:
            raise HTTPException(status_code=500, detail="Drift check returned no results")
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        # Add note about what was checked
        result["note"] = "Drift check performed on 30 engineered features that the model actually uses"
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drift check failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
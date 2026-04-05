import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

TRAIN_DATA_PATH = os.getenv('TRAIN_DATA_PATH', '../data/processed/X_train.csv')
ENGINEERED_LOG_PATH = os.getenv('ENGINEERED_LOG_PATH', '../logs/engineered_features_log.csv')
DRIFT_THRESHOLD_PSI = float(os.getenv('DRIFT_THRESHOLD_PSI', 0.2))


def calculate_psi(expected, actual, bins=10):
    """Calculate Population Stability Index (PSI) for continuous features"""
    if len(expected) == 0 or len(actual) == 0:
        return None
    
    try:
        breakpoints = np.percentile(expected, np.linspace(0, 100, bins + 1))
        breakpoints = np.unique(breakpoints)
        
        if len(breakpoints) <= 2:
            return None
            
        expected_percents = np.histogram(expected, breakpoints)[0] / len(expected)
        actual_percents = np.histogram(actual, breakpoints)[0] / len(actual)
        
        expected_percents = np.where(expected_percents == 0, 0.0001, expected_percents)
        actual_percents = np.where(actual_percents == 0, 0.0001, actual_percents)
        
        psi = np.sum((actual_percents - expected_percents) * np.log(actual_percents / expected_percents))
        return psi
    except:
        return None


def check_drift(days_window=7, return_results=False):
    # Load training data
    if not os.path.exists(TRAIN_DATA_PATH):
        if return_results:
            return {"error": f"Training data not found: {TRAIN_DATA_PATH}"}
        print(f"❌ Training data not found: {TRAIN_DATA_PATH}")
        return
    
    train_data = pd.read_csv(TRAIN_DATA_PATH)
    
    # Load engineered features log
    if not os.path.exists(ENGINEERED_LOG_PATH):
        if return_results:
            return {"error": f"Engineered features log not found: {ENGINEERED_LOG_PATH}"}
        print(f"❌ Engineered features log not found: {ENGINEERED_LOG_PATH}")
        return
    
    log_data = pd.read_csv(ENGINEERED_LOG_PATH)
    
    # Filter recent predictions
    if 'timestamp' in log_data.columns:
        log_data['timestamp'] = pd.to_datetime(log_data['timestamp'])
        cutoff_date = datetime.now() - timedelta(days=days_window)
        recent_logs = log_data[log_data['timestamp'] >= cutoff_date]
    else:
        recent_logs = log_data
    
    if len(recent_logs) < 10:
        if return_results:
            return {
                "status": "insufficient_data",
                "message": f"Only {len(recent_logs)} predictions. Need at least 10.",
                "total_predictions": len(log_data),
                "recent_predictions": len(recent_logs)
            }
        print(f"\n⚠️  Only {len(recent_logs)} predictions. Need at least 10.")
        return
    
    # Get feature columns
    exclude_cols = ['request_id', 'timestamp', 'prediction', 'probability', 'model_version']
    feature_cols = [col for col in train_data.columns if col not in exclude_cols]
    
    drift_results = []
    
    for feature in feature_cols:
        if feature not in recent_logs.columns:
            continue
        
        if train_data[feature].dtype not in ['float64', 'int64']:
            continue
            
        unique_vals = train_data[feature].nunique()
        
        # Binary features - use proportion difference
        if unique_vals <= 2:
            train_mean = train_data[feature].mean()
            recent_mean = recent_logs[feature].mean()
            diff = abs(train_mean - recent_mean)
            
            if diff < 0.05:
                status = "stable"
            elif diff < 0.1:
                status = "slight_drift"
            else:
                status = "significant_drift"
            
            drift_results.append({
                'feature': feature,
                'value': float(diff),
                'status': status,
                'metric': 'proportion_diff'
            })
            
        # Continuous features - use PSI
        else:
            psi = calculate_psi(train_data[feature].values, recent_logs[feature].values)
            
            if psi is None:
                continue
            elif psi < 0.1:
                status = "stable"
            elif psi < DRIFT_THRESHOLD_PSI:
                status = "slight_drift"
            else:
                status = "significant_drift"
            
            drift_results.append({
                'feature': feature,
                'value': float(psi),
                'status': status,
                'metric': 'psi'
            })
    
    # Calculate recommendation
    high_drift = [r for r in drift_results if 
                  (r['metric'] == 'psi' and r['value'] > DRIFT_THRESHOLD_PSI) or
                  (r['metric'] == 'proportion_diff' and r['value'] > 0.2)]
    
    if not high_drift:
        recommendation = "stable"
        message = "No significant drift. Model is stable."
    elif len(high_drift) <= 2:
        recommendation = "monitor"
        message = f"{len(high_drift)} feature(s) drifted. Monitor closely."
    else:
        recommendation = "retrain"
        message = f"{len(high_drift)} features drifted. Retrain recommended!"
    
    # Return results
    if return_results:
        return {
            "status": "success",
            "days_analyzed": days_window,
            "total_predictions": len(log_data),
            "recent_predictions": len(recent_logs),
            "features_analyzed": len(drift_results),
            "drift_results": drift_results,
            "recommendation": recommendation,
            "message": message,
            "threshold_psi": DRIFT_THRESHOLD_PSI
        }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Check drift in engineered features')
    parser.add_argument('--days', type=int, default=7)
    args = parser.parse_args()
    check_drift(days_window=args.days)
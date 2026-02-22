import pandas as pd
import numpy as np
import pickle
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Load transformers and selected features once at module import
TRANSFORMERS_PATH = os.getenv('TRANSFORMERS_PATH', '../data/processed/transformers.pkl')
FEATURES_PATH = os.getenv('FEATURES_PATH', '../data/processed/selected_features.json')

with open(TRANSFORMERS_PATH, 'rb') as f:
    transformers = pickle.load(f)

with open(FEATURES_PATH, 'r') as f:
    selected_features = json.load(f)

print(f"Loaded transformers from {TRANSFORMERS_PATH}")
print(f"Loaded {len(selected_features)} selected features")


def build_new_features(df):
    """Build same features as training (Day 2)"""
    df = df.copy()
    
    # Capital features
    df['capital_net'] = df['capital.gain'] - df['capital.loss']
    df['has_capital_activity'] = ((df['capital.gain'] > 0) | (df['capital.loss'] > 0)).astype(int)
    df['capital_gain_log'] = np.log1p(df['capital.gain'])
    
    # Age features
    df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 50, 65, 100], 
                             labels=['Young', 'Early-Career', 'Mid-Career', 'Senior', 'Retirement'])
    df['is_prime_age'] = ((df['age'] >= 35) & (df['age'] <= 55)).astype(int)
    
    # Work features
    df['hours_category'] = pd.cut(df['hours.per.week'], bins=[0, 35, 40, 50, 100], 
                                  labels=['Part-time', 'Standard', 'Overtime', 'Extreme'])
    df['is_overworker'] = (df['hours.per.week'] > 50).astype(int)
    
    # Other features
    df['has_higher_education'] = (df['education.num'] >= 13).astype(int)
    df['is_married'] = df['marital.status'].str.contains('Married').astype(int)
    df['is_us_native'] = (df['native.country'] == 'United-States').astype(int)
    
    return df


def apply_transformations(df):
    """Apply fitted transformers (fit=False mode)"""
    df = df.copy()
    
    onehot_cols = ['workclass', 'marital.status', 'occupation', 'relationship', 
                   'race', 'sex', 'age_group', 'hours_category']
    scale_cols = ['age', 'education.num', 'capital.gain', 'capital.loss', 
                  'hours.per.week', 'capital_net', 'capital_gain_log', 'native.country']
    
    # One-Hot Encoding (transform only, no fitting)
    encoded = transformers['onehot'].transform(df[onehot_cols])
    encoded_df = pd.DataFrame(encoded, 
                              columns=transformers['onehot'].get_feature_names_out(onehot_cols), 
                              index=df.index)
    df = df.drop(columns=onehot_cols)
    df = pd.concat([df, encoded_df], axis=1)
    
    # Target Encoding (transform only)
    df[['native.country']] = transformers['target'].transform(df[['native.country']])
    
    # Scaling (transform only)
    df[scale_cols] = transformers['scaler'].transform(df[scale_cols])
    
    return df


def preprocess(input_data: dict) -> pd.DataFrame:
    """
    Complete preprocessing pipeline for single prediction.
    
    Input: dict with 12 raw features from API
    Output: DataFrame with 30 selected features ready for model
    """
    # Convert to DataFrame
    df = pd.DataFrame([input_data])
    
    # Step 1: Build new features (23 features total)
    df = build_new_features(df)
    
    # Step 2: Apply transformations (60 features after one-hot)
    df = apply_transformations(df)
    
    # Step 3: Filter to selected features (30 features)
    df = df[selected_features]
    
    return df
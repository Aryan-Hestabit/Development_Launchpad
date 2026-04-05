import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from category_encoders import TargetEncoder
import pickle
import json
import os

def build_new_features(df):
    df = df.copy()
    df = df.drop(['fnlwgt', 'education'], axis=1, errors='ignore')
    
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

def encode_and_scale(df):
    df = df.copy()
    y = (df['income'] == '>50K').astype(int)
    X = df.drop('income', axis=1)
    
    onehot_cols = ['workclass', 'marital.status', 'occupation', 'relationship', 
                   'race', 'sex', 'age_group', 'hours_category']
    
    # One-Hot Encoding
    onehot = OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')
    encoded = onehot.fit_transform(X[onehot_cols])
    encoded_df = pd.DataFrame(encoded, columns=onehot.get_feature_names_out(onehot_cols), index=X.index)
    X = X.drop(columns=onehot_cols)
    X = pd.concat([X, encoded_df], axis=1)
    
    # Target Encoding
    target_encoder = TargetEncoder(cols=['native.country'])
    X[['native.country']] = target_encoder.fit_transform(X[['native.country']], y)
    
    # Scaling
    scale_cols = ['age', 'education.num', 'capital.gain', 'capital.loss', 
                  'hours.per.week', 'capital_net', 'capital_gain_log', 'native.country']
    scaler = RobustScaler()
    X[scale_cols] = scaler.fit_transform(X[scale_cols])
    
    X['income'] = y
    transformers = {'onehot': onehot, 'target': target_encoder, 'scaler': scaler}
    
    return X, transformers

# Load and process
df = pd.read_csv('../data/processed/processed_adult.csv')
print(f"Loaded: {df.shape}")

df = build_new_features(df)
print(f"Features built: {df.shape}")

df, transformers = encode_and_scale(df)
print(f"Encoded & scaled: {df.shape}")

# Save
os.makedirs('../data/processed', exist_ok=True)
df.to_csv('../data/processed/features_engineered.csv', index=False)

with open('../data/processed/transformers.pkl', 'wb') as f:
    pickle.dump(transformers, f)

feature_list = {'all_features': df.columns.tolist(), 'n_features': len(df.columns)}
with open('../data/processed/feature_list.json', 'w') as f:
    json.dump(feature_list, f, indent=4)

print("Done!")
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import mutual_info_classif
import matplotlib.pyplot as plt
import json
import os

def select_features(X_train, y_train, X_test, k=30):
    mi_scores = mutual_info_classif(X_train, y_train, random_state=42)
    scores = pd.DataFrame({
        'feature': X_train.columns,
        'score': mi_scores
    }).sort_values('score', ascending=False)

    selected = scores.head(k)['feature'].tolist()
    print(f"Selected {k}/{X_train.shape[1]} features")

    return X_train[selected], X_test[selected], selected


def save_data(X_train, X_test, y_train, y_test, selected, output_dir='../data/processed/'):
    os.makedirs(output_dir, exist_ok=True)

    X_train.to_csv(f'{output_dir}X_train.csv', index=False)
    X_test.to_csv(f'{output_dir}X_test.csv', index=False)
    y_train.to_csv(f'{output_dir}y_train.csv', index=False, header=True)
    y_test.to_csv(f'{output_dir}y_test.csv', index=False, header=True)

    with open(f'{output_dir}selected_features.json', 'w') as f:
        json.dump(selected, f, indent=4)

    print(f"Saved to {output_dir}")


if __name__ == "__main__":
    df = pd.read_csv('../data/processed/features_engineered.csv')
    X = df.drop('income', axis=1)
    y = df['income']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Train: {X_train.shape}, Test: {X_test.shape}")

    X_train, X_test, selected = select_features(X_train, y_train, X_test, k=30)

    save_data(X_train, X_test, y_train, y_test, selected)

    print("Done!")
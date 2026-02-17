import pandas as pd
import numpy as np
import shap
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

X_train = pd.read_csv('../data/processed/X_train.csv')
X_test = pd.read_csv('../data/processed/X_test.csv')
y_test = pd.read_csv('../data/processed/y_test.csv').values.ravel()

with open('../models/tuned_model.pkl', 'rb') as f:
    model = pickle.load(f)

y_pred = model.predict(X_test)

# Feature Importance
feature_imp = pd.DataFrame({
    'feature': X_train.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("Top 10 Features:")
print(feature_imp.head(10).to_string(index=False))

plt.figure(figsize=(10, 8))
top_features = feature_imp.head(20)
plt.barh(range(len(top_features)), top_features['importance'])
plt.yticks(range(len(top_features)), top_features['feature'])
plt.xlabel('Importance')
plt.title('Top 20 Feature Importances')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('../Screenshots/feature_importance.png', dpi=150)
plt.close()

# SHAP Summary
X_sample = X_test.sample(n=500, random_state=42)
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_sample)

plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values, X_sample, show=False)
plt.tight_layout()
plt.savefig('../Screenshots/shap_summary.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: shap_summary.png")

# Error Analysis
errors = y_test != y_pred
false_positives = (y_test == 0) & (y_pred == 1)
false_negatives = (y_test == 1) & (y_pred == 0)

print(f"\nFalse Positives: {false_positives.sum()}")
print(f"False Negatives: {false_negatives.sum()}")

print("Done!")
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.model_selection import cross_validate
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import json
import os
import warnings
warnings.filterwarnings('ignore')

X_train = pd.read_csv('../data/processed/X_train.csv')
X_test = pd.read_csv('../data/processed/X_test.csv')
y_train = pd.read_csv('../data/processed/y_train.csv').values.ravel()
y_test = pd.read_csv('../data/processed/y_test.csv').values.ravel()

models = {
    'Logistic Regression': LogisticRegression(C=1.0, penalty='l2', max_iter=1000, class_weight='balanced', random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1),
    'XGBoost': XGBClassifier(n_estimators=100, max_depth=6, scale_pos_weight=3.15, random_state=42, eval_metric='logloss'),
    'LightGBM': LGBMClassifier(n_estimators=100, class_weight='balanced', random_state=42, verbose=-1)
}

results = {}

for name, model in models.items():
    cv_scores = cross_validate(model, X_train, y_train,
                               scoring=['accuracy', 'precision', 'recall', 'f1', 'roc_auc'], n_jobs=-1)
    
    cv_metrics = {k: cv_scores[f'test_{k}'].mean() for k in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']}
    print(f"\nFitting {name}")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    test_metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_proba),
        'confusion_matrix': confusion_matrix(y_test, y_pred),
        'y_proba': y_proba
    }
    print(f"CV Metrics: Acc={cv_metrics['accuracy']:.3f}, Recall={cv_metrics['recall']:.3f}, Precision={cv_metrics['precision']:.3f}, F1={cv_metrics['f1']:.3f}, AUC={cv_metrics['roc_auc']:.3f}")
    print(f"Test Metrics: Acc={test_metrics['accuracy']:.3f}, Recall={test_metrics['recall']:.3f}, Precision={test_metrics['precision']:.3f}, F1={test_metrics['f1']:.3f}, AUC={test_metrics['roc_auc']:.3f}")
    results[name] = {'model': model, 'cv_metrics': cv_metrics, 'test_metrics': test_metrics}

# Best model
best_name = max(results, key=lambda x: results[x]['test_metrics']['f1'])
print(f"\nBest model: {best_name} (F1={results[best_name]['test_metrics']['f1']:.3f})")

# Save best model
os.makedirs('../models', exist_ok=True)
with open('../models/best_model.pkl', 'wb') as f:
    pickle.dump(results[best_name]['model'], f)

with open('../models/best_model_info.json', 'w') as f:
    json.dump({
        'model_name': best_name,
        'test_metrics': {k: v for k, v in results[best_name]['test_metrics'].items()
                         if k not in ['confusion_matrix', 'y_proba']}
    }, f, indent=4)

# Save all metrics
os.makedirs('../evaluation', exist_ok=True)
with open('../evaluation/metrics.json', 'w') as f:
    json.dump({
        name: {
            'cv_metrics': res['cv_metrics'],
            'test_metrics': {k: v for k, v in res['test_metrics'].items()
                             if k not in ['confusion_matrix', 'y_proba']}
        } for name, res in results.items()
    }, f, indent=4)

# Confusion matrices
for name, res in results.items():
    plt.figure(figsize=(6, 5))
    sns.heatmap(res['test_metrics']['confusion_matrix'], annot=True, fmt='d', cmap='Blues',
                xticklabels=['<=50K', '>50K'], yticklabels=['<=50K', '>50K'])
    plt.title(name)
    plt.ylabel('True')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(f'../Screenshots/confusion_matrix_{name.lower().replace(" ", "_")}.png', dpi=150)
    plt.close()

# ROC curves
plt.figure(figsize=(8, 6))
for name, res in results.items():
    fpr, tpr, _ = roc_curve(y_test, res['test_metrics']['y_proba'])
    plt.plot(fpr, tpr, label=f'{name} (AUC={res["test_metrics"]["roc_auc"]:.3f})', linewidth=2)

plt.plot([0, 1], [0, 1], 'k--', label='Random')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('../Screenshots/roc_curves.png', dpi=150)
plt.close()

print("Done!")
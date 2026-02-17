import pandas as pd
import numpy as np
import optuna
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import json

optuna.logging.set_verbosity(optuna.logging.WARNING)

X_train = pd.read_csv('../data/processed/X_train.csv')
X_test = pd.read_csv('../data/processed/X_test.csv')
y_train = pd.read_csv('../data/processed/y_train.csv').values.ravel()
y_test = pd.read_csv('../data/processed/y_test.csv').values.ravel()

with open('../models/best_model_info.json', 'r') as f:
    baseline_info = json.load(f)

baseline_test_f1 = baseline_info['test_metrics']['f1']
print(f"Baseline Model: XGBoost | F1: {baseline_test_f1:.4f}")

def objective(trial):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 500),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 7),
        'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 1.0),
        'reg_lambda': trial.suggest_float('reg_lambda', 0.5, 2.0),
    }
    model = XGBClassifier(**params)
    return cross_val_score(model, X_train, y_train, cv=5, scoring='f1', n_jobs=-1).mean()

print("Starting Optuna optimization (500 trials)...")
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=500, show_progress_bar=True)

best_params = study.best_params
best_cv_f1 = study.best_value
print(f"\nBest CV F1: {best_cv_f1:.4f}")
print(f"Best Parameters: {best_params}")

best_params.update({'scale_pos_weight': 3.15, 'random_state': 42, 'eval_metric': 'logloss'})
tuned_model = XGBClassifier(**best_params)
tuned_model.fit(X_train, y_train)

y_pred = tuned_model.predict(X_test)
y_proba = tuned_model.predict_proba(X_test)[:, 1]

test_metrics = {
    'accuracy': accuracy_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred),
    'recall': recall_score(y_test, y_pred),
    'f1': f1_score(y_test, y_pred),
    'roc_auc': roc_auc_score(y_test, y_proba)
}

print(f"\nTuned Model Performance:")
print(f"  Accuracy:  {test_metrics['accuracy']:.4f}")
print(f"  Precision: {test_metrics['precision']:.4f}")
print(f"  Recall:    {test_metrics['recall']:.4f}")
print(f"  F1-Score:  {test_metrics['f1']:.4f}")
print(f"  ROC-AUC:   {test_metrics['roc_auc']:.4f}")

print(f"\nComparison with Baseline:")
print(f"  Baseline F1: {baseline_test_f1:.4f}")
print(f"  Tuned F1:    {test_metrics['f1']:.4f}")
print(f"  Improvement: {test_metrics['f1'] - baseline_test_f1:+.4f}")

if test_metrics['f1'] > baseline_test_f1:
    print("Tuned model is BETTER - saving tuned model")
    final_model = tuned_model
else:
    print("Tuned model is NOT better - saving baseline model")
    with open('../models/best_model.pkl', 'rb') as f:
        final_model = pickle.load(f)

with open('../models/tuned_model.pkl', 'wb') as f:
    pickle.dump(final_model, f)

results = {
    'model_name': 'XGBoost',
    'method': 'Optuna',
    'baseline_test_metrics': {k: float(v) for k, v in baseline_info['test_metrics'].items()},
    'tuned_cv_f1': float(best_cv_f1),
    'tuned_test_metrics': {k: float(v) for k, v in test_metrics.items()},
    'improvement': float(test_metrics['f1'] - baseline_test_f1),
    'best_params': {k: int(v) if isinstance(v, np.integer) else float(v) if isinstance(v, np.floating) else v
                    for k, v in best_params.items()},
    'n_trials': len(study.trials),
    'cv_folds': 5,
    'final_model_used': 'tuned' if test_metrics['f1'] > baseline_test_f1 else 'baseline'
}

with open('../tuning/results.json', 'w') as f:
    json.dump(results, f, indent=4)

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['<=50K', '>50K'], yticklabels=['<=50K', '>50K'])
plt.title('Confusion Matrix - Tuned Model')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.savefig('../evaluation/confusion_matrix_tuned.png', dpi=150)
plt.close()

print("\nDone!")
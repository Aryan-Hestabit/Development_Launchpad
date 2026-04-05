# Model Comparison Report - Day 3

## Summary

**Best Model:** LightGBM
**Best F1-Score:** 0.6965

## Models Trained

1. Logistic Regression (with L2 regularization)
2. Random Forest
3. XGBoost
4. LightGBM

All models use **class_weight='balanced'** (or equivalent) to handle 76:24 class imbalance.

## Cross-Validation Results (5-Fold)

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|-------|----------|-----------|--------|----------|---------|
| Logistic Regression | 0.8052 | 0.5626 | 0.8599 | 0.6799 | 0.9078 |
| Random Forest | 0.8360 | 0.6554 | 0.6729 | 0.6639 | 0.8921 |
| XGBoost | 0.8294 | 0.6019 | 0.8617 | 0.7087 | 0.9233 |
| LightGBM | 0.8283 | 0.5991 | 0.8671 | 0.7085 | 0.9254 |

## Test Set Results

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|-------|----------|-----------|--------|----------|---------|
| Logistic Regression | 0.8012 | 0.5567 | 0.8583 | 0.6754 | 0.9073 |
| Random Forest | 0.8280 | 0.6321 | 0.6842 | 0.6571 | 0.8882 |
| XGBoost | 0.8221 | 0.5905 | 0.8525 | 0.6977 | 0.9190 |
| LightGBM  | 0.8204 | 0.5866 | 0.8603 | 0.6976 | 0.9216 |

XGBoost = Best Model

## Confusion Matrices

### Logistic Regression

```
True Negative:   3909  |  False Positive:  1036
False Negative:   240  |  True Positive:   1328
```

### Random Forest

```
True Negative:   4470  |  False Positive:   475
False Negative:   568  |  True Positive:   1000
```

### XGBoost

```
True Negative:   4038  |  False Positive:   907
False Negative:   257  |  True Positive:   1311
```

### LightGBM

```
True Negative:   4005  |  False Positive:   940
False Negative:   228  |  True Positive:   1340
```

## Key Findings

- **Best performing model:** LightGBM
- **Class imbalance handled:** Using class weights for all models
- **Regularization:** L2 regularization applied to Logistic Regression
- **Cross-validation:** 5-fold CV used for robust evaluation
